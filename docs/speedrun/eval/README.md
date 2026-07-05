# Speedrun — evidence & re-runnable tests

Quantitative evidence for the Sunday gate. Everything here is a **re-runnable
script** (brief §7h ethos) that regenerates its own report, so a grader can
reproduce the numbers rather than trust a screenshot.

| Evidence                                 | Script                  | One-command        | Report                                         |
| ---------------------------------------- | ----------------------- | ------------------ | ---------------------------------------------- |
| **Memory calibration** (brief §9 Step 1) | `calibration.py`        | `just calibration` | `calibration-report.md` + `calibration.svg`    |
| **Interleaving ablation** (brief §8)     | `ablation.py`           | `just ablation`    | `ablation-report.md`                           |
| **Model descriptions**                   | —                       | —                  | [`../models/`](../models/)                     |
| **AI card / retrieval eval** (§7f)       | `../../.../pipeline.py` | —                  | [`../ai/eval-report.md`](../ai/eval-report.md) |
| **CARS AI eval** (§7f, reasoning)        | `pipeline cars-eval`    | `just cars-eval`   | [`../ai/cars/`](../ai/cars/)                   |

## Memory calibration — `calibration.py`

For every past review it recovers the model's predicted recall (the FSRS
forgetting curve, with stability reconstructed from the interval the scheduler
set) and compares it to the actual pass/fail. Reports a reliability diagram,
**Brier score**, **log loss**, and **ECE**.

```
just calibration --collection "C:/Users/<you>/AppData/Roaming/Anki2/User 1/collection.anki2"
```

> **Honest hybrid — real + simulated.** A week-long project has no months-long
> review history, so the report combines the **real** reviews in your collection
> (however many — same-day study clusters near high predicted recall) with a
> clearly-**labelled simulation** of a multi-day learner that exercises the full
> 0–1 prediction range. Real and simulated are scored separately _and_ combined,
> and the chart marks real-only points (○) against the combined curve (●) — so
> nothing simulated is passed off as real. As you accumulate real multi-day
> reviews, re-run and the real share grows. Close Anki first (the collection
> locks). `--no-sim` for real-only.

## Interleaving ablation — `ablation.py`

The study-feature test: three builds (interleave **on** / **off** / **plain
Anki**), equal study time, same questions. The three study orders come from the
**real shipped scheduler** (imports `MCAT.apkg`, reads the queue under each
config); the learner is a **pre-registered simulation** whose assumptions —
including the confusability parameter `c` that is swept, with `c = 0` as the
honest null — are stated in full in the report. Reports a 3-arm table with a
range and an explicit "results that didn't work" section.

```
just ablation
```

## Honesty stance

These are the _steps of the bridge_ the brief asks us to grade (§9): the memory
model is calibrated on held-out reviews; the study feature is tested with a fair,
pre-registered method that could show no effect; and the readiness projection is
explicitly an uncalibrated mapping, never a made-up number. See
[`../models/readiness.md`](../models/readiness.md).
