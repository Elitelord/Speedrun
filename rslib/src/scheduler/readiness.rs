// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

//! Speedrun: the two "beyond memory" honest scores — Performance and Readiness.
//!
//! These sit alongside the memory score ([`super::memory_score`]) so the app can
//! show three separate, honestly-uncertain numbers rather than one blended one.
//!
//! * **Performance** predicts accuracy on held-out, exam-style questions. Recall
//!   of a flashcard overstates the odds of answering a reworded exam item, so we
//!   discount FSRS retrievability by the card's FSRS *difficulty*: a hard item at
//!   the same retrievability contributes a lower performance estimate. Same band
//!   + give-up machinery as the memory score.
//! * **Readiness** maps overall mastery onto the real MCAT scale (total 472–528,
//!   per section 118–132), and reports a range, the **% of topics covered**, and
//!   a stricter give-up rule (no projected score until there are enough graded
//!   reviews *and* at least half the topics have data). We do not have
//!   longitudinal practice-test data to calibrate the mapping, so it is a
//!   deliberately simple affine map, always shown with its range and coverage.
//!
//! Both reuse the same FSRS retrievability call and topic classifier as the
//! memory score, via the shared [`Collection::gather_card_facts`] gather, so the
//! three numbers stay consistent.

use std::collections::HashMap;

use anki_proto::scheduler::MemoryScore;
use anki_proto::scheduler::MemoryScoreRequest;
use anki_proto::scheduler::MemoryScoreResponse;
use anki_proto::scheduler::ReadinessScore;
use anki_proto::scheduler::ReadinessScoreResponse;
use fsrs::FSRS;
use fsrs::FSRS5_DEFAULT_DECAY;

use crate::prelude::*;
use crate::scheduler::topics::topic_index_for_tags;
use crate::search::SortMode;

/// Give-up thresholds shared with the memory score (tunable via the request).
const DEFAULT_TOPIC_MIN_REVIEWS: u32 = 20;
const DEFAULT_DECK_MIN_REVIEWS: u32 = 100;
/// Readiness is a stronger claim, so it needs more evidence before we show it.
const READINESS_MIN_REVIEWS: u32 = 200;
const READINESS_MIN_COVERAGE: f32 = 0.5;

/// Band half-width constant: `k / sqrt(graded_reviews)` (matches memory score).
const BAND_K: f32 = 0.5;

/// How strongly FSRS difficulty (1..10) discounts retrievability when turning it
/// into a performance estimate. At the maximum difficulty a card contributes
/// `1 - PERF_DIFFICULTY_WEIGHT` of its retrievability.
const PERF_DIFFICULTY_WEIGHT: f32 = 0.4;

/// MCAT scale endpoints.
const TOTAL_MIN: f32 = 472.0;
const TOTAL_SPAN: f32 = 56.0; // 528 - 472
const SECTION_MIN: f32 = 118.0;
const SECTION_SPAN: f32 = 14.0; // 132 - 118

/// Per-card facts needed by every score, gathered once.
struct CardFacts {
    topic: Option<usize>,
    retrievability: Option<f32>,
    difficulty: Option<f32>,
    graded: u32,
    last_review: i64,
}

#[derive(Default)]
struct Accumulator {
    value_sum: f32,
    cards_with_value: u32,
    card_count: u32,
    graded_reviews: u32,
    last_review_secs: i64,
}

impl Accumulator {
    fn add(&mut self, value: Option<f32>, graded: u32, last_review: i64) {
        self.card_count += 1;
        self.graded_reviews += graded;
        self.last_review_secs = self.last_review_secs.max(last_review);
        if let Some(v) = value {
            self.value_sum += v;
            self.cards_with_value += 1;
        }
    }

    fn into_score(self, label: String, min_reviews: u32) -> MemoryScore {
        let estimate = if self.cards_with_value > 0 {
            self.value_sum / self.cards_with_value as f32
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
            cards_with_state: self.cards_with_value,
            shown: self.graded_reviews >= min_reviews,
            last_review_secs: self.last_review_secs,
        }
    }
}

