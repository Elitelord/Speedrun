// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

mod burying;
mod gathering;
mod interleaving;
pub(crate) mod intersperser;
pub(crate) mod sized_chain;
mod sorting;

use std::collections::HashMap;
use std::collections::VecDeque;

use intersperser::Intersperser;
use sized_chain::SizedChain;

use super::BuryMode;
use super::CardQueues;
use super::Counts;
use super::LearningQueueEntry;
use super::MainQueueEntry;
use super::MainQueueEntryKind;
use crate::deckconfig::NewCardGatherPriority;
use crate::deckconfig::NewCardSortOrder;
use crate::deckconfig::ReviewCardOrder;
use crate::deckconfig::ReviewMix;
use crate::decks::limits::LimitTreeMap;
use crate::prelude::*;
use crate::scheduler::states::load_balancer::LoadBalancer;
use crate::scheduler::timing::SchedTimingToday;

/// Temporary holder for review cards that will be built into a queue.
#[derive(Debug, Clone, Copy)]
pub(crate) struct DueCard {
    pub id: CardId,
    pub note_id: NoteId,
    pub mtime: TimestampSecs,
    pub due: i32,
    pub current_deck_id: DeckId,
    pub original_deck_id: DeckId,
    pub kind: DueCardKind,
    pub reps: u32,
}

#[derive(Debug, Clone, Copy)]
pub(crate) enum DueCardKind {
    Review,
    Learning,
}

/// Temporary holder for new cards that will be built into a queue.
#[derive(Debug, Default, Clone, Copy)]
pub(crate) struct NewCard {
    pub id: CardId,
    pub note_id: NoteId,
    pub mtime: TimestampSecs,
    pub current_deck_id: DeckId,
    pub original_deck_id: DeckId,
    pub template_index: u32,
    pub hash: u64,
}

impl From<DueCard> for MainQueueEntry {
    fn from(c: DueCard) -> Self {
        MainQueueEntry {
            id: c.id,
            mtime: c.mtime,
            kind: match c.kind {
                DueCardKind::Review => MainQueueEntryKind::Review,
                DueCardKind::Learning => MainQueueEntryKind::InterdayLearning,
            },
        }
    }
}

impl From<NewCard> for MainQueueEntry {
    fn from(c: NewCard) -> Self {
        MainQueueEntry {
            id: c.id,
            mtime: c.mtime,
            kind: MainQueueEntryKind::New,
        }
    }
}

impl From<DueCard> for LearningQueueEntry {
    fn from(c: DueCard) -> Self {
        LearningQueueEntry {
            due: TimestampSecs(c.due as i64),
            id: c.id,
            mtime: c.mtime,
            reps: c.reps,
        }
    }
}

#[derive(Default, Clone, Debug)]
pub(super) struct QueueSortOptions {
    pub(super) new_order: NewCardSortOrder,
    pub(super) new_gather_priority: NewCardGatherPriority,
    pub(super) review_order: ReviewCardOrder,
    pub(super) day_learn_mix: ReviewMix,
    pub(super) new_review_mix: ReviewMix,
}

#[derive(Debug)]
pub(super) struct QueueBuilder {
    pub(super) new: Vec<NewCard>,
    pub(super) review: Vec<DueCard>,
    pub(super) learning: Vec<DueCard>,
    pub(super) day_learning: Vec<DueCard>,
    limits: LimitTreeMap,
    load_balancer: Option<LoadBalancer>,
    /// Speedrun: maps a gathered card's note to its topic index (the position
    /// of the first matching tag in `Context::topic_tags`). Notes that match no
    /// configured topic are absent. Populated by `resolve_topics()` after
    /// gathering, and consumed by the topic-interleaving reorder in `build()`.
    topic_map: HashMap<NoteId, usize>,
    /// Speedrun: per-topic emission weight for the interleaving round-robin
    /// (same order as `Context::topic_tags`). All `1.0` for uniform mixing;
    /// when weakness-weighting is on, weaker topics (lower mean FSRS recall)
    /// get larger weights. Populated by `resolve_topics()`.
    topic_weights: Vec<f32>,
    context: Context,
}

