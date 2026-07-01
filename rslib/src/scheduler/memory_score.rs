// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

//! Speedrun: an "honest" memory score.
//!
//! The point estimate is the mean FSRS predicted recall (retrievability) across
//! a topic's cards. It is always paired with an uncertainty band that widens
//! with fewer graded reviews, and governed by a give-up rule: below a minimum
//! number of graded reviews we refuse to show a score at all (`shown = false`)
//! rather than present a confident-looking guess.
//!
//! This reuses the same FSRS retrievability computation as the stats graphs and
//! the same topic classification as the interleaving scheduler, so the numbers
//! are consistent across the app.

use std::collections::HashMap;

use anki_proto::scheduler::MemoryScore;
use anki_proto::scheduler::MemoryScoreRequest;
use anki_proto::scheduler::MemoryScoreResponse;
use fsrs::FSRS;
use fsrs::FSRS5_DEFAULT_DECAY;

use crate::prelude::*;
use crate::scheduler::topics::topic_index_for_tags;
use crate::search::SortMode;

/// Default give-up thresholds (tunable via the request). No per-topic score
/// until this many graded reviews, and no overall/deck score until this many.
const DEFAULT_TOPIC_MIN_REVIEWS: u32 = 20;
const DEFAULT_DECK_MIN_REVIEWS: u32 = 100;

/// Band half-width constant: `k / sqrt(graded_reviews)`. Chosen so ~30 reviews
/// gives roughly ±9% and ~100 reviews roughly ±5%.
const BAND_K: f32 = 0.5;

#[derive(Default)]
struct Accumulator {
    recall_sum: f32,
    cards_with_state: u32,
    card_count: u32,
    graded_reviews: u32,
    last_review_secs: i64,
}

impl Accumulator {
    fn into_score(self, label: String, min_reviews: u32) -> MemoryScore {
        let estimate = if self.cards_with_state > 0 {
            self.recall_sum / self.cards_with_state as f32
        } else {
            0.0
        };
        let half_width = if self.graded_reviews > 0 {
            (BAND_K / (self.graded_reviews as f32).sqrt()).min(0.5)
        } else {
            0.5
        };
        MemoryScore {
            label,
            estimate,
            range_low: (estimate - half_width).max(0.0),
            range_high: (estimate + half_width).min(1.0),
            graded_reviews: self.graded_reviews,
            card_count: self.card_count,
            cards_with_state: self.cards_with_state,
            shown: self.graded_reviews >= min_reviews,
            last_review_secs: self.last_review_secs,
        }
    }
}

impl Collection {
    pub(crate) fn compute_memory_score(
        &mut self,
        req: MemoryScoreRequest,
    ) -> Result<MemoryScoreResponse> {
        let topic_tags = req.topic_tags;
        let topic_min = nonzero_or(req.topic_min_reviews, DEFAULT_TOPIC_MIN_REVIEWS);
        let deck_min = nonzero_or(req.deck_min_reviews, DEFAULT_DECK_MIN_REVIEWS);
        let search = req.search;

        // Count graded reviews per card from the revlog.
        let mut graded_by_card: HashMap<CardId, u32> = HashMap::new();
        for entry in self.revlog_for_srs(&search)? {
            if entry.has_rating_and_affects_scheduling() {
                *graded_by_card.entry(entry.cid).or_default() += 1;
            }
        }

        // Load the matching cards, then batch-load their notes' tags so each
        // card can be classified into a topic.
        let card_ids = self.search_cards(&search, SortMode::NoOrder)?;
        let mut cards = Vec::with_capacity(card_ids.len());
        for cid in card_ids {
            if let Some(card) = self.storage.get_card(cid)? {
                cards.push(card);
            }
        }
        let mut note_ids: Vec<NoteId> = cards.iter().map(|c| c.note_id).collect();
        note_ids.sort_unstable();
        note_ids.dedup();
        let mut topic_of_note: HashMap<NoteId, usize> = HashMap::new();
        for note in self.storage.get_note_tags_by_id_list(&note_ids)? {
            if let Some(idx) = topic_index_for_tags(&note.tags, &topic_tags) {
                topic_of_note.insert(note.id, idx);
            }
        }

        let timing = self.timing_today()?;
        let fsrs = FSRS::new(None)?;
        let mut overall = Accumulator::default();
        let mut per_topic: Vec<Accumulator> = (0..topic_tags.len())
            .map(|_| Accumulator::default())
            .collect();

        for card in &cards {
            let graded = graded_by_card.get(&card.id).copied().unwrap_or(0);
            let recall = card.memory_state.map(|state| {
                let elapsed = card.seconds_since_last_review(&timing).unwrap_or_default();
                fsrs.current_retrievability_seconds(
                    state.into(),
                    elapsed,
                    card.decay.unwrap_or(FSRS5_DEFAULT_DECAY),
                )
            });
            let last_review = card.last_review_time.map(|t| t.0).unwrap_or(0);
            let topic = topic_of_note.get(&card.note_id).copied();

            let mut targets: Vec<&mut Accumulator> = vec![&mut overall];
            if let Some(idx) = topic {
                targets.push(&mut per_topic[idx]);
            }
            for acc in targets {
                acc.card_count += 1;
                acc.graded_reviews += graded;
                acc.last_review_secs = acc.last_review_secs.max(last_review);
                if let Some(r) = recall {
                    acc.recall_sum += r;
                    acc.cards_with_state += 1;
                }
            }
        }

        Ok(MemoryScoreResponse {
            overall: Some(overall.into_score(String::new(), deck_min)),
            topics: per_topic
                .into_iter()
                .zip(topic_tags)
                .map(|(acc, tag)| acc.into_score(tag, topic_min))
                .collect(),
        })
    }
}

