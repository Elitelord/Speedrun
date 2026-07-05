# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the reproducible card-generation + eval pipeline.

Source of truth for the Friday AI gate. Subcommands:

    python -m aqt.speedrun_ai.pipeline build-index   # chunk + embed sources
    python -m aqt.speedrun_ai.pipeline generate      # grounded card drafts
    python -m aqt.speedrun_ai.pipeline eval          # gate vs pre-set cutoff
    python -m aqt.speedrun_ai.pipeline emit          # write PASSING cards -> TSV

Run with the built pylib on the path, e.g.:

    PYTHONPATH="pylib;out/pylib" out/pyenv/scripts/python.exe \
        -m aqt.speedrun_ai.pipeline eval

Pass ``--fake`` to use the deterministic offline client (used by the CI test).
Determinism: temperature 0, a fixed embedding model, cosine over stored vectors.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import get_client
from .client import FakeClient
from .generate import CardDraft, generate_cards
from .rag import Chunk, build_index, chunk_text, load_index, retrieve, save_index

RECALL_K = 5


def ai_dir() -> Path:
    # speedrun_ai -> aqt -> qt -> repo root
    return Path(__file__).resolve().parents[3] / "docs" / "speedrun" / "ai"


def _source_dir() -> Path:
    return ai_dir() / "source"


def _generated_dir() -> Path:
    return ai_dir() / "generated"


def cars_dir() -> Path:
    return ai_dir() / "cars"


def _cars_generated_dir() -> Path:
    return cars_dir() / "generated"


def load_sources() -> list[dict[str, str]]:
    """Read the source manifest: [{file, name, topic}, ...]."""
    manifest = ai_dir() / "sources.json"
    return json.loads(manifest.read_text(encoding="utf-8"))


def _chunks_for(source: dict[str, str]) -> list[Chunk]:
    text = (_source_dir() / source["file"]).read_text(encoding="utf-8")
    return chunk_text(text, source["name"])


def _all_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    for source in load_sources():
        chunks.extend(_chunks_for(source))
    return chunks


def cmd_build_index(client: Any) -> int:
    chunks = _all_chunks()
    index = build_index(chunks, client)
    save_index(index, ai_dir() / "index.json")
    print(f"indexed {len(chunks)} chunks -> {ai_dir() / 'index.json'}")
    return 0


def cmd_generate(client: Any) -> int:
    drafts: list[CardDraft] = []
    for source in load_sources():
        drafts.extend(generate_cards(_chunks_for(source), client, source["topic"]))
    out = _generated_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "drafts.json").write_text(
        json.dumps([asdict(d) for d in drafts], indent=1), encoding="utf-8"
    )
    supported = sum(1 for d in drafts if d.supported)
    print(f"generated {len(drafts)} drafts ({supported} grounded) -> {out}")
    return 0


def cmd_eval(client: Any) -> int:
    from .eval import run_eval, write_report

    index = load_index(ai_dir() / "index.json")
    gold = _load_gold()
    cutoff = json.loads((ai_dir() / "cutoff.json").read_text(encoding="utf-8"))

    def rag_retriever(q: str) -> Any:
        return retrieve(q, index, client, k=RECALL_K)

    bm25_retriever = _make_bm25_retriever(index)

    result = run_eval(gold, index, cutoff, rag_retriever, bm25_retriever)
    (ai_dir() / "eval-result.json").write_text(
        json.dumps(result, indent=1), encoding="utf-8"
    )
    write_report(result, ai_dir() / "eval-report.md")
    print(json.dumps(result["checks"], indent=1))
    print("PASSED" if result["passed"] else "FAILED")
    return 0 if result["passed"] else 1


def cmd_emit() -> int:
    from .emit import write_tsvs

    result_path = ai_dir() / "eval-result.json"
    if not result_path.exists():
        print("no eval-result.json — run `eval` first", file=sys.stderr)
        return 1
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not result.get("passed"):
        print("eval did not pass the cutoff — refusing to emit cards", file=sys.stderr)
        return 1
    drafts_raw = json.loads(
        (_generated_dir() / "drafts.json").read_text(encoding="utf-8")
    )
    drafts = [CardDraft(**d) for d in drafts_raw]
    counts = write_tsvs(drafts, _generated_dir())
    print(f"emitted passing cards: {counts}")
    return 0


def _load_gold() -> list[dict[str, Any]]:
    from .eval import load_gold

    return load_gold(ai_dir() / "gold.jsonl")


# -- CARS track (passages + multiple-choice reasoning questions) -------------


def _load_cars_sources() -> list[dict[str, str]]:
    return json.loads((cars_dir() / "sources.json").read_text(encoding="utf-8"))


