# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the retrieval-augmented-generation path.

Chunk MCAT source text, embed the chunks with OpenAI, and retrieve the most
relevant chunks for a query by cosine similarity. The index is a plain JSON blob
(chunks + vectors); retrieval is a single numpy matmul — no vector DB, no binary
deps, fully deterministic given a fixed embedding model. This is the "AI path"
we show beats the keyword baseline in :mod:`.baseline`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


class _Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class Chunk:
    chunk_id: str
    source_name: str
    text: str


@dataclass
class Retrieved:
    chunk_id: str
    source_name: str
    text: str
    score: float


def chunk_text(
    text: str, source_name: str, target_words: int = 220, overlap: int = 40
) -> list[Chunk]:
    """Split ``text`` into overlapping, paragraph-aware chunks of roughly
    ``target_words`` words. Overlap keeps facts that straddle a boundary
    retrievable."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[Chunk] = []
    buf: list[str] = []
    count = 0
    idx = 0

    def flush() -> None:
        nonlocal buf, count, idx
        if not buf:
            return
        chunks.append(
            Chunk(
                chunk_id=f"{source_name}#{idx}",
                source_name=source_name,
                text="\n\n".join(buf).strip(),
            )
        )
        idx += 1
        # Carry the tail as overlap into the next chunk.
        if overlap > 0:
            tail_words = " ".join(buf).split()[-overlap:]
            buf = [" ".join(tail_words)] if tail_words else []
            count = len(tail_words)
        else:
            buf = []
            count = 0

    for para in paragraphs:
        words = len(para.split())
        if count + words > target_words and buf:
            flush()
        buf.append(para)
        count += words
    if buf:
        chunks.append(
            Chunk(
                chunk_id=f"{source_name}#{idx}",
                source_name=source_name,
                text="\n\n".join(buf).strip(),
            )
        )
    return chunks


def build_index(chunks: list[Chunk], client: _Embedder, model: str = "") -> dict[str, Any]:
    vectors = client.embed([c.text for c in chunks])
    dim = len(vectors[0]) if vectors else 0
    return {
        "model": model,
        "dim": dim,
        "entries": [
            {
                "chunk_id": c.chunk_id,
                "source_name": c.source_name,
                "text": c.text,
                "vector": vec,
            }
            for c, vec in zip(chunks, vectors)
        ],
    }


def save_index(index: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index), encoding="utf-8")


def load_index(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def retrieve(
    query: str, index: dict[str, Any], client: _Embedder, k: int = 5
) -> list[Retrieved]:
    import numpy as np  # type: ignore[import-not-found,import-untyped]

    entries = index.get("entries", [])
    if not entries:
        return []
    mat = np.array([e["vector"] for e in entries], dtype="float32")
    qv = np.array(client.embed([query])[0], dtype="float32")
    # Cosine similarity = normalised dot product.
    mat_norm = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-8)
    q_norm = qv / (np.linalg.norm(qv) + 1e-8)
    scores = mat_norm @ q_norm
    order = np.argsort(-scores)[:k]
    return [
        Retrieved(
            chunk_id=entries[i]["chunk_id"],
            source_name=entries[i]["source_name"],
            text=entries[i]["text"],
            score=float(scores[i]),
        )
        for i in order
    ]