/// Data container and helper for building queues.
#[derive(Debug, Clone)]
struct Context {
    timing: SchedTimingToday,
    config_map: HashMap<DeckConfigId, DeckConfig>,
    root_deck: Deck,
    sort_options: QueueSortOptions,
    seen_note_ids: HashMap<NoteId, BuryMode>,
    deck_map: HashMap<DeckId, Deck>,
    fsrs: bool,
    /// Speedrun: whether topic-aware interleaving is enabled for this build.
    interleave_topics: bool,
    /// Speedrun: ordered topic tags to interleave across (round-robin follows
    /// this order). Empty disables interleaving regardless of the flag above.
    topic_tags: Vec<String>,
    /// Speedrun: when true, weight the interleaving round-robin by measured
    /// weakness (lower mean FSRS recall -> more frequent emission).
    weight_by_weakness: bool,
}

impl QueueBuilder {
    pub(super) fn new(col: &mut Collection, deck_id: DeckId) -> Result<Self> {
        let timing = col.timing_for_timestamp(TimestampSecs::now())?;
        let new_cards_ignore_review_limit = col.get_config_bool(BoolKey::NewCardsIgnoreReviewLimit);
        let apply_all_parent_limits = col.get_config_bool(BoolKey::ApplyAllParentLimits);
        let config_map = col.storage.get_deck_config_map()?;
        let root_deck = col.storage.get_deck(deck_id)?.or_not_found(deck_id)?;
        let mut decks = col.storage.child_decks(&root_deck)?;
        decks.insert(0, root_deck.clone());
        if apply_all_parent_limits {
            for parent in col.storage.parent_decks(&root_deck)? {
                decks.insert(0, parent);
            }
        }
        let limits = LimitTreeMap::build(
            &decks,
            &config_map,
            timing.days_elapsed,
            new_cards_ignore_review_limit,
        );
        let sort_options = sort_options(&root_deck, &config_map);
        let deck_map = col.storage.get_decks_map()?;

        let load_balancer = col
            .get_config_bool(BoolKey::LoadBalancerEnabled)
            .then(|| {
                let did_to_dcid = deck_map
                    .values()
                    .filter_map(|deck| Some((deck.id, deck.config_id()?)))
                    .collect::<HashMap<_, _>>();
                LoadBalancer::new(
                    timing.days_elapsed,
                    did_to_dcid,
                    col.timing_today()?.next_day_at,
                    &col.storage,
                )
            })
            .transpose()?;

        Ok(QueueBuilder {
            new: Vec::new(),
            review: Vec::new(),
            learning: Vec::new(),
            day_learning: Vec::new(),
            limits,
            load_balancer,
            topic_map: HashMap::new(),
            topic_weights: Vec::new(),
            context: Context {
                timing,
                config_map,
                root_deck,
                sort_options,
                seen_note_ids: HashMap::new(),
                deck_map,
                fsrs: col.get_config_bool(BoolKey::Fsrs),
                interleave_topics: col.get_config_bool(BoolKey::InterleaveTopics),
                topic_tags: col.get_interleave_topic_tags(),
                weight_by_weakness: col.get_config_bool(BoolKey::InterleaveWeightByWeakness),
            },
        })
    }

    pub(super) fn build(mut self, learn_ahead_secs: i64) -> CardQueues {
        self.sort_new();

        // Speedrun: mix due/new cards across MCAT topics. This only reorders the
        // already-gathered, already-sorted cards (never touching due dates,
        // intervals, or memory state), so FSRS scheduling stays valid. Runs after
        // sort_new() so a topic's internal order matches the configured new-card
        // sort.
        self.interleave_by_topic();

        // intraday learning and total learn count
        let intraday_learning = sort_learning(self.learning);
        let now = TimestampSecs::now();
        let cutoff = now.adding_secs(learn_ahead_secs);
        let learn_count =
            intraday_learning.iter().filter(|e| e.due <= cutoff).count() + self.day_learning.len();
        let review_count = self.review.len();
        let new_count = self.new.len();

        // merge interday and new cards into main
        let with_interday_learn = merge_day_learning(
            self.review,
            self.day_learning,
            self.context.sort_options.day_learn_mix,
        );
        let main_iter = merge_new(
            with_interday_learn,
            self.new,
            self.context.sort_options.new_review_mix,
        );

        CardQueues {
            counts: Counts {
                new: new_count,
                review: review_count,
                learning: learn_count,
            },
            main: main_iter.collect(),
            intraday_learning,
            learn_ahead_secs,
            current_day: self.context.timing.days_elapsed,
            build_time: TimestampMillis::now(),
            load_balancer: self.load_balancer,
            current_learning_cutoff: now,
        }
    }
}

