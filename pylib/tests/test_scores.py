# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun: end-to-end tests of the Performance and Readiness score RPCs.

Confirms the new ComputePerformanceScore / ComputeReadinessScore protobuf RPCs
round-trip through the shared Rust engine from Python, return the expected
shape, place readiness on the MCAT scale, and apply their give-up rules.
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


def test_performance_score_rpc_shape():
    col = getEmptyCol()
    for tag in TOPICS:
        _add_tagged_review_card(col, tag)

    resp = col.sched.compute_performance_score(search="", topic_tags=TOPICS)
    assert resp.overall is not None
    assert len(resp.topics) == len(TOPICS)
    # No graded reviews yet -> below give-up threshold, so not shown.
    assert resp.overall.shown is False
    for topic in resp.topics:
        assert 0.0 <= topic.estimate <= 1.0


def test_readiness_score_rpc_scale_and_giveup():
    col = getEmptyCol()
    for tag in TOPICS:
        _add_tagged_review_card(col, tag)

    resp = col.sched.compute_readiness_score(search="", topic_tags=TOPICS)
    # Projected total lands on the real MCAT scale.
    assert 472.0 <= resp.scaled_estimate <= 528.0
    assert resp.scaled_low <= resp.scaled_estimate <= resp.scaled_high
    # Per-section projections land on 118..132.
    assert len(resp.topics) == len(TOPICS)
    for topic in resp.topics:
        assert 118.0 <= topic.scaled_estimate <= 132.0
    # coverage is a fraction; give-up hides readiness with no graded reviews.
    assert 0.0 <= resp.coverage <= 1.0
    assert resp.shown is False
