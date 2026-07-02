# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun: the pure grade->ease mapping for the free-text production loop.

Testing the pure decision table avoids threading/Qt flakiness while pinning the
FSRS-consistent behaviour: correct first try -> Good, correct after a hint ->
Hard, wrong/revealed -> Again, and an explicit grader ease wins.
"""

from __future__ import annotations

from aqt.reviewer import Reviewer


def test_decide_ease_attempt_defaults() -> None:
    assert Reviewer._decide_ease("correct", None, 1) == 3  # Good, first try
    assert Reviewer._decide_ease("correct", None, 2) == 2  # Hard, after a hint
    assert Reviewer._decide_ease("wrong", None, 2) == 1  # Again
    assert Reviewer._decide_ease("partial", None, 1) == 1  # Again


def test_decide_ease_honours_explicit_grader_ease() -> None:
    assert Reviewer._decide_ease("correct", 4, 1) == 4  # grader forced Easy
    assert Reviewer._decide_ease("wrong", 2, 2) == 2
    # out-of-range grader ease falls back to the attempt default
    assert Reviewer._decide_ease("correct", 9, 1) == 3
