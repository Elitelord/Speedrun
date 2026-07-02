# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the keyword baseline retriever (the "simpler method" to beat).

A standard BM25 ranker over the same chunks the RAG path embeds. The eval
harness runs both retrievers on the held-out gold set and reports whether the
embedding path beats this baseline (brief requirement: beat a keyword/vector
baseline). Pure-Python (``rank_bm25``); dev/eval-only, never on the hot path.
"""

from __future__ import annotations

import re

from .rag import Chunk, Retrieved

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class Bm25Index:
    """Same ``retrieve`` shape as :func:`.rag.retrieve` so the eval harness can
    swap retrievers behind one interface."""

    def __init__(self, chunks: list[Chunk]) -> None:
        from rank_bm25 import BM25Okapi  # type: ignore[import-not-found,import-untyped]

        self._chunks = chunks
        self._bm25 = BM25Okapi([_tokenize(c.text) for c in chunks])

    def retrieve(self, query: str, k: int = 5) -> list[Retrieved]:
        if not self._chunks:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [
            Retrieved(
                chunk_id=self._chunks[i].chunk_id,
                source_name=self._chunks[i].source_name,
                text=self._chunks[i].text,
                score=float(scores[i]),
            )
            for i in order
        ]