/// Retrievability discounted by FSRS difficulty -> a performance estimate.
fn performance_value(facts: &CardFacts) -> Option<f32> {
    let r = facts.retrievability?;
    let d = facts.difficulty.unwrap_or(5.0);
    let discount = 1.0 - PERF_DIFFICULTY_WEIGHT * ((d - 1.0) / 9.0).clamp(0.0, 1.0);
    Some(r * discount)
}

fn scale_total(v: f32) -> f32 {
    TOTAL_MIN + v.clamp(0.0, 1.0) * TOTAL_SPAN
}

fn scale_section(v: f32) -> f32 {
    SECTION_MIN + v.clamp(0.0, 1.0) * SECTION_SPAN
}

fn nonzero_or(value: u32, default: u32) -> u32 {
    if value == 0 {
        default
    } else {
        value
    }
}

impl Collection {
    /// Gather the per-card facts (topic, retrievability, difficulty, graded
    /// review count, last review time) shared by the performance and readiness
    /// scores. Mirrors the load path in [`super::memory_score`].
    fn gather_card_facts(
        &mut self,
        search: &str,
        topic_tags: &[String],
    ) -> Result<Vec<CardFacts>> {
        let mut graded_by_card: HashMap<CardId, u32> = HashMap::new();
        for entry in self.revlog_for_srs(search)? {
            if entry.has_rating_and_affects_scheduling() {
                *graded_by_card.entry(entry.cid).or_default() += 1;
            }
        }

        let card_ids = self.search_cards(search, SortMode::NoOrder)?;
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
            if let Some(idx) = topic_index_for_tags(&note.tags, topic_tags) {
                topic_of_note.insert(note.id, idx);
            }
        }

