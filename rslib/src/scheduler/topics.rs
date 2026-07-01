// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

//! Speedrun: shared helper for mapping a note's tags to an MCAT topic.
//!
//! Used by the topic-aware interleaving scheduler
//! ([`crate::scheduler::queue::builder`]) and the honest memory score
//! ([`crate::scheduler::memory_score`]) so both classify cards identically.

/// Returns the index of the first configured topic (in `topic_tags` order) that
/// the note's space-separated `tags` match. A note tag matches a topic when it
/// equals the topic tag or is a subtag of it (`mcat::biobiochem::genetics`
/// matches topic `mcat::biobiochem`). Returns `None` when no topic matches.
pub(crate) fn topic_index_for_tags(tags: &str, topic_tags: &[String]) -> Option<usize> {
    let card_tags: Vec<&str> = tags.split_whitespace().collect();
    topic_tags.iter().position(|topic| {
        card_tags
            .iter()
            .any(|tag| *tag == topic.as_str() || is_subtag_of(tag, topic))
    })
}

fn is_subtag_of(tag: &str, parent: &str) -> bool {
    tag.len() > parent.len()
        && tag.as_bytes()[parent.len()] == b':'
        && tag.starts_with(parent)
        && tag[parent.len()..].starts_with("::")
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn matches_exact_and_subtags() {
        let topics = vec!["mcat::biobiochem".to_string(), "mcat::chemphys".to_string()];
        assert_eq!(topic_index_for_tags("mcat::biobiochem", &topics), Some(0));
        assert_eq!(topic_index_for_tags("mcat::chemphys", &topics), Some(1));
        // subtag matches its parent topic
        assert_eq!(
            topic_index_for_tags("mcat::chemphys::thermo", &topics),
            Some(1)
        );
        // unrelated / prefix-but-not-subtag does not match
        assert_eq!(topic_index_for_tags("mcat::psychsoc", &topics), None);
        assert_eq!(topic_index_for_tags("mcat::chemphysics", &topics), None);
        assert_eq!(topic_index_for_tags("", &topics), None);
    }

    #[test]
    fn first_configured_topic_wins() {
        let topics = vec!["a".to_string(), "b".to_string()];
        // a card carrying both tags is assigned to the earlier-configured topic
        assert_eq!(topic_index_for_tags("b a", &topics), Some(0));
    }
}
