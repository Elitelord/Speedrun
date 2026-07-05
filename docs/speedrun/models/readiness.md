# Readiness model

**What it measures.** A projected **MCAT total on the real scale (472–528)**,
always shown with a range and how much of the exam has been studied — never a
single blended "% ready".

**Source & formula** (`rslib/src/scheduler/readiness.rs`). The MCAT has four
sections, each scored **118–132**; the total is their **sum**. We map each
section's [performance](performance.md) mastery `m ∈ [0,1]` onto the section
scale:

```
section_score = SECTION_MIN + m · SECTION_SPAN        (118 + m · 14)
```

and produce `scaled_estimate / low / high` from the performance point estimate
and its band. The **projected total** is:

```
total = Σ(covered sections: section_score) + Σ(uncovered sections: neutral prior)
```

An **uncovered** section (no studied cards — including **CARS** until its cards
exist) contributes a neutral prior at the **mid of its range**, `SECTION_MID = 125`,
spanning the full `118…132`. So every unstudied section widens the total's
uncertainty band honestly instead of pretending 472 or a flattering number.

**Coverage & give-up rule.** `coverage = covered_sections / 4`. A section counts
as covered when its mastery is shown _and_ it has cards with state. We show a
projected total only at **coverage ≥ 50%** (`READINESS_MIN_COVERAGE`); below
that the Progress page shows "study more to unlock". The UI states coverage
directly ("N/4 sections studied") and the "/528" scale.

**Data.** Built on the same per-card FSRS facts and topic classifier as memory
and performance; no separate data source, so the three numbers stay consistent.

**Honest limitations (this is the automatic-fail line — read it).**

- **This is a deliberately simple, uncalibrated affine map, not a validated
  score.** We do **not** have longitudinal data (students' study history paired
  with real MCAT results), so we cannot prove that a projected 508 corresponds to
  an actual 508. Per the brief's §9, we grade the _steps of the bridge_: memory is
  calibrated ([calibration report](../eval/calibration-report.md)); the
  memory→section→total mapping is transparent and always shown with its range and
  coverage, and is explicitly **not** claimed to be accurate against real scores.
- Saying "we calibrated memory but do not yet have the data to prove the
  projected score is right" is the honest position, and the one we take here.
- The section mapping is linear (118–132) and treats sections independently; it
  does not weight sub-topics by MCAT frequency. Coverage is section-level, not
  yet against the full official content outline (the coverage-map task, §7c).
- CARS is scored from its own flashcard topic once CARS cards exist; before then
  it is an uncovered section contributing the neutral 125 prior and widening the
  band.
