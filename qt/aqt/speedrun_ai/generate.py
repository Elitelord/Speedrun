# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: grounded MCAT card generation.

Each card is generated from a specific source chunk and must be *supported* by
that chunk — a hard grounding precondition (Brainlift 4.5). Cards whose answer is
not grounded in their cited chunk are flagged and blocked downstream regardless
of any LLM judgement, so a fabricated fact can't slip through.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from .rag import Chunk

_WORD = re.compile(r"[a-z0-9]+")

# Content words that carry no topical signal; ignored by the grounding check.
_STOPWORDS = frozenset(
    "the a an of to in is are and or for with that this it as by be on at from "
    "which what when how why does do into than then two both each per its".split()
)


class _Chat(Protocol):
    def chat(self, messages: list[dict[str, str]], **opts: Any) -> str: ...


@dataclass
class CardDraft:
    front: str
    back: str
    topic_tag: str
    source_name: str
    chunk_id: str
    supported: bool = True
    reasons: list[str] = field(default_factory=list)


_GEN_SYSTEM = (
    "You are an MCAT content author. From the provided source text, write "
    "high-quality flashcards (a specific question + a concise, correct answer) "
    "testing facts a student must know for the MCAT. Use ONLY facts stated in "
    "the text — never add outside knowledge. If the text has no testable "
    'content, return an empty list. Output JSON: {"cards": [{"front": ..., '
    '"back": ...}, ...]}.'
)


def _content_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS}


def is_grounded(back: str, source_text: str, threshold: float = 0.5) -> bool:
    """A card answer is grounded when at least ``threshold`` of its content words
    appear in the cited source chunk. Cheap, deterministic, and independent of
    the LLM — the guardrail that blocks fabricated answers."""
    answer_words = _content_words(back)
    if not answer_words:
        return False
    source_words = _content_words(source_text)
    overlap = len(answer_words & source_words) / len(answer_words)
    return overlap >= threshold


def parse_cards(raw: str, topic_tag: str, chunk: Chunk) -> list[CardDraft]:
    """Parse the model's JSON reply into drafts, grounding each against the
    source chunk. Malformed output yields no cards (never raises)."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    items = data.get("cards", []) if isinstance(data, dict) else []
    drafts: list[CardDraft] = []
    for item in items:
        front = str(item.get("front", "")).strip()
        back = str(item.get("back", "")).strip()
        if not front or not back:
            continue
        grounded = is_grounded(back, chunk.text)
        drafts.append(
            CardDraft(
                front=front,
                back=back,
                topic_tag=topic_tag,
                source_name=chunk.source_name,
                chunk_id=chunk.chunk_id,
                supported=grounded,
                reasons=[] if grounded else ["answer not grounded in source chunk"],
            )
        )
    return drafts


def generate_cards(
    chunks: list[Chunk], client: _Chat, topic_tag: str
) -> list[CardDraft]:
    """Generate grounded drafts from every chunk of a source. Each draft records
    its source name + chunk id so cards trace back to a named source."""
    drafts: list[CardDraft] = []
    for chunk in chunks:
        raw = client.chat(
            [
                {"role": "system", "content": _GEN_SYSTEM},
                {"role": "user", "content": chunk.text},
            ],
            response_format={"type": "json_object"},
        )
        drafts.extend(parse_cards(raw, topic_tag, chunk))
    return drafts
