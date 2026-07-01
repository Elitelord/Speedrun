// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

//! Speedrun: topic-aware interleaving of the study queue.
//!
//! Anki normally presents review/new cards grouped by deck or sorted by a
//! single criterion. For MCAT study we want the session to *mix* topics
//! (Bio/Biochem, Chem/Phys, Psych/Soc) the way the exam does. This module
//! reorders the already-gathered cards into a round-robin across the configured
//! topic tags, preserving each topic's internal order.
//!
//! The mix can be *uniform* (one card per topic per pass) or *weakness
//! weighted*: when enabled, each topic's share of the round-robin is scaled by
//! its measured weakness (`1 - mean FSRS recall`), so topics the learner
//! remembers less well surface more often — concentrating study on
//! not-yet-mastered material rather than mixing evenly.
//!
//! Crucially this is purely a reordering step: it never mutates a card's due
//! date, interval, or FSRS memory state, so scheduling correctness and undo are
//! unaffected.

use std::collections::HashMap;
use std::collections::VecDeque;

use fsrs::FSRS;
use fsrs::FSRS5_DEFAULT_DECAY;

use super::QueueBuilder;
use crate::prelude::*;
use crate::scheduler::topics::topic_index_for_tags;

/// Lowest emission weight any topic can be given, so even a fully-mastered
/// topic still appears occasionally in a weakness-weighted mix.
const MIN_TOPIC_WEIGHT: f32 = 0.1;

/// Weakness assumed for a topic that has no reviewed cards yet (no FSRS memory
/// state to measure), i.e. a neutral `1 - 0.5`.
const UNKNOWN_TOPIC_WEAKNESS: f32 = 0.5;

impl QueueBuilder {
    /// Map each gathered card's note to a topic index, so `build()` can later
    /// interleave without needing the collection. When weakness weighting is
    /// on, also compute each topic's emission weight from the gathered review
    /// cards' FSRS recall. No-op unless interleaving is enabled and at least
    /// one topic tag is configured.
    pub(super) fn resolve_topics(&mut self, col: &mut Collection) -> Result<()> {
        if !self.interleaving_enabled() {
            return Ok(());
        }

        let mut note_ids: Vec<NoteId> = self
            .review
            .iter()
            .map(|c| c.note_id)
            .chain(self.new.iter().map(|c| c.note_id))
            .collect();
        note_ids.sort_unstable();
        note_ids.dedup();

        let topic_tags = &self.context.topic_tags;
        let mut map = HashMap::with_capacity(note_ids.len());
        for note in col.storage.get_note_tags_by_id_list(&note_ids)? {
            if let Some(idx) = topic_index_for_tags(&note.tags, topic_tags) {
                map.insert(note.id, idx);
            }
        }
        self.topic_map = map;

        if self.context.weight_by_weakness {
            self.topic_weights = self.compute_topic_weights(col)?;
        }

        Ok(())
    }

    /// Emission weight per topic (same order as `topic_tags`), derived from the
    /// mean FSRS recall of the gathered *review* cards in each topic. Weaker
    /// topics (lower recall) get larger weights; a topic with no reviewed cards
    /// falls back to a neutral weakness. Weights are floored so no topic is
    /// ever fully starved.
    fn compute_topic_weights(&self, col: &mut Collection) -> Result<Vec<f32>> {
        let num_topics = self.context.topic_tags.len();
        let timing = col.timing_today()?;
        let fsrs = FSRS::new(None)?;

        let mut recall_sum = vec![0.0f32; num_topics];
        let mut recall_count = vec![0u32; num_topics];

        for review in &self.review {
            let Some(&idx) = self.topic_map.get(&review.note_id) else {
                continue;
            };
            let Some(card) = col.storage.get_card(review.id)? else {
                continue;
            };
            if let Some(state) = card.memory_state {
                let elapsed = card.seconds_since_last_review(&timing).unwrap_or_default();
                let recall = fsrs.current_retrievability_seconds(
                    state.into(),
                    elapsed,
                    card.decay.unwrap_or(FSRS5_DEFAULT_DECAY),
                );
                recall_sum[idx] += recall;
                recall_count[idx] += 1;
            }
        }

        Ok((0..num_topics)
            .map(|i| {
                let weakness = if recall_count[i] > 0 {
                    1.0 - recall_sum[i] / recall_count[i] as f32
                } else {
                    UNKNOWN_TOPIC_WEAKNESS
                };
                weakness.max(MIN_TOPIC_WEIGHT)
            })
            .collect())
    }

    /// Reorder the gathered review and new cards into a round-robin across
    /// topics. Cards matching no configured topic keep their relative order and
    /// are appended after the interleaved cards.
    pub(super) fn interleave_by_topic(&mut self) {
        if !self.interleaving_enabled() {
            return;
        }
        let num_topics = self.context.topic_tags.len();
        let weights = self.emission_weights(num_topics);
        let topic_map = &self.topic_map;
        let topic_of = |note_id: NoteId| topic_map.get(&note_id).copied();

        self.review =
            weighted_round_robin_by_topic(std::mem::take(&mut self.review), &weights, |c| {
                topic_of(c.note_id)
            });
        self.new = weighted_round_robin_by_topic(std::mem::take(&mut self.new), &weights, |c| {
            topic_of(c.note_id)
        });
    }

