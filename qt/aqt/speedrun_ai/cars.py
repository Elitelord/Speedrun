# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: grounded CARS (Critical Analysis & Reasoning) generation.

MCAT CARS is *reasoning*, not recall: a ~500-600 word humanities/social-science
passage plus single-best-answer questions (main idea, inference, tone,
application). The recall-card grounding gate (bag-of-words overlap in
``generate.py``) is the wrong tool here — a good inference question is
deliberately *not* a lexical echo of the passage.

So CARS uses a different, stronger grounding gate: a question is *supported* only
if an **independent** model re-read of the passage — given ONLY the passage,
stem, and options — selects the keyed answer. That checks two things at once:
the question is answerable from the passage alone (no outside knowledge), and the
key is the single best answer. A question that fails is blocked, exactly like an
ungrounded recall card. Under the offline :class:`FakeClient` no unit is produced
(``chat`` returns ``"{}"``), so the whole path degrades cleanly.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

QTYPES = ("main-idea", "inference", "tone", "application")


class _Chat(Protocol):
    def chat(self, messages: list[dict[str, str]], **opts: Any) -> str: ...


@dataclass
class CarsQuestion:
    stem: str
    options: list[str]
    answer_index: int
    explanation: str
    qtype: str
    supported: bool = True
    reasons: list[str] = field(default_factory=list)


@dataclass
class CarsUnit:
    passage: str
    source_name: str
    topic_tag: str
    questions: list[CarsQuestion] = field(default_factory=list)

    @property
    def supported_questions(self) -> list[CarsQuestion]:
        return [q for q in self.questions if q.supported]


_GEN_SYSTEM = (
    "You are an MCAT CARS item writer. From the provided source text, write ONE "
    "self-contained passage of about 500-600 words in an analytical humanities / "
    "social-science register (argument, interpretation, or synthesis — NOT a list "
    "of facts), staying faithful to the ideas in the source. Then write "
    "single-best-answer multiple-choice questions that test REASONING about the "
    "passage (main idea, inference, author tone/attitude, or applying the "
    "argument to a new case) — never mere recall of a stated fact. Each question "
    "has exactly 4 options, exactly one clearly best answer supported by the "
    "passage, and the other three defensibly wrong. "
    'Output JSON only: {"passage": "...", "questions": [{"stem": "...", '
    '"options": ["...","...","...","..."], "answer_index": 0, "explanation": '
    '"why the key is best and others are not", "qtype": "inference"}]}.'
)

_ANSWER_SYSTEM = (
    "You are answering an MCAT CARS question using ONLY the passage provided. Do "
    "not use outside knowledge. Choose the single best answer. Output JSON only: "
    '{"answer_index": <0-based integer>}.'
)


def parse_units(raw: str, source_name: str, topic_tag: str) -> list[CarsUnit]:
    """Parse the model's JSON reply into CARS units. Accepts either a single
    passage object or a list of them. Malformed output yields no units."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    blocks = data if isinstance(data, list) else [data]
    units: list[CarsUnit] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        passage = str(block.get("passage", "")).strip()
        if not passage:
            continue
        questions: list[CarsQuestion] = []
        for item in block.get("questions", []) or []:
            stem = str(item.get("stem", "")).strip()
            options = [
                str(o).strip() for o in item.get("options", []) if str(o).strip()
            ]
            try:
                answer_index = int(item.get("answer_index", -1))
            except (ValueError, TypeError):
                answer_index = -1
            if not stem or len(options) != 4 or not (0 <= answer_index < 4):
                continue
            qtype = str(item.get("qtype", "")).strip() or "inference"
            questions.append(
                CarsQuestion(
                    stem=stem,
                    options=options,
                    answer_index=answer_index,
                    explanation=str(item.get("explanation", "")).strip(),
                    qtype=qtype,
                )
            )
        if questions:
            units.append(CarsUnit(passage, source_name, topic_tag, questions))
    return units


def answer_question(
    passage: str, stem: str, options: list[str], client: _Chat
) -> int | None:
    """Independent model re-read: pick the best option index from the passage
    alone. Returns None if the reply is unusable (the offline stub, or malformed
    output) — the caller treats that as 'not supported'."""
    user = json.dumps({"passage": passage, "question": stem, "options": options})
    raw = client.chat(
        [
            {"role": "system", "content": _ANSWER_SYSTEM},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(raw)
        idx = int(data.get("answer_index", -1))
    except (ValueError, TypeError, AttributeError):
        return None
    return idx if 0 <= idx < len(options) else None


def ground_unit(unit: CarsUnit, client: _Chat) -> CarsUnit:
    """Mark each question supported iff an independent re-read agrees with its
    key (answerable from the passage AND single-best-answer)."""
    for q in unit.questions:
        picked = answer_question(unit.passage, q.stem, q.options, client)
        if picked is None:
            q.supported = False
            q.reasons = ["independent re-read could not answer from the passage"]
        elif picked != q.answer_index:
            q.supported = False
            q.reasons = ["independent re-read disagreed with the answer key"]
        else:
            q.supported = True
            q.reasons = []
    return unit


def generate_cars(
    source_text: str, source_name: str, topic_tag: str, client: _Chat
) -> list[CarsUnit]:
    """Generate a grounded CARS unit from a source: draft a passage + questions,
    then gate every question through the independent-re-read grounding check."""
    raw = client.chat(
        [
            {"role": "system", "content": _GEN_SYSTEM},
            {"role": "user", "content": source_text},
        ],
        response_format={"type": "json_object"},
    )
    units = parse_units(raw, source_name, topic_tag)
    return [ground_unit(u, client) for u in units]


def unit_to_dict(unit: CarsUnit) -> dict[str, Any]:
    return asdict(unit)
