#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Speedrun: memory-model calibration harness (brief §9 Step 1).

Answers the question the assignment asks of the memory model: *when it says 80%,
does the student actually recall about 80% of the time?* For each graded review
we recover the model's predicted recall at that moment and compare it to what
actually happened (pass vs. Again), then bin predictions, measure observed recall
per bin, and report **Brier score**, **log loss**, and **expected calibration
error (ECE)** plus a reliability diagram.

Predicted recall uses the exact closed-form FSRS forgetting curve the app ships
(rslib/src/scheduler/memory_score.rs -> fsrs::current_retrievability):

    R = (1 + factor * delta_t / stability) ** (-decay)   factor = 0.9**(1/-decay) - 1

The model's stability at a review is **reconstructed from the schedule**, not read
from the log: FSRS set the previous interval so that predicted recall would equal
the card's desired retention at the due date, so
``stability = factor * scheduled_interval / (desired_retention**(-1/decay) - 1)``.
(This works even though Anki does not store per-review memory state in the revlog,
and matches what the scheduler intended.)

## Real + simulated (honest hybrid)

A one-week project cannot gather months of longitudinal reviews. So the report
combines two clearly-separated sources:

* **REAL** — the graded reviews in the collection you pass. As many as you have;
  same-day study gives short intervals (predictions cluster near 1.0), so real
  data alone rarely fills the low-probability bins.
* **SIMULATED** — a synthetic learner over a multi-day schedule, used to exercise
  the full 0..1 prediction range the real same-day data can't reach. The learner's
  true forgetting is deliberately a bit faster than the model assumes, so the
  chart shows a *realistic, detectable* miscalibration rather than a rigged fit.

Both are reported on their own AND combined, always labelled, so nothing is
passed off as more than it is (brief: honest numbers over flattering ones).

Usage:

    just calibration --collection "C:/Users/<you>/AppData/Roaming/Anki2/User 1/collection.anki2"
    just calibration                     # auto-detect profile; simulation still runs
    just calibration --no-sim            # real reviews only
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import sys
import tempfile

from anki.collection import Collection
from anki.consts import REVLOG_CRAM

# FSRS-5 default decay; matches card.decay.unwrap_or(FSRS5_DEFAULT_DECAY) in Rust.
FSRS5_DEFAULT_DECAY = 0.5
DEFAULT_DESIRED_RETENTION = 0.9

NUM_BINS = 10
HERE = os.path.dirname(os.path.abspath(__file__))


def forgetting_curve(delta_t_days: float, stability: float, decay: float) -> float:
    """FSRS predicted recall after ``delta_t_days`` at the given stability."""
    if stability <= 0:
        return 0.0
    factor = 0.9 ** (1.0 / -decay) - 1.0
    return (1.0 + factor * delta_t_days / stability) ** (-decay)


def implied_stability(scheduled_days: float, decay: float, retention: float) -> float:
    """Stability the scheduler implied when it set ``scheduled_days`` as the gap,
    i.e. the S for which recall equals ``retention`` at the due date."""
    factor = 0.9 ** (1.0 / -decay) - 1.0
    denom = retention ** (-1.0 / decay) - 1.0
    if denom <= 0 or scheduled_days <= 0:
        return 0.0
    return factor * scheduled_days / denom


# -- real reviews ----------------------------------------------------------


def find_default_collection() -> str | None:
    candidates = []
    if os.environ.get("APPDATA"):
        candidates.append(os.path.join(os.environ["APPDATA"], "Anki2"))
    candidates.append(os.path.expanduser("~/.local/share/Anki2"))
    candidates.append(os.path.expanduser("~/Library/Application Support/Anki2"))
    for base in candidates:
        if not os.path.isdir(base):
            continue
        for entry in sorted(os.listdir(base)):
            if entry in ("addons21", "prefs21.db"):
                continue
            path = os.path.join(base, entry, "collection.anki2")
            if os.path.isfile(path):
                return path
    return None