    /// Per-topic weights for this build: the computed weakness weights when
    /// weighting is on and available, else uniform (`1.0` each), which makes
    /// the weighted round-robin degenerate to a plain one-per-topic
    /// round-robin.
    fn emission_weights(&self, num_topics: usize) -> Vec<f32> {
        if self.context.weight_by_weakness && self.topic_weights.len() == num_topics {
            self.topic_weights.clone()
        } else {
            vec![1.0; num_topics]
        }
    }

    fn interleaving_enabled(&self) -> bool {
        self.context.interleave_topics && !self.context.topic_tags.is_empty()
    }
}

/// Distribute `items` into `weights.len()` buckets by `topic_of`, then emit
/// them in a weight-proportional round-robin, preserving each bucket's input
/// order.
///
/// Emission order is stride-scheduled: each bucket has a virtual `next` cursor
/// advanced by `1 / weight` after it emits, and the non-empty bucket with the
/// smallest cursor emits next (ties break toward the lower topic index). With
/// equal weights this reduces to a plain one-per-topic round-robin. Items whose
/// `topic_of` is `None` are appended last in their original order.
fn weighted_round_robin_by_topic<T>(
    items: Vec<T>,
    weights: &[f32],
    topic_of: impl Fn(&T) -> Option<usize>,
) -> Vec<T> {
    let num_topics = weights.len();
    let total = items.len();
    let mut buckets: Vec<VecDeque<T>> = (0..num_topics).map(|_| VecDeque::new()).collect();
    let mut untagged: Vec<T> = Vec::new();
    for item in items {
        match topic_of(&item) {
            Some(idx) if idx < num_topics => buckets[idx].push_back(item),
            _ => untagged.push(item),
        }
    }

    // Stride per emission: heavier (weaker) topics advance more slowly, so they
    // reach the front more often. Guard against a zero/negative weight.
    let steps: Vec<f64> = weights
        .iter()
        .map(|&w| 1.0 / (w.max(MIN_TOPIC_WEIGHT) as f64))
        .collect();
    let mut cursors = vec![0.0f64; num_topics];

    let mut out = Vec::with_capacity(total);
    loop {
        // Pick the non-empty bucket with the smallest cursor (lowest index wins
        // ties), matching the deterministic one-per-pass order at equal weights.
        let mut chosen: Option<usize> = None;
        for i in 0..num_topics {
            if buckets[i].is_empty() {
                continue;
            }
            match chosen {
                Some(c) if cursors[i] >= cursors[c] => {}
                _ => chosen = Some(i),
            }
        }
        let Some(i) = chosen else { break };
        out.push(buckets[i].pop_front().unwrap());
        cursors[i] += steps[i];
    }
    out.extend(untagged);
    out
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn round_robin_preserves_within_topic_order_and_trails_untagged() {
        // three topics, uneven sizes, plus an untagged item
        let items = vec![
            (0, "a1"),
            (0, "a2"),
            (1, "b1"),
            (2, "c1"),
            (2, "c2"),
            (2, "c3"),
            (9, "x"), // untagged (>= num_topics)
        ];
        // uniform weights => plain one-per-topic round-robin
        let out = weighted_round_robin_by_topic(items, &[1.0, 1.0, 1.0], |(t, _)| Some(*t));
        let labels: Vec<&str> = out.iter().map(|(_, l)| *l).collect();
        assert_eq!(
            labels,
            vec!["a1", "b1", "c1", "a2", "c2", "c3", "x"],
            "round-robin should alternate topics, keep within-topic order, and append untagged last"
        );
    }

    #[test]
    fn weighted_round_robin_favours_heavier_topics() {
        // Topic 0 is weighted 3x topic 1: it should emit roughly three of its
        // cards for each one of topic 1, while keeping within-topic order.
        let items = vec![
            (0, "a1"),
            (0, "a2"),
            (0, "a3"),
            (1, "b1"),
            (1, "b2"),
            (1, "b3"),
        ];
        let out = weighted_round_robin_by_topic(items, &[3.0, 1.0], |(t, _)| Some(*t));
        let labels: Vec<&str> = out.iter().map(|(_, l)| *l).collect();
        // Topic 0 (weight 3) advances its cursor a third as fast, so it emits
        // three cards for each one of topic 1: it wins the first slot, then
        // reclaims the front after each single topic-1 emission.
        assert_eq!(labels, vec!["a1", "b1", "a2", "a3", "b2", "b3"]);
        // within-topic order preserved for both
        let a_order: Vec<&str> = labels
            .iter()
            .copied()
            .filter(|l| l.starts_with('a'))
            .collect();
        let b_order: Vec<&str> = labels
            .iter()
            .copied()
            .filter(|l| l.starts_with('b'))
            .collect();
        assert_eq!(a_order, vec!["a1", "a2", "a3"]);
        assert_eq!(b_order, vec!["b1", "b2", "b3"]);
    }
}