        let timing = self.timing_today()?;
        let fsrs = FSRS::new(None)?;
        let mut facts = Vec::with_capacity(cards.len());
        for card in &cards {
            let difficulty = card.memory_state.map(|s| s.difficulty);
            let retrievability = card.memory_state.map(|state| {
                let elapsed = card.seconds_since_last_review(&timing).unwrap_or_default();
                fsrs.current_retrievability_seconds(
                    state.into(),
                    elapsed,
                    card.decay.unwrap_or(FSRS5_DEFAULT_DECAY),
                )
            });
            facts.push(CardFacts {
                topic: topic_of_note.get(&card.note_id).copied(),
                retrievability,
                difficulty,
                graded: graded_by_card.get(&card.id).copied().unwrap_or(0),
                last_review: card.last_review_time.map(|t| t.0).unwrap_or(0),
            });
        }
        Ok(facts)
    }

    fn accumulate_performance(
        &mut self,
        req: &MemoryScoreRequest,
    ) -> Result<(Accumulator, Vec<Accumulator>)> {
        let facts = self.gather_card_facts(&req.search, &req.topic_tags)?;
        let mut overall = Accumulator::default();
        let mut per_topic: Vec<Accumulator> = (0..req.topic_tags.len())
            .map(|_| Accumulator::default())
            .collect();
        for f in &facts {
            let v = performance_value(f);
            overall.add(v, f.graded, f.last_review);
            if let Some(idx) = f.topic {
                per_topic[idx].add(v, f.graded, f.last_review);
            }
        }
        Ok((overall, per_topic))
    }

    pub(crate) fn compute_performance_score(
        &mut self,
        req: MemoryScoreRequest,
    ) -> Result<MemoryScoreResponse> {
        let topic_min = nonzero_or(req.topic_min_reviews, DEFAULT_TOPIC_MIN_REVIEWS);
        let deck_min = nonzero_or(req.deck_min_reviews, DEFAULT_DECK_MIN_REVIEWS);
        let topic_tags = req.topic_tags.clone();
        let (overall, per_topic) = self.accumulate_performance(&req)?;
        Ok(MemoryScoreResponse {
            overall: Some(overall.into_score(String::new(), deck_min)),
            topics: per_topic
                .into_iter()
                .zip(topic_tags)
                .map(|(acc, tag)| acc.into_score(tag, topic_min))
                .collect(),
        })
    }

    pub(crate) fn compute_readiness_score(
        &mut self,
        req: MemoryScoreRequest,
    ) -> Result<ReadinessScoreResponse> {
        let topic_min = nonzero_or(req.topic_min_reviews, DEFAULT_TOPIC_MIN_REVIEWS);
        let readiness_min = nonzero_or(req.deck_min_reviews, READINESS_MIN_REVIEWS);
        let topic_tags = req.topic_tags.clone();
        let (overall, per_topic) = self.accumulate_performance(&req)?;

        let topics_with_data = per_topic.iter().filter(|a| a.cards_with_value > 0).count();
        let coverage = if topic_tags.is_empty() {
            0.0
        } else {
            topics_with_data as f32 / topic_tags.len() as f32
        };

        let overall_score = overall.into_score(String::new(), readiness_min);
        // Readiness give-up rule: enough graded reviews AND at least half the
        // topics studied.
        let shown = overall_score.shown && coverage >= READINESS_MIN_COVERAGE;

        let topics = per_topic
            .into_iter()
            .zip(topic_tags)
            .map(|(acc, tag)| {
                let mastery = acc.into_score(tag, topic_min);
                ReadinessScore {
                    scaled_estimate: scale_section(mastery.estimate),
                    scaled_low: scale_section(mastery.range_low),
                    scaled_high: scale_section(mastery.range_high),
                    mastery: Some(mastery),
                }
            })
            .collect();

        Ok(ReadinessScoreResponse {
            scaled_estimate: scale_total(overall_score.estimate),
            scaled_low: scale_total(overall_score.range_low),
            scaled_high: scale_total(overall_score.range_high),
            coverage,
            shown,
            overall: Some(overall_score),
            topics,
        })
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
        fn add_reviewed_card_with_state(&mut self, tag: &str, difficulty: f32) -> CardId {
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
            // one graded review
            loop {
                if self.get_next_card().unwrap().is_none() {
                    break;
                }
                self.answer_good();
            }
            let mut card = self.storage.get_card(cid).unwrap().unwrap();
            card.memory_state = Some(FsrsMemoryState {
                stability: 100.0,
                difficulty,
            });
            card.last_review_time = Some(TimestampSecs::now());
            self.storage.update_card(&card).unwrap();
            cid
        }
    }

    /// Performance discounts by difficulty, so a hard card scores below an easy
    /// one at the same (high) stability; readiness maps overall onto 472..528
    /// with coverage, and its give-up rule hides the projection with too few
    /// reviews / too little coverage.
    #[test]
    fn performance_discounts_difficulty_and_readiness_scales_and_gives_up() {
        let mut col = Collection::new();
        let topics = vec!["mcat::a".to_string(), "mcat::b".to_string()];

        // topic a: an easy card (difficulty 1); topic b: a hard card (10).
        col.add_reviewed_card_with_state("mcat::a", 1.0);
        col.add_reviewed_card_with_state("mcat::b", 10.0);

        let req = || MemoryScoreRequest {
            search: "deck:Default".into(),
            topic_tags: topics.clone(),
            topic_min_reviews: 1,
            deck_min_reviews: 0,
        };

        let perf = col.compute_performance_score(req()).unwrap();
        let a = &perf.topics[0];
        let b = &perf.topics[1];
        assert!(a.cards_with_state == 1 && b.cards_with_state == 1);
        // Same stability, but the harder card yields a lower performance value.
        assert!(
            a.estimate > b.estimate,
            "easy topic {} should beat hard topic {}",
            a.estimate,
            b.estimate
        );
        // Performance is a valid probability inside its band.
        assert!(a.estimate > 0.0 && a.estimate <= 1.0);
        assert!(a.range_low <= a.estimate && a.estimate <= a.range_high);

        let readiness = col.compute_readiness_score(req()).unwrap();
        // Both topics have data -> full coverage.
        assert!((readiness.coverage - 1.0).abs() < 1e-6);
        // Projected total lands on the MCAT scale.
        assert!(readiness.scaled_estimate >= 472.0 && readiness.scaled_estimate <= 528.0);
        assert!(readiness.scaled_low <= readiness.scaled_estimate);
        assert!(readiness.scaled_estimate <= readiness.scaled_high);
        // Per-section projections land on 118..132.
        for t in &readiness.topics {
            assert!(t.scaled_estimate >= 118.0 && t.scaled_estimate <= 132.0);
        }
        // Give-up: only 2 graded reviews, far below the 200 default -> hidden.
        assert!(!readiness.shown, "readiness hidden below review threshold");
    }
}