def cmd_cars_generate(client: Any) -> int:
    from .cars import generate_cars, unit_to_dict

    units = []
    for source in _load_cars_sources():
        text = (cars_dir() / "source" / source["file"]).read_text(encoding="utf-8")
        units.extend(generate_cars(text, source["name"], source["topic"], client))
    out = _cars_generated_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "units-draft.json").write_text(
        json.dumps([unit_to_dict(u) for u in units], indent=1), encoding="utf-8"
    )
    total_q = sum(len(u.questions) for u in units)
    grounded_q = sum(len(u.supported_questions) for u in units)
    print(
        f"generated {len(units)} CARS passages, {total_q} questions "
        f"({grounded_q} grounded) -> {out}"
    )
    return 0


def cmd_cars_eval(client: Any) -> int:
    from .cars import answer_question
    from .cars_eval import load_cars_gold, run_cars_eval, write_report

    gold = load_cars_gold(cars_dir() / "gold.jsonl")
    cutoff = json.loads((cars_dir() / "cutoff.json").read_text(encoding="utf-8"))

    def answer_fn(passage: str, stem: str, options: list[str]) -> Any:
        return answer_question(passage, stem, options, client)

    result = run_cars_eval(gold, answer_fn, cutoff)
    (cars_dir() / "cars-eval-result.json").write_text(
        json.dumps(result, indent=1), encoding="utf-8"
    )
    write_report(result, cars_dir() / "cars-eval-report.md")
    print(json.dumps(result["checks"], indent=1))
    print("PASSED" if result["passed"] else "FAILED")
    return 0 if result["passed"] else 1


def cmd_cars_emit() -> int:
    """Write eval-passed CARS units (supported questions only) for the deck
    builder. Refuses unless the CARS eval passed its cutoff."""
    result_path = cars_dir() / "cars-eval-result.json"
    if not result_path.exists():
        print("no cars-eval-result.json — run `cars-eval` first", file=sys.stderr)
        return 1
    if not json.loads(result_path.read_text(encoding="utf-8")).get("passed"):
        print("CARS eval did not pass the cutoff — refusing to emit", file=sys.stderr)
        return 1
    draft_path = _cars_generated_dir() / "units-draft.json"
    if not draft_path.exists():
        print("no units-draft.json — run `cars-generate` first", file=sys.stderr)
        return 1
    units = json.loads(draft_path.read_text(encoding="utf-8"))
    emitted = []
    for u in units:
        supported = [q for q in u.get("questions", []) if q.get("supported")]
        if supported:
            emitted.append({**u, "questions": supported})
    out = _cars_generated_dir() / "units.json"
    out.write_text(json.dumps(emitted, indent=1), encoding="utf-8")
    n_q = sum(len(u["questions"]) for u in emitted)
    print(f"emitted {len(emitted)} CARS passages, {n_q} grounded questions -> {out}")
    return 0


def _make_bm25_retriever(index: dict[str, Any]) -> Any:
    """Build the BM25 baseline retriever from the index chunks, or None if
    rank_bm25 isn't installed (retrieval comparison then degrades to RAG-only)."""
    try:
        from .baseline import Bm25Index
    except Exception:
        return None
    chunks = [
        Chunk(e["chunk_id"], e["source_name"], e["text"])
        for e in index.get("entries", [])
    ]
    bm25 = Bm25Index(chunks)
    return lambda q: bm25.retrieve(q, k=RECALL_K)


def _client(use_fake: bool) -> Any:
    if use_fake:
        return FakeClient()
    client = get_client()
    if client is None:
        print(
            "AI is disabled or no OPENAI_API_KEY found. Set it in .env or the "
            "environment, or pass --fake for the offline stub.",
            file=sys.stderr,
        )
        sys.exit(2)
    return client


def main(argv: list[str] | None = None) -> int:
    # --fake is accepted either before or after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--fake", action="store_true", help="use the offline stub client"
    )
    parser = argparse.ArgumentParser(prog="speedrun_ai.pipeline", parents=[common])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in (
        "build-index",
        "generate",
        "eval",
        "emit",
        "cars-generate",
        "cars-eval",
        "cars-emit",
    ):
        sub.add_parser(name, parents=[common])
    args = parser.parse_args(argv)

    if args.cmd == "emit":
        return cmd_emit()
    if args.cmd == "cars-emit":
        return cmd_cars_emit()
    client = _client(args.fake)
    if args.cmd == "build-index":
        return cmd_build_index(client)
    if args.cmd == "generate":
        return cmd_generate(client)
    if args.cmd == "eval":
        return cmd_eval(client)
    if args.cmd == "cars-generate":
        return cmd_cars_generate(client)
    if args.cmd == "cars-eval":
        return cmd_cars_eval(client)
    return 2


if __name__ == "__main__":
    sys.exit(main())