def collect_real(col: Collection) -> tuple[list[tuple[float, int]], dict]:
    """(predicted_recall, actual_pass) for every graded review with a scheduled
    prior interval to reconstruct the model's prediction from."""
    pairs: list[tuple[float, int]] = []
    skipped_first = skipped_no_ivl = skipped_cram = cards_seen = 0

    for cid in col.find_cards(""):
        card = col.get_card(cid)
        decay = card.decay if card.decay else FSRS5_DEFAULT_DECAY
        retention = card.desired_retention or DEFAULT_DESIRED_RETENTION
        entries = list(col.get_review_logs(cid))
        cards_seen += 1
        prev = None
        for entry in entries:
            if entry.button_chosen == 0:
                continue
            if entry.review_kind == REVLOG_CRAM:
                skipped_cram += 1
                prev = entry
                continue
            if prev is None:
                skipped_first += 1
                prev = entry
                continue
            # prev.interval (seconds) = the gap the scheduler set until this review.
            scheduled_days = prev.interval / 86400.0
            delta_days = (entry.time - prev.time) / 1000.0 / 86400.0
            if scheduled_days <= 0 or delta_days < 0:
                skipped_no_ivl += 1
                prev = entry
                continue
            if prev.HasField("memory_state") and prev.memory_state.stability > 0:
                stability = prev.memory_state.stability
            else:
                stability = implied_stability(scheduled_days, decay, retention)
            if stability <= 0:
                skipped_no_ivl += 1
                prev = entry
                continue
            pred = forgetting_curve(delta_days, stability, decay)
            pairs.append((pred, 1 if entry.button_chosen > 1 else 0))
            prev = entry

    diag = {
        "cards_seen": cards_seen,
        "usable_reviews": len(pairs),
        "skipped_first_review": skipped_first,
        "skipped_no_interval": skipped_no_ivl,
        "skipped_cram": skipped_cram,
    }
    return pairs, diag


# -- simulated reviews -----------------------------------------------------


def simulate(n_reviews: int, seed: int) -> list[tuple[float, int]]:
    """Synthetic multi-day study: the model predicts recall from the schedule it
    set; the learner's TRUE stability is a bit lower (forgets faster), so the
    model is mildly over-confident — a realistic, detectable miscalibration.

    Returns (model_predicted_recall, actual_outcome) pairs spanning 0..1."""
    rng = random.Random(seed)
    decay = FSRS5_DEFAULT_DECAY
    factor = 0.9 ** (1.0 / -decay) - 1.0
    pairs: list[tuple[float, int]] = []
    for _ in range(n_reviews):
        # Draw the model's predicted recall uniformly so every bin is exercised,
        # and back out the elapsed/stability ratio that produces it.
        predicted = rng.uniform(0.30, 0.995)
        ratio = (predicted ** (-1.0 / decay) - 1.0) / factor  # = elapsed / stability
        # The learner's true stability is a bit lower (forgets faster), so at the
        # same elapsed gap the true recall is below the prediction -> mild,
        # realistic over-confidence the chart should reveal.
        shrink = rng.uniform(0.7, 0.95)
        true_recall = (1.0 + factor * ratio / shrink) ** (-decay)
        outcome = 1 if rng.random() < true_recall else 0
        pairs.append((predicted, outcome))
    return pairs


# -- metrics ---------------------------------------------------------------


def bin_stats(pairs: list[tuple[float, int]]) -> list[dict]:
    bins = []
    for b in range(NUM_BINS):
        lo, hi = b / NUM_BINS, (b + 1) / NUM_BINS
        members = [
            (p, y) for (p, y) in pairs if p >= lo and (p < hi or b == NUM_BINS - 1)
        ]
        n = len(members)
        if n == 0:
            bins.append(
                {"lo": lo, "hi": hi, "n": 0, "mean_pred": None, "observed": None}
            )
        else:
            bins.append(
                {
                    "lo": lo,
                    "hi": hi,
                    "n": n,
                    "mean_pred": sum(p for p, _ in members) / n,
                    "observed": sum(y for _, y in members) / n,
                }
            )
    return bins


def metrics(pairs: list[tuple[float, int]], bins: list[dict]) -> dict:
    n = len(pairs)
    if n == 0:
        return {"n": 0, "brier": None, "log_loss": None, "ece": None, "base_rate": None}
    brier = sum((p - y) ** 2 for p, y in pairs) / n
    eps = 1e-15
    log_loss = (
        -sum(
            y * math.log(min(max(p, eps), 1 - eps))
            + (1 - y) * math.log(min(max(1 - p, eps), 1 - eps))
            for p, y in pairs
        )
        / n
    )
    ece = sum(
        (b["n"] / n) * abs(b["mean_pred"] - b["observed"]) for b in bins if b["n"] > 0
    )
    return {
        "n": n,
        "brier": brier,
        "log_loss": log_loss,
        "ece": ece,
        "base_rate": sum(y for _, y in pairs) / n,
    }