fn sort_options(deck: &Deck, config_map: &HashMap<DeckConfigId, DeckConfig>) -> QueueSortOptions {
    deck.config_id()
        .and_then(|config_id| config_map.get(&config_id))
        .map(|config| QueueSortOptions {
            new_order: config.inner.new_card_sort_order(),
            new_gather_priority: config.inner.new_card_gather_priority(),
            review_order: config.inner.review_order(),
            day_learn_mix: config.inner.interday_learning_mix(),
            new_review_mix: config.inner.new_mix(),
        })
        .unwrap_or_else(|| {
            // filtered decks do not space siblings
            QueueSortOptions {
                new_order: NewCardSortOrder::NoSort,
                ..Default::default()
            }
        })
}

fn merge_day_learning(
    reviews: Vec<DueCard>,
    day_learning: Vec<DueCard>,
    mode: ReviewMix,
) -> Box<dyn ExactSizeIterator<Item = MainQueueEntry>> {
    let day_learning_iter = day_learning.into_iter().map(Into::into);
    let reviews_iter = reviews.into_iter().map(Into::into);

    match mode {
        ReviewMix::AfterReviews => Box::new(SizedChain::new(reviews_iter, day_learning_iter)),
        ReviewMix::BeforeReviews => Box::new(SizedChain::new(day_learning_iter, reviews_iter)),
        ReviewMix::MixWithReviews => Box::new(Intersperser::new(reviews_iter, day_learning_iter)),
    }
}

fn merge_new(
    review_iter: impl ExactSizeIterator<Item = MainQueueEntry> + 'static,
    new: Vec<NewCard>,
    mode: ReviewMix,
) -> Box<dyn ExactSizeIterator<Item = MainQueueEntry>> {
    let new_iter = new.into_iter().map(Into::into);

    match mode {
        ReviewMix::BeforeReviews => Box::new(SizedChain::new(new_iter, review_iter)),
        ReviewMix::AfterReviews => Box::new(SizedChain::new(review_iter, new_iter)),
        ReviewMix::MixWithReviews => Box::new(Intersperser::new(review_iter, new_iter)),
    }
}

fn sort_learning(learning: Vec<DueCard>) -> VecDeque<LearningQueueEntry> {
    let mut entries: Vec<LearningQueueEntry> =
        learning.into_iter().map(LearningQueueEntry::from).collect();
    entries.sort_by(|a, b| a.cmp_by_reps_then_due(b));
    entries.into_iter().collect()
}

impl Collection {
    pub(crate) fn build_queues(&mut self, deck_id: DeckId) -> Result<CardQueues> {
        let mut queues = QueueBuilder::new(self, deck_id)?;
        self.storage
            .update_active_decks(&queues.context.root_deck)?;

        queues.gather_cards(self)?;
        // Speedrun: resolve each gathered card's topic while the collection is
        // available; the reorder itself happens later in build().
        queues.resolve_topics(self)?;

        let queues = queues.build(self.learn_ahead_secs() as i64);

        Ok(queues)
    }
}

#[cfg(test)]
mod test {
    use std::collections::HashMap;
    use std::collections::HashSet;

    use anki_proto::deck_config::deck_config::config::NewCardGatherPriority;
    use anki_proto::deck_config::deck_config::config::NewCardSortOrder;

    use super::*;
    use crate::card::CardQueue;
    use crate::card::CardType;

    impl Collection {
        fn set_deck_gather_order(&mut self, deck: &mut Deck, order: NewCardGatherPriority) {
            let mut conf = DeckConfig::default();
            conf.inner.new_card_gather_priority = order as i32;
            conf.inner.new_card_sort_order = NewCardSortOrder::NoSort as i32;
            self.add_or_update_deck_config(&mut conf).unwrap();
            deck.normal_mut().unwrap().config_id = conf.id.0;
            self.add_or_update_deck(deck).unwrap();
        }

