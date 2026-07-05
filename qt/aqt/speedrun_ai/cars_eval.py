# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the pre-display eval gate for CARS questions (brief §7f).

Same shape as the recall-card eval, adapted to reasoning items. The classifier
under test is the CARS grounding gate: an **independent** model re-read of the
passage answers each question; the question is *shipped* if the re-read agrees
with the proposed key, else *blocked*.

We run that classifier over a hand-authored gold set of good/bad questions and
tally a 2×2 confusion matrix against a **pre-registered** ``cars-cutoff.json``.
Positive class = *bad question*; the dangerous cell is a **false negative** — a
bad question (wrong or ambiguous key) shipped as good. The cutoff caps that cell.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .eval import Confusion, load_gold

# Given (passage, stem, options) return the chosen index, or None if unanswerable.
AnswerFn = Callable[[str, str, list[str]], "int | None"]


def classify_questions(gold: list[dict[str, Any]], answer_fn: AnswerFn) -> Confusion:
    """Run the independent-re-read classifier over labelled gold questions.

    A question is *blocked* when the re-read disagrees with (or can't produce) the
    proposed key; *shipped* when it agrees. Positive class = bad question."""
    c = Confusion()
    for row in gold:
        actual_bad = row.get("label") == "bad"
        picked = answer_fn(
            row.get("passage", ""), row.get("stem", ""), list(row.get("options", []))
        )
        agrees = picked is not None and picked == row.get("answer_index")
        blocked = not agrees
        if actual_bad and blocked:
            c.tp += 1
        elif actual_bad and not blocked:
            c.fn += 1
        elif not actual_bad and blocked:
            c.fp += 1
        else:
            c.tn += 1
    return c


def run_cars_eval(
    gold: list[dict[str, Any]], answer_fn: AnswerFn, cutoff: dict[str, float]
) -> dict[str, Any]:
    confusion = classify_questions(gold, answer_fn)
    m = confusion.metrics()
    checks = {
        "accuracy": m["accuracy"] >= cutoff.get("min_accuracy", 0.0),
        "false_negative_rate": m["false_negative_rate"]
        <= cutoff.get("max_false_negative_rate", 1.0),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "cutoff": cutoff,
        "confusion": asdict(confusion),
        "card_metrics": m,
        "gold_size": len(gold),
    }


def write_report(result: dict[str, Any], path: Path) -> None:
    c = result["confusion"]
    m = result["card_metrics"]
    status = "PASS ✅" if result["passed"] else "FAIL ❌"
    lines = [
        "# Speedrun AI — CARS eval report",
        "",
        f"**Result: {status}** (measured against pre-registered `cars-cutoff.json`)",
        "",
        f"Gold set: {result['gold_size']} labelled CARS questions. The classifier "
        "is the grounding gate — an independent model re-read of the passage must "
        "agree with the answer key for a question to ship.",
        "",
        "## Answer-key correctness (2×2 confusion matrix)",
        "",
        "Positive class = *bad question* (wrong or ambiguous key). FN (a bad "
        "question shipped as good) is the dangerous cell — a wrong reasoning item "
        "is worse than none.",
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


def load_cars_gold(path: Path) -> list[dict[str, Any]]:
    return load_gold(path)
