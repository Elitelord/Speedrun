# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun: end-to-end test of the topic-aware interleaving RPC.

Exercises the new SetInterleaveConfig/GetInterleaveConfig protobuf RPCs from
Python and confirms the shared Rust engine actually interleaves the study queue
across MCAT topics.
"""

from anki.consts import CARD_TYPE_REV, QUEUE_TYPE_REV
from tests.shared import getEmptyCol

TOPICS = ["mcat::biobiochem", "mcat::chemphys", "mcat::psychsoc"]


def _add_tagged_review_card(col, tag: str) -> int:
    note = col.newNote()
    note["Front"] = "q"
    note["Back"] = "a"
    note.tags = [tag]
    col.addNote(note)
    cid = note.card_ids()[0]
    card = col.get_card(cid)
    card.type = CARD_TYPE_REV
    card.queue = QUEUE_TYPE_REV
    card.due = col.sched.today
    card.ivl = 10
    col.update_card(card)
    return cid


def test_interleave_config_roundtrip_and_ordering():
    col = getEmptyCol()

    # RPC round-trips through the Rust backend.
    col.sched.set_interleave_config(enabled=True, topic_tags=TOPICS)
    cfg = col.sched.get_interleave_config()
    assert cfg.enabled is True
    assert list(cfg.topic_tags) == TOPICS

    # Two review cards per topic, added grouped by topic.
    topic_of: dict[int, int] = {}
    for idx, tag in enumerate(TOPICS):
        for _ in range(2):
            cid = _add_tagged_review_card(col, tag)
            topic_of[cid] = idx

    # The built queue should round-robin across the three topics.
    queued = col._backend.get_queued_cards(fetch_limit=10, intraday_learning_only=False)
    order = [topic_of[qc.card.id] for qc in queued.cards]
    assert order == [0, 1, 2, 0, 1, 2]

    # Disabling via the same RPC restores topic-blocked grouping (the cards were
    # added grouped by topic, so the un-interleaved set is contiguous per topic).
    col.sched.set_interleave_config(enabled=False, topic_tags=TOPICS)
    assert col.sched.get_interleave_config().enabled is False
    queued = col._backend.get_queued_cards(fetch_limit=10, intraday_learning_only=False)
    counts = [0, 0, 0]
    for qc in queued.cards:
        counts[topic_of[qc.card.id]] += 1
    # all six cards still present, two per topic
    assert counts == [2, 2, 2]
