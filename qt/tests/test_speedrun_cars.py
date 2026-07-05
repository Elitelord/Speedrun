# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Tests for the Speedrun CARS generation + eval subsystem — network-free.

Covers passage/question parsing, the independent-re-read grounding gate, the
offline (FakeClient) degradation to zero units, and the CARS eval confusion
matrix / cutoff logic — all without an API key or network.
"""

from __future__ import annotations

import json
from typing import Any

from aqt.speedrun_ai import cars, cars_eval
from aqt.speedrun_ai.client import FakeClient

_GOOD_UNIT = {
    "passage": "A passage about ethics and its two competing traditions.",
    "questions": [
        {
            "stem": "What is the main idea?",
            "options": ["contrast two traditions", "a biography", "a recipe", "a poem"],
            "answer_index": 0,
            "explanation": "The passage contrasts two traditions.",
            "qtype": "main-idea",
        }
    ],
}


class _StubChat:
    """A chat client that generates the fixed unit and answers with a fixed
    index, so grounding is deterministic in tests."""

    def __init__(self, gen: str, answer_index: int) -> None:
        self._gen = gen
        self._answer_index = answer_index

    def chat(self, messages: list[dict[str, str]], **opts: Any) -> str:
        # The answer prompt carries an "options" key in the user JSON.
        user = messages[-1]["content"]
        if '"options"' in user and '"question"' in user:
            return json.dumps({"answer_index": self._answer_index})
        return self._gen


# -- parsing ---------------------------------------------------------------


def test_parse_units_valid() -> None:
    units = cars.parse_units(json.dumps(_GOOD_UNIT), "src", "mcat::cars")
    assert len(units) == 1
    assert units[0].source_name == "src"
    assert units[0].topic_tag == "mcat::cars"
    assert len(units[0].questions) == 1
    assert units[0].questions[0].answer_index == 0


def test_parse_units_malformed_yields_nothing() -> None:
    assert cars.parse_units("not json", "s", "mcat::cars") == []
    assert cars.parse_units("{}", "s", "mcat::cars") == []


def test_parse_units_skips_bad_questions() -> None:
    block = {
        "passage": "p",
        "questions": [
            {"stem": "q", "options": ["a", "b", "c"], "answer_index": 0},  # 3 options
            {"stem": "q", "options": ["a", "b", "c", "d"], "answer_index": 9},  # oob
            {"stem": "", "options": ["a", "b", "c", "d"], "answer_index": 0},  # no stem
        ],
    }
    assert cars.parse_units(json.dumps(block), "s", "mcat::cars") == []


# -- grounding gate --------------------------------------------------------


def test_ground_unit_supported_when_reread_agrees() -> None:
    client = _StubChat(json.dumps(_GOOD_UNIT), answer_index=0)
    unit = cars.parse_units(json.dumps(_GOOD_UNIT), "src", "mcat::cars")[0]
    cars.ground_unit(unit, client)
    assert unit.questions[0].supported is True
    assert unit.supported_questions


def test_ground_unit_blocked_when_reread_disagrees() -> None:
    client = _StubChat(json.dumps(_GOOD_UNIT), answer_index=2)  # disagrees with key 0
    unit = cars.parse_units(json.dumps(_GOOD_UNIT), "src", "mcat::cars")[0]
    cars.ground_unit(unit, client)
    assert unit.questions[0].supported is False
    assert not unit.supported_questions


def test_generate_cars_offline_is_empty() -> None:
    # FakeClient.chat returns "{}" -> no passage -> zero units (AI-off invariant).
    assert cars.generate_cars("source text", "src", "mcat::cars", FakeClient()) == []


# -- eval gate -------------------------------------------------------------


def test_classify_questions_confusion() -> None:
    gold = [
        {
            "passage": "p",
            "stem": "s",
            "options": ["a", "b", "c", "d"],
            "answer_index": 0,
            "label": "good",
        },
        {
            "passage": "p",
            "stem": "s",
            "options": ["a", "b", "c", "d"],
            "answer_index": 0,
            "label": "bad",
        },
    ]

    # A classifier that always picks index 0: agrees with both keys -> both ship.
    def always_zero(passage: str, stem: str, options: list[str]) -> int:
        return 0

    c = cars_eval.classify_questions(gold, always_zero)
    # good+shipped = TN; bad+shipped = FN (the dangerous cell)
    assert c.tn == 1 and c.fn == 1 and c.tp == 0 and c.fp == 0


def test_run_cars_eval_gate() -> None:
    # Bad question has key 0 but the true best answer (what the re-read picks) is 1,
    # so a faithful classifier blocks it (TP); good question's key matches (TN).
    gold = [
        {
            "passage": "p",
            "stem": "g",
            "options": ["a", "b", "c", "d"],
            "answer_index": 0,
            "label": "good",
        },
        {
            "passage": "p",
            "stem": "b",
            "options": ["a", "b", "c", "d"],
            "answer_index": 0,
            "label": "bad",
        },
    ]
    best = {"g": 0, "b": 1}

    def faithful(passage: str, stem: str, options: list[str]) -> int:
        return best[stem]

    cutoff = {"min_accuracy": 0.8, "max_false_negative_rate": 0.1}
    result = cars_eval.run_cars_eval(gold, faithful, cutoff)
    assert result["confusion"]["tn"] == 1
    assert result["confusion"]["tp"] == 1
    assert result["card_metrics"]["false_negative_rate"] == 0.0
    assert result["passed"] is True