        fn set_deck_new_limit(&mut self, deck: &mut Deck, new_limit: u32) {
            let mut conf = DeckConfig::default();
            conf.inner.new_per_day = new_limit;
            self.add_or_update_deck_config(&mut conf).unwrap();
            deck.normal_mut().unwrap().config_id = conf.id.0;
            self.add_or_update_deck(deck).unwrap();
        }

        fn set_deck_review_limit(&mut self, deck: DeckId, limit: u32) {
            let dcid = self.get_deck(deck).unwrap().unwrap().config_id().unwrap();
            let mut conf = self.get_deck_config(dcid, false).unwrap().unwrap();
            conf.inner.reviews_per_day = limit;
            self.add_or_update_deck_config(&mut conf).unwrap();
        }

        fn queue_as_deck_and_template(&mut self, deck_id: DeckId) -> Vec<(DeckId, u16)> {
            self.build_queues(deck_id)
                .unwrap()
                .iter()
                .map(|entry| {
                    let card = self.storage.get_card(entry.card_id()).unwrap().unwrap();
                    (card.deck_id, card.template_idx)
                })
                .collect()
        }

        fn set_deck_review_order(&mut self, deck: &mut Deck, order: ReviewCardOrder) {
            let mut conf = DeckConfig::default();
            conf.inner.review_order = order as i32;
            self.add_or_update_deck_config(&mut conf).unwrap();
            deck.normal_mut().unwrap().config_id = conf.id.0;
            self.add_or_update_deck(deck).unwrap();
        }

        fn queue_as_due_and_ivl(&mut self, deck_id: DeckId) -> Vec<(i32, u32)> {
            self.build_queues(deck_id)
                .unwrap()
                .iter()
                .map(|entry| {
                    let card = self.storage.get_card(entry.card_id()).unwrap().unwrap();
                    (card.due, card.interval)
                })
                .collect()
        }
    }

    #[test]
    fn should_build_empty_queue_if_limit_is_reached() {
        let mut col = Collection::new();
        CardAdder::new().due_dates(["0"]).add(&mut col);
        col.set_deck_review_limit(DeckId(1), 0);
        assert_eq!(col.queue_as_deck_and_template(DeckId(1)), vec![]);
    }

    #[test]
    fn new_queue_building() -> Result<()> {
        let mut col = Collection::new();

        // parent
        // ┣━━child━━grandchild
        // ┗━━child_2
        let mut parent = DeckAdder::new("parent").add(&mut col);
        let mut child = DeckAdder::new("parent::child").add(&mut col);
        let child_2 = DeckAdder::new("parent::child_2").add(&mut col);
        let grandchild = DeckAdder::new("parent::child::grandchild").add(&mut col);

        // add 2 new cards to each deck
        for deck in [&parent, &child, &child_2, &grandchild] {
            CardAdder::new().siblings(2).deck(deck.id).add(&mut col);
        }

        // set child's new limit to 3, which should affect grandchild
        col.set_deck_new_limit(&mut child, 3);

        // depth-first tree order
        col.set_deck_gather_order(&mut parent, NewCardGatherPriority::Deck);
        let cards = vec![
            (parent.id, 0),
            (parent.id, 1),
            (child.id, 0),
            (child.id, 1),
            (grandchild.id, 0),
            (child_2.id, 0),
            (child_2.id, 1),
        ];
        assert_eq!(col.queue_as_deck_and_template(parent.id), cards);

        // insertion order
        col.set_deck_gather_order(&mut parent, NewCardGatherPriority::LowestPosition);
        let cards = vec![
            (parent.id, 0),
            (parent.id, 1),
            (child.id, 0),
            (child.id, 1),
            (child_2.id, 0),
            (child_2.id, 1),
            (grandchild.id, 0),
        ];
        assert_eq!(col.queue_as_deck_and_template(parent.id), cards);

        // inverted insertion order, but sibling order is preserved
        col.set_deck_gather_order(&mut parent, NewCardGatherPriority::HighestPosition);
        let cards = vec![
            (grandchild.id, 0),
            (grandchild.id, 1),
            (child_2.id, 0),
            (child_2.id, 1),
            (child.id, 0),
            (parent.id, 0),
            (parent.id, 1),
        ];
        assert_eq!(col.queue_as_deck_and_template(parent.id), cards);

        Ok(())
    }

