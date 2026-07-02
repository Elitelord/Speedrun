# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the pre-display evaluation gate.

Two things are measured against a *pre-registered* ``cutoff.json`` (committed
before any results are seen — git history is the enforcement):

1. **Beat-a-baseline** — retrieval Recall@k / MRR for the embedding RAG path vs.
   the BM25 keyword baseline on a held-out gold set. The AI path must beat the
   baseline by a pre-registered margin.
2. **Good/bad card classifier** — a 2x2 confusion matrix over generated cards.
   Positive = "bad card" (the thing we must catch). The dangerous cell is a
   **false negative**: a wrong card shipped as good. The cutoff caps that cell
   explicitly.

The run writes a human report + a machine-checkable result; a failing run makes
the pipeline refuse to emit cards and exit non-zero.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .generate import is_grounded
from .rag import Retrieved

# A retriever is anything that maps a query to a ranked list of chunks.
Retriever = Callable[[str], list[Retrieved]]


def load_gold(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _target_hit(row: dict[str, Any], hits: list[Retrieved]) -> int:
    """1-based rank of the first retrieved chunk matching the gold row's target
    (chunk_id if present, else source_name), or 0 if not retrieved."""
    for rank, h in enumerate(hits, start=1):
        if row.get("chunk_id") and h.chunk_id == row["chunk_id"]:
            return rank
        if not row.get("chunk_id") and h.source_name == row.get("source_name"):
            return rank
    return 0


def recall_and_mrr(
    gold: list[dict[str, Any]], retriever: Retriever
) -> tuple[float, float]:
    if not gold:
        return 0.0, 0.0
    hits = 0
    rr_sum = 0.0
    for row in gold:
        rank = _target_hit(row, retriever(row["front"]))
        if rank:
            hits += 1
            rr_sum += 1.0 / rank
    n = len(gold)
    return hits / n, rr_sum / n


@dataclass
class Confusion:
    # positive class = "bad card"
    tp: int = 0  # bad & blocked (correct)
    fp: int = 0  # good & blocked (lost content)
    tn: int = 0  # good & shipped (correct)
    fn: int = 0  # bad & shipped  (DANGEROUS: wrong fact ships)

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    def metrics(self) -> dict[str, float]:
        total = self.total or 1
        actual_bad = self.tp + self.fn or 1
        shipped = self.tn + self.fn or 1
        predicted_block = self.tp + self.fp or 1
        return {
            "accuracy": (self.tp + self.tn) / total,
            "false_negative_rate": self.fn / actual_bad,
            "wrong_answer_rate": self.fn / shipped,
            "precision": self.tp / predicted_block,
            "recall": self.tp / actual_bad,
        }


def classify_cards(gold: list[dict[str, Any]], index: dict[str, Any]) -> Confusion:
    """Run the grounding gate (the accept/reject classifier) over labelled gold
    cards and tally the confusion matrix. A card is *blocked* when its answer is
    not grounded in its named source (all that source's chunks concatenated), so
    the check is robust to how the source was chunked."""
    source_text: dict[str, str] = {}
    for e in index.get("entries", []):
        source_text[e["source_name"]] = (
            source_text.get(e["source_name"], "") + "\n" + e["text"]
        )
    c = Confusion()
    for row in gold:
        actual_bad = row.get("label") == "bad"
        source = source_text.get(row.get("source_name", ""), "")
        blocked = not is_grounded(row.get("back", ""), source)
        if actual_bad and blocked:
            c.tp += 1
        elif actual_bad and not blocked:
            c.fn += 1
        elif not actual_bad and blocked:
            c.fp += 1
        else:
            c.tn += 1
    return c


def run_eval(
    gold: list[dict[str, Any]],
    index: dict[str, Any],
    cutoff: dict[str, float],
    rag_retriever: Retriever,
    bm25_retriever: Retriever | None,
) -> dict[str, Any]:
    rag_recall, rag_mrr = recall_and_mrr(gold, rag_retriever)
    if bm25_retriever is not None:
        bm25_recall, bm25_mrr = recall_and_mrr(gold, bm25_retriever)
    else:
        bm25_recall, bm25_mrr = 0.0, 0.0
    confusion = classify_cards(gold, index)
    m = confusion.metrics()

    checks = {
        "accuracy": m["accuracy"] >= cutoff.get("min_accuracy", 0.0),
        "false_negative_rate": m["false_negative_rate"]
        <= cutoff.get("max_false_negative_rate", 1.0),
        "recall_at_k": rag_recall >= cutoff.get("min_recall_at_5", 0.0),
        "beats_baseline": (rag_recall - bm25_recall)
        >= cutoff.get("min_rag_minus_bm25_recall", 0.0),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "cutoff": cutoff,
        "retrieval": {
            "rag_recall": rag_recall,
            "rag_mrr": rag_mrr,
            "bm25_recall": bm25_recall,
            "bm25_mrr": bm25_mrr,
            "rag_minus_bm25_recall": rag_recall - bm25_recall,
        },
        "confusion": asdict(confusion),
        "card_metrics": m,
    }


def write_report(result: dict[str, Any], path: Path) -> None:
    r = result["retrieval"]
    c = result["confusion"]
    m = result["card_metrics"]
    status = "PASS ✅" if result["passed"] else "FAIL ❌"
    lines = [
        "# Speedrun AI — eval report",
        "",
        f"**Result: {status}** (measured against pre-registered `cutoff.json`)",
        "",
        "## Beat-a-baseline (retrieval)",
        "",
        "| Retriever | Recall@k | MRR |",
        "| --- | --- | --- |",
        f"| RAG (embeddings) | {r['rag_recall']:.3f} | {r['rag_mrr']:.3f} |",
        f"| BM25 (keyword baseline) | {r['bm25_recall']:.3f} | {r['bm25_mrr']:.3f} |",
        f"| **RAG − BM25 recall** | **{r['rag_minus_bm25_recall']:+.3f}** | |",
        "",
        "## Good/bad card classifier (2×2 confusion matrix)",
        "",
        "Positive class = *bad card*. FN (bad card shipped as good) is the "
        "dangerous cell.",
        "",
        "| | predicted block | predicted ship |",
        "| --- | --- | --- |",
        f"| **actually bad** | TP={c['tp']} | FN={c['fn']} |",
        f"| **actually good** | FP={c['fp']} | TN={c['tn']} |",
        "",
        f"- accuracy: {m['accuracy']:.3f}",
        f"- false-negative rate: {m['false_negative_rate']:.3f}",
        f"- wrong-answer rate (of shipped): {m['wrong_answer_rate']:.3f}",
        f"- precision: {m['precision']:.3f} · recall: {m['recall']:.3f}",
        "",
        "## Cutoff checks",
        "",
    ]
    for name, ok in result["checks"].items():
        lines.append(f"- {'✅' if ok else '❌'} {name}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