# -- rendering -------------------------------------------------------------


def render_svg(bins_combined: list[dict], bins_real: list[dict]) -> str:
    W = H = 360
    pad = 44
    plot = W - 2 * pad

    def px(v: float) -> float:
        return pad + v * plot

    def py(v: float) -> float:
        return H - pad - v * plot

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="11">',
        f'<rect width="{W}" height="{H}" fill="white"/>',
        f'<line x1="{pad}" y1="{H - pad}" x2="{W - pad}" y2="{H - pad}" stroke="#333"/>',
        f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{H - pad}" stroke="#333"/>',
        f'<line x1="{px(0)}" y1="{py(0)}" x2="{px(1)}" y2="{py(1)}" '
        'stroke="#bbb" stroke-dasharray="4 3"/>',
        f'<text x="{W / 2}" y="{H - 8}" text-anchor="middle">predicted recall</text>',
        f'<text x="12" y="{H / 2}" text-anchor="middle" '
        f'transform="rotate(-90 12 {H / 2})">observed recall</text>',
    ]
    for tick in (0.0, 0.5, 1.0):
        parts.append(
            f'<text x="{px(tick)}" y="{H - pad + 16}" text-anchor="middle" '
            f'fill="#666">{tick:.1f}</text>'
        )
        parts.append(
            f'<text x="{pad - 8}" y="{py(tick) + 4}" text-anchor="end" '
            f'fill="#666">{tick:.1f}</text>'
        )
    combined = [b for b in bins_combined if b["n"] > 0]
    if len(combined) >= 2:
        poly = " ".join(f"{px(b['mean_pred'])},{py(b['observed'])}" for b in combined)
        parts.append(f'<polyline points="{poly}" fill="none" stroke="#2b6cb0"/>')
    mx = max((b["n"] for b in combined), default=1)
    for b in combined:
        r = 3 + 6 * (b["n"] / mx)
        parts.append(
            f'<circle cx="{px(b["mean_pred"])}" cy="{py(b["observed"])}" '
            f'r="{r:.1f}" fill="#2b6cb0" fill-opacity="0.55"/>'
        )
    for b in (x for x in bins_real if x["n"] > 0):
        parts.append(
            f'<circle cx="{px(b["mean_pred"])}" cy="{py(b["observed"])}" '
            f'r="4" fill="none" stroke="#e07a1f" stroke-width="2"/>'
        )
    parts.append(
        f'<text x="{W - pad}" y="{pad}" text-anchor="end" fill="#2b6cb0">'
        "● combined</text>"
    )
    parts.append(
        f'<text x="{W - pad}" y="{pad + 15}" text-anchor="end" fill="#e07a1f">'
        "○ real only</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def _scores_block(title: str, m: dict) -> list[str]:
    if not m["n"]:
        return [f"### {title}", "", "_No reviews in this source._", ""]
    return [
        f"### {title} — N = {m['n']}",
        "",
        f"- Brier: **{m['brier']:.4f}** · log loss: **{m['log_loss']:.4f}** · "
        f"ECE: **{m['ece']:.4f}** · base recall: {m['base_rate']:.3f}",
        "",
    ]


def _bin_table(bins: list[dict]) -> list[str]:
    rows = [
        "| predicted bin | n | mean predicted | observed | gap |",
        "| --- | --- | --- | --- | --- |",
    ]
    for b in bins:
        if b["n"] == 0:
            rows.append(f"| {b['lo']:.1f}–{b['hi']:.1f} | 0 | — | — | — |")
        else:
            rows.append(
                f"| {b['lo']:.1f}–{b['hi']:.1f} | {b['n']} | {b['mean_pred']:.3f} | "
                f"{b['observed']:.3f} | {b['observed'] - b['mean_pred']:+.3f} |"
            )
    return rows


def render_report(
    real_m: dict,
    sim_m: dict,
    comb_m: dict,
    comb_bins: list[dict],
    diag: dict,
    collection: str | None,
) -> str:
    lines = [
        "# Speedrun — memory calibration report",
        "",
        "Does the memory model's predicted recall match what actually happens? "
        "(brief §9 Step 1). Predicted recall is the shipped FSRS forgetting curve, "
        "with the model's stability reconstructed from the schedule it set.",
        "",
        "> **Honest hybrid.** A week-long project has no months-long review history, "
        "so this combines **real** reviews (however many exist) with a **labelled "
        "simulation** that fills the prediction range same-day study can't reach. "
        "Real and simulated points are reported separately and marked on the chart "
        "(● combined line, ○ real-only points). Nothing simulated is passed off as "
        "real.",
        "",
        f"- Collection: `{os.path.basename(collection)}`"
        if collection
        else "- Collection: (none)",
        f"- Real cards scanned: {diag['cards_seen']} · real usable reviews: "
        f"**{diag['usable_reviews']}** (skipped: {diag['skipped_first_review']} first-of-card, "
        f"{diag['skipped_no_interval']} no-interval, {diag['skipped_cram']} cram)",
        "",
        "See `calibration.svg` for the reliability diagram.",
        "",
        "## Scores",
        "",
    ]
    lines += _scores_block("Real reviews", real_m)
    lines += _scores_block("Simulated reviews", sim_m)
    lines += _scores_block("Combined", comb_m)
    if diag["usable_reviews"] < 50:
        lines += [
            f"> ⚠️ Only {diag['usable_reviews']} real reviews — the real-only scores "
            "carry wide sampling error and the real points cluster at short (same-day) "
            "intervals. The combined curve leans on the simulation for the low- and "
            "mid-probability bins; treat it as a methodology demonstration until more "
            "real multi-day reviews accumulate.",
            "",
        ]
    lines += ["## Reliability by decile (combined)", ""]
    lines += _bin_table(comb_bins)
    lines += [
        "",
        "A well-calibrated model tracks the diagonal (observed ≈ predicted in every "
        "bin). A consistent negative gap means over-confidence; positive means "
        "under-confidence.",
        "",
        "_Method: `docs/speedrun/eval/calibration.py` · re-run with `just calibration`._",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Speedrun memory calibration harness")
    ap.add_argument(
        "--collection", help="path to a collection.anki2 with review history"
    )
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument(
        "--sim-reviews", type=int, default=2000, help="simulated reviews (0 to disable)"
    )
    ap.add_argument("--no-sim", action="store_true", help="real reviews only")
    ap.add_argument("--seed", type=int, default=12345)
    args = ap.parse_args()

    collection = args.collection or find_default_collection()
    real_pairs: list[tuple[float, int]] = []
    diag = {
        "cards_seen": 0,
        "usable_reviews": 0,
        "skipped_first_review": 0,
        "skipped_no_interval": 0,
        "skipped_cram": 0,
    }
    if collection and os.path.isfile(collection):
        tmpdir = tempfile.mkdtemp()
        work = os.path.join(tmpdir, "collection.anki2")
        shutil.copy(collection, work)
        # Copy the WAL/SHM sidecars too: while Anki is open, recent reviews live
        # in collection.anki2-wal and aren't in the main db yet. Matching the
        # names lets SQLite replay them so we see the latest study.
        for suffix in ("-wal", "-shm"):
            side = collection + suffix
            if os.path.isfile(side):
                shutil.copy(side, work + suffix)
        col = Collection(work)
        try:
            real_pairs, diag = collect_real(col)
        finally:
            col.close()
    else:
        print("note: no collection found; running simulation only.", file=sys.stderr)
        collection = None

    sim_pairs = (
        []
        if args.no_sim or args.sim_reviews <= 0
        else simulate(args.sim_reviews, args.seed)
    )
    combined = real_pairs + sim_pairs

    real_m = metrics(real_pairs, bin_stats(real_pairs))
    sim_m = metrics(sim_pairs, bin_stats(sim_pairs))
    comb_bins = bin_stats(combined)
    comb_m = metrics(combined, comb_bins)

    os.makedirs(args.out_dir, exist_ok=True)
    report = render_report(real_m, sim_m, comb_m, comb_bins, diag, collection)
    with open(
        os.path.join(args.out_dir, "calibration-report.md"), "w", encoding="utf-8"
    ) as f:
        f.write(report)
    with open(
        os.path.join(args.out_dir, "calibration.svg"), "w", encoding="utf-8"
    ) as f:
        f.write(render_svg(comb_bins, bin_stats(real_pairs)))
    with open(
        os.path.join(args.out_dir, "calibration.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(
            {
                "real": real_m,
                "simulated": sim_m,
                "combined": comb_m,
                "diagnostics": diag,
            },
            f,
            indent=2,
        )
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
