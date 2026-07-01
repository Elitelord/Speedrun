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
//! Crucially this is purely a reordering step: it never mutates a card's due
//! date, interval, or FSRS memory state, so scheduling correctness and undo are
//! unaffected.

use std::collections::HashMap;
use std::collections::VecDeque;

use super::QueueBuilder;
use crate::prelude::*;
use crate::scheduler::topics::topic_index_for_tags;

impl QueueBuilder {
    /// Map each gathered card's note to a topic index, so `build()` can later
    /// interleave without needing the collection. No-op unless interleaving is
    /// enabled and at least one topic tag is configured.
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

        Ok(())
    }

    /// Reorder the gathered review and new cards into a round-robin across
    /// topics. Cards matching no configured topic keep their relative order and
    /// are appended after the interleaved cards.
    pub(super) fn interleave_by_topic(&mut self) {
        if !self.interleaving_enabled() {
            return;
        }
        let num_topics = self.context.topic_tags.len();
        let topic_map = &self.topic_map;
        let topic_of = |note_id: NoteId| topic_map.get(&note_id).copied();

        self.review = round_robin_by_topic(std::mem::take(&mut self.review), num_topics, |c| {
            topic_of(c.note_id)
        });
        self.new = round_robin_by_topic(std::mem::take(&mut self.new), num_topics, |c| {
            topic_of(c.note_id)
        });
    }

    fn interleaving_enabled(&self) -> bool {
        self.context.interleave_topics && !self.context.topic_tags.is_empty()
    }
}

/// Distribute `items` into `num_topics` buckets by `topic_of`, then emit them
/// round-robin (one from each non-empty bucket per pass), preserving each
/// bucket's input order. Items whose `topic_of` is `None` are appended last in
/// their original order.
fn round_robin_by_topic<T>(
    items: Vec<T>,
    num_topics: usize,
    topic_of: impl Fn(&T) -> Option<usize>,
) -> Vec<T> {
    let total = items.len();
    let mut buckets: Vec<VecDeque<T>> = (0..num_topics).map(|_| VecDeque::new()).collect();
    let mut untagged: Vec<T> = Vec::new();
    for item in items {
        match topic_of(&item) {
            Some(idx) if idx < num_topics => buckets[idx].push_back(item),
            _ => untagged.push(item),
        }
    }

    let mut out = Vec::with_capacity(total);
    loop {
        let mut emitted = false;
        for bucket in buckets.iter_mut() {
            if let Some(item) = bucket.pop_front() {
                out.push(item);
                emitted = true;
            }
        }
        if !emitted {
            break;
        }
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
        let out = round_robin_by_topic(items, 3, |(t, _)| Some(*t));
        let labels: Vec<&str> = out.iter().map(|(_, l)| *l).collect();
        assert_eq!(
            labels,
            vec!["a1", "b1", "c1", "a2", "c2", "c3", "x"],
            "round-robin should alternate topics, keep within-topic order, and append untagged last"
        );
    }
}
