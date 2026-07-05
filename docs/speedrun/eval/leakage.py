#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Speedrun: the leakage check (brief §7e).

Leaked test data makes a model look smarter than it is. Our held-out gold sets
(recall queries + CARS questions) are used to *evaluate* retrieval and card
quality; the source texts are what the generator sees. If a gold item were
lifted verbatim from its source, two things would be fake:

  * the beat-a-baseline result — BM25 would win by lexical echo, and our RAG
    advantage would be an artifact of the query copying the source, not better
    semantic retrieval;
  * the eval generally — a memorised test item isn't a real test.

This script scans every gold item against the source text it is graded against
and flags any **near-copy** (a run of shared word n-grams above a pre-registered
threshold). A clean run shows the gold was genuinely paraphrased into learner
phrasing, so the eval and the baseline comparison are honest.

    just leakage
"""

from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
AI = os.path.abspath(os.path.join(HERE, "..", "ai"))

# Pre-registered: a gold item is a "near-copy" if at least this fraction of its
# word 4-grams also appear in the source text. 0.5 = half the phrasing lifted.
NGRAM = 4
LEAK_THRESHOLD = 0.5

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _ngrams(tokens: list[str], n: int) -> set[tuple[str, ...]]:
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def overlap(query: str, source: str) -> float:
    """Fraction of the query's word n-grams that also occur in the source."""
    q = _ngrams(_tokens(query), NGRAM)
    if not q:
        return 0.0
    s = _ngrams(_tokens(source), NGRAM)
    return len(q & s) / len(q)


def _load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _source_text_map(sources_json: str, source_dir: str) -> dict[str, str]:
    out: dict[str, str] = {}
    manifest = json.loads(open(sources_json, encoding="utf-8").read())
    for s in manifest:
        path = os.path.join(source_dir, s["file"])
        if os.path.isfile(path):
            out[s["name"]] = open(path, encoding="utf-8").read()
    return out


def check_track(
    name: str, gold_rows: list[dict], sources: dict[str, str], query_key: str
) -> dict:
    results = []
    for row in gold_rows:
        src = sources.get(row.get("source_name", ""), "")
        # CARS gold also carries its passage inline; check against both so a
        # question lifted from either counts.
        text = src + "\n" + str(row.get("passage", ""))
        ov = overlap(str(row.get(query_key, "")), text)
        results.append({"query": str(row.get(query_key, ""))[:80], "overlap": ov})
    overlaps = [r["overlap"] for r in results] or [0.0]
    flagged = [r for r in results if r["overlap"] >= LEAK_THRESHOLD]
    return {
        "track": name,
        "checked": len(results),
        "max_overlap": max(overlaps),
        "mean_overlap": sum(overlaps) / len(overlaps),
        "flagged": len(flagged),
        "flagged_items": [f["query"] for f in flagged],
        "clean": len(flagged) == 0,
    }


def main() -> int:
    tracks = []
    # Recall track
    recall_gold = os.path.join(AI, "gold.jsonl")
    if os.path.isfile(recall_gold):
        srcs = _source_text_map(
            os.path.join(AI, "sources.json"), os.path.join(AI, "source")
        )
        tracks.append(
            check_track("recall cards", _load_jsonl(recall_gold), srcs, "front")
        )
    # CARS track
    cars_gold = os.path.join(AI, "cars", "gold.jsonl")
    if os.path.isfile(cars_gold):
        srcs = _source_text_map(
            os.path.join(AI, "cars", "sources.json"), os.path.join(AI, "cars", "source")
        )
        tracks.append(
            check_track("CARS questions", _load_jsonl(cars_gold), srcs, "stem")
        )

    all_clean = all(t["clean"] for t in tracks)
    lines = [
        "# Speedrun — leakage check (§7e)",
        "",
        f"**Result: {'CLEAN ✅' if all_clean else 'LEAK FOUND ❌'}**",
        "",
        f"A gold item is flagged as a near-copy when ≥ {LEAK_THRESHOLD:.0%} of its "
        f"word {NGRAM}-grams also appear in the source text it is graded against "
        "(and, for CARS, its passage). Near-copies would let a keyword baseline "
        "win by lexical echo and would mean the test item leaked from the "
        "generation corpus.",
        "",
        "| track | gold items | flagged | max overlap | mean overlap | verdict |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for t in tracks:
        lines.append(
            f"| {t['track']} | {t['checked']} | {t['flagged']} | "
            f"{t['max_overlap']:.3f} | {t['mean_overlap']:.3f} | "
            f"{'clean' if t['clean'] else 'LEAK'} |"
        )
    for t in tracks:
        if t["flagged_items"]:
            lines += ["", f"**Flagged in {t['track']}:**"]
            lines += [f"- {q}" for q in t["flagged_items"]]
    lines += [
        "",
        "Low overlap confirms the gold queries are genuine paraphrases (learner "
        "phrasing), so the retrieval beat-a-baseline result and the eval are not "
        "artifacts of copied text.",
        "",
        "_Method: `docs/speedrun/eval/leakage.py` · re-run with `just leakage`._",
    ]
    report = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "leakage-report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    with open(os.path.join(HERE, "leakage.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"clean": all_clean, "tracks": tracks, "threshold": LEAK_THRESHOLD},
            f,
            indent=2,
        )
    print(report)
    return 0 if all_clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