    #[test]
    fn review_queue_building() -> Result<()> {
        let mut col = Collection::new();

        let mut deck = col.get_or_create_normal_deck("Default").unwrap();
        let nt = col.get_notetype_by_name("Basic")?.unwrap();
        let mut cards = vec![];

        // relative overdueness
        let expected_queue = vec![
            (-150, 1),
            (-100, 1),
            (-50, 1),
            (-150, 5),
            (-100, 5),
            (-50, 5),
            (-150, 20),
            (-150, 20),
            (-100, 20),
            (-50, 20),
            (-150, 100),
            (-100, 100),
            (-50, 100),
            (0, 1),
            (0, 5),
            (0, 20),
            (0, 100),
        ];
        for t in expected_queue.iter() {
            let mut note = nt.new_note();
            note.set_field(0, "foo")?;
            note.id.0 = 0;
            col.add_note(&mut note, deck.id)?;
            let mut card = col.storage.get_card_by_ordinal(note.id, 0)?.unwrap();
            card.interval = t.1;
            card.due = t.0;
            card.ctype = CardType::Review;
            card.queue = CardQueue::Review;
            cards.push(card);
        }
        col.update_cards_maybe_undoable(cards, false)?;
        col.set_deck_review_order(&mut deck, ReviewCardOrder::RelativeOverdueness);
        assert_eq!(col.queue_as_due_and_ivl(deck.id), expected_queue);

        Ok(())
    }

    impl Collection {
        fn card_queue_len(&mut self) -> usize {
            self.get_queued_cards(5, false).unwrap().cards.len()
        }
    }

    #[test]
    fn new_card_potentially_burying_review_card() {
        let mut col = Collection::new();
        // add one new and one review card
        CardAdder::new().siblings(2).due_dates(["0"]).add(&mut col);
        // Potentially problematic config: New cards are shown first and would bury
        // review siblings. This poses a problem because we gather review cards first.
        col.update_default_deck_config(|config| {
            config.new_mix = ReviewMix::BeforeReviews as i32;
            config.bury_new = false;
            config.bury_reviews = true;
        });

        let old_queue_len = col.card_queue_len();
        col.answer_easy();
        col.clear_study_queues();

        // The number of cards in the queue must decrease by exactly 1, either because
        // no burying was performed, or the first built queue anticipated it and didn't
        // include the buried card.
        assert_eq!(col.card_queue_len(), old_queue_len - 1);
    }

    #[test]
    fn new_cards_may_ignore_review_limit() {
        let mut col = Collection::new();
        col.set_config_bool(BoolKey::NewCardsIgnoreReviewLimit, true, false)
            .unwrap();
        col.update_default_deck_config(|config| {
            config.reviews_per_day = 0;
        });
        CardAdder::new().add(&mut col);

        // review limit doesn't apply to new card
        assert_eq!(col.card_queue_len(), 1);
    }

    #[test]
    fn reviews_dont_affect_new_limit_before_review_limit_is_reached() {
        let mut col = Collection::new();
        col.update_default_deck_config(|config| {
            config.new_per_day = 1;
        });
        CardAdder::new().siblings(2).due_dates(["0"]).add(&mut col);
        assert_eq!(col.card_queue_len(), 2);
    }

    #[test]
    fn may_apply_parent_limits() {
        let mut col = Collection::new();
        col.set_config_bool(BoolKey::ApplyAllParentLimits, true, false)
            .unwrap();
        col.update_default_deck_config(|config| {
            config.new_per_day = 0;
        });
        let child = DeckAdder::new("Default::child")
            .with_config(|_| ())
            .add(&mut col);
        CardAdder::new().deck(child.id).add(&mut col);
        col.set_current_deck(child.id).unwrap();
        assert_eq!(col.card_queue_len(), 0);
    }