fn nonzero_or(value: u32, default: u32) -> u32 {
    if value == 0 {
        default
    } else {
        value
    }
}

#[cfg(test)]
mod test {
    use anki_proto::scheduler::MemoryScoreRequest;

    use crate::card::CardQueue;
    use crate::card::CardType;
    use crate::card::FsrsMemoryState;
    use crate::prelude::*;

    impl Collection {
        fn add_scored_review_card(&mut self, tag: &str) -> CardId {
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
            card.ctype = CardType::Review;
            card.queue = CardQueue::Review;
            card.due = 0;
            card.interval = 10;
            let cid = card.id;
            self.update_cards_maybe_undoable(vec![card], false).unwrap();
            cid
        }

        fn set_memory_state(&mut self, cid: CardId) {
            let mut card = self.storage.get_card(cid).unwrap().unwrap();
            card.memory_state = Some(FsrsMemoryState {
                stability: 100.0,
                difficulty: 5.0,
            });
            card.last_review_time = Some(TimestampSecs::now());
            self.storage.update_card(&card).unwrap();
        }
    }

    /// Topics are scored separately, graded reviews are counted from the
    /// revlog, the uncertainty band narrows with more reviews, and the
    /// give-up rule hides a score with too few graded reviews.
    #[test]
    fn memory_score_breakdown_band_and_give_up() {
        let mut col = Collection::new();
        let topics = vec!["mcat::a".to_string(), "mcat::b".to_string()];

        // 3 cards for topic a, 1 for topic b
        let mut a_cards = vec![];
        for _ in 0..3 {
            a_cards.push(col.add_scored_review_card("mcat::a"));
        }
        let b_card = col.add_scored_review_card("mcat::b");

        // Answer every due card once -> one graded review per card.
        loop {
            if col.get_next_card().unwrap().is_none() {
                break;
            }
            col.answer_good();
        }
        // Give each card an FSRS memory state so a recall estimate is produced.
        for cid in a_cards.iter().copied().chain(std::iter::once(b_card)) {
            col.set_memory_state(cid);
        }

        let resp = col
            .compute_memory_score(MemoryScoreRequest {
                search: "deck:Default".into(),
                topic_tags: topics,
                topic_min_reviews: 2,
                deck_min_reviews: 100,
            })
            .unwrap();

        // Overall: 4 cards, 4 graded reviews, hidden (below deck threshold 100).
        let overall = resp.overall.unwrap();
        assert_eq!(overall.card_count, 4);
        assert_eq!(overall.graded_reviews, 4);
        assert_eq!(overall.cards_with_state, 4);
        assert!(!overall.shown, "deck score hidden below give-up threshold");

        let topic_a = &resp.topics[0];
        let topic_b = &resp.topics[1];
        assert_eq!(topic_a.card_count, 3);
        assert_eq!(topic_a.graded_reviews, 3);
        assert_eq!(topic_b.card_count, 1);
        assert_eq!(topic_b.graded_reviews, 1);

        // Give-up rule: topic a meets the 2-review threshold, topic b does not.
        assert!(topic_a.shown);
        assert!(!topic_b.shown);

        // Estimate is a valid recall probability inside its band.
        assert!(topic_a.estimate > 0.0 && topic_a.estimate <= 1.0);
        assert!(topic_a.range_low <= topic_a.estimate && topic_a.estimate <= topic_a.range_high);
        assert!(topic_a.range_low >= 0.0 && topic_a.range_high <= 1.0);

        // Band narrows with more reviews: overall (4) is tighter than topic a (3).
        let a_width = topic_a.range_high - topic_a.range_low;
        let overall_width = overall.range_high - overall.range_low;
        assert!(overall_width < a_width);
    }
}