    // Speedrun: topic-aware interleaving tests.

    const TOPIC_TAGS: [&str; 3] = ["mcat::a", "mcat::b", "mcat::c"];

    impl Collection {
        /// Add a due review card on the default deck, tagged with `tag`, with
        /// the given interval/due. Returns its card id.
        fn add_tagged_review_card(&mut self, tag: &str, interval: u32, due: i32) -> CardId {
            let nt = self.get_notetype_by_name("Basic").unwrap().unwrap();
            let mut note = nt.new_note();
            note.set_field(0, "q").unwrap();
            note.tags = vec![tag.to_string()];
            self.add_note(&mut note, DeckId(1)).unwrap();
            let mut card = self
                .storage
                .get_card_by_ordinal(note.id, 0)
                .unwrap()
                .unwrap();
            card.interval = interval;
            card.due = due;
            card.ctype = CardType::Review;
            card.queue = CardQueue::Review;
            let cid = card.id;
            self.update_cards_maybe_undoable(vec![card], false).unwrap();
            cid
        }

        fn enable_interleaving(&mut self) {
            self.set_config_bool(BoolKey::InterleaveTopics, true, false)
                .unwrap();
            self.set_interleave_topic_tags(
                &TOPIC_TAGS.iter().map(|t| t.to_string()).collect::<Vec<_>>(),
            )
            .unwrap();
        }

        /// Give a card an FSRS memory state and a last-review time `days_ago`,
        /// so `compute_topic_weights` produces a real retrievability for it.
        fn set_memory(&mut self, cid: CardId, stability: f32, days_ago: i64) {
            use crate::card::FsrsMemoryState;
            let mut card = self.storage.get_card(cid).unwrap().unwrap();
            card.memory_state = Some(FsrsMemoryState {
                stability,
                difficulty: 5.0,
            });
            card.decay = Some(fsrs::FSRS5_DEFAULT_DECAY);
            card.last_review_time = Some(TimestampSecs::now().adding_secs(-days_ago * 86_400));
            self.storage.update_card(&card).unwrap();
        }

        fn queue_card_ids(&mut self, deck_id: DeckId) -> Vec<CardId> {
            self.build_queues(deck_id)
                .unwrap()
                .iter()
                .map(|entry| entry.card_id())
                .collect()
        }
    }

    /// The queue should round-robin across the configured topics, regardless of
    /// the order the cards were gathered in.
    #[test]
    fn interleaving_round_robins_topics() {
        let mut col = Collection::new();
        // Pin review order to insertion order (card-id ascending) so the
        // un-interleaved order is deterministically topic-blocked.
        let mut deck = col.get_or_create_normal_deck("Default").unwrap();
        col.set_deck_review_order(&mut deck, ReviewCardOrder::Added);
        col.enable_interleaving();

        // 3 cards per topic, added grouped by topic, so a passing round-robin
        // assertion can't be an accident of insertion order.
        let mut topic_of: HashMap<CardId, usize> = HashMap::new();
        for (idx, tag) in TOPIC_TAGS.iter().enumerate() {
            for _ in 0..3 {
                let cid = col.add_tagged_review_card(tag, 10, 0);
                topic_of.insert(cid, idx);
            }
        }

        let topics: Vec<usize> = col
            .queue_card_ids(DeckId(1))
            .iter()
            .map(|cid| topic_of[cid])
            .collect();
        assert_eq!(topics, vec![0, 1, 2, 0, 1, 2, 0, 1, 2]);

        // Disabling the toggle restores topic-blocked order.
        col.set_config_bool(BoolKey::InterleaveTopics, false, false)
            .unwrap();
        let topics: Vec<usize> = col
            .queue_card_ids(DeckId(1))
            .iter()
            .map(|cid| topic_of[cid])
            .collect();
        assert_eq!(topics, vec![0, 0, 0, 1, 1, 1, 2, 2, 2]);
    }

    /// Interleaving only reorders: it must not change any card's due date or
    /// interval, and must gather the same set of cards as a non-interleaved
    /// build.
    #[test]
    fn interleaving_preserves_fsrs_scheduling() {
        let mut col = Collection::new();

        // distinct (interval, due) per card so a mutation would be visible
        let mut expected: HashMap<CardId, (i32, u32)> = HashMap::new();
        for (i, tag) in TOPIC_TAGS.iter().enumerate() {
            for j in 0..3u32 {
                let interval = 10 + (i as u32) * 3 + j;
                let due = 0; // all due today
                let cid = col.add_tagged_review_card(tag, interval, due);
                expected.insert(cid, (due, interval));
            }
        }

        let plain: HashSet<CardId> = col.queue_card_ids(DeckId(1)).into_iter().collect();
        col.enable_interleaving();
        let interleaved: HashSet<CardId> = col.queue_card_ids(DeckId(1)).into_iter().collect();

        // same cards gathered either way
        assert_eq!(interleaved, plain);
        // due/interval untouched by the reorder
        for (cid, (due, interval)) in expected {
            let card = col.storage.get_card(cid).unwrap().unwrap();
            assert_eq!((card.due, card.interval), (due, interval));
        }
    }

    /// With weakness weighting on, the topic with lower measured FSRS recall
    /// gets more of the early slots; uniform weighting alternates evenly.
    #[test]
    fn weakness_weighting_front_loads_the_weak_topic() {
        let mut col = Collection::new();
        let mut deck = col.get_or_create_normal_deck("Default").unwrap();
        col.set_deck_review_order(&mut deck, ReviewCardOrder::Added);
        col.enable_interleaving();

        // Topic a (index 0): low stability, long since review -> weak (low
        // recall). Topic b (index 1): high stability, just reviewed -> strong.
        let mut topic_of: HashMap<CardId, usize> = HashMap::new();
        for _ in 0..3 {
            let cid = col.add_tagged_review_card(TOPIC_TAGS[0], 10, 0);
            col.set_memory(cid, 1.0, 30);
            topic_of.insert(cid, 0);
        }
        for _ in 0..3 {
            let cid = col.add_tagged_review_card(TOPIC_TAGS[1], 10, 0);
            col.set_memory(cid, 500.0, 0);
            topic_of.insert(cid, 1);
        }

        // Uniform interleaving: strict alternation a,b,a,b,a,b.
        let uniform: Vec<usize> = col
            .queue_card_ids(DeckId(1))
            .iter()
            .map(|cid| topic_of[cid])
            .collect();
        assert_eq!(uniform, vec![0, 1, 0, 1, 0, 1]);

        // Turn on weakness weighting: the weak topic (0) is front-loaded, so its
        // three cards all land in the first four slots.
        col.set_config_bool(BoolKey::InterleaveWeightByWeakness, true, false)
            .unwrap();
        let weighted: Vec<usize> = col
            .queue_card_ids(DeckId(1))
            .iter()
            .map(|cid| topic_of[cid])
            .collect();
        let weak_positions: Vec<usize> = weighted
            .iter()
            .enumerate()
            .filter(|(_, &t)| t == 0)
            .map(|(i, _)| i)
            .collect();
        assert!(
            weak_positions.iter().all(|&p| p < 4),
            "weak topic should be front-loaded, got order {weighted:?}"
        );
        assert_ne!(
            weighted, uniform,
            "weighted order must differ from uniform alternation"
        );
    }

    /// Answering a card from an interleaved queue must remain fully undoable.
    #[test]
    fn interleaving_keeps_undo_intact() {
        let mut col = Collection::new();
        col.enable_interleaving();
        for tag in TOPIC_TAGS.iter() {
            col.add_tagged_review_card(tag, 10, 0);
        }

        col.clear_study_queues();
        let cid = col.get_next_card().unwrap().unwrap().card.id;
        let before = col.storage.get_card(cid).unwrap().unwrap();

        col.answer_good();
        let after = col.storage.get_card(cid).unwrap().unwrap();
        assert_ne!(after.reps, before.reps, "answering should change the card");

        col.undo().unwrap();
        let restored = col.storage.get_card(cid).unwrap().unwrap();
        assert_eq!(restored.reps, before.reps);
        assert_eq!(restored.due, before.due);
        assert_eq!(restored.interval, before.interval);
        assert_eq!(restored.ctype, before.ctype);
    }
}
