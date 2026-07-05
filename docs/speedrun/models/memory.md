# Memory model

**What it measures.** The probability that the student recalls a fact we have
already taught them — right now. This is the layer Anki's FSRS already does well;
we surface it honestly rather than reinventing it.

**Source & formula** (`rslib/src/scheduler/memory_score.rs`). For each card that
has an FSRS memory state, we compute the current predicted recall
(retrievability) with the same closed-form FSRS forgetting curve used by the
stats graphs:

```
R = (1 + factor · t / stability) ^ (−decay)      factor = 0.9^(1/−decay) − 1
```

where `t` = time since last review, `stability` = the card's FSRS stability, and
`decay` = the card's decay (default `FSRS5_DEFAULT_DECAY = 0.5`). The **point
estimate** for a topic (or the whole deck) is the **mean R across its cards with
state**. Cards without an FSRS state (never studied under FSRS) do not
contribute.

**Range.** Paired with a band of half-width `min(0.5, 0.5 / √graded_reviews)`
(`BAND_K = 0.5`), so ~30 reviews ≈ ±9% and ~100 ≈ ±5%. The band is clamped to
[0, 1]. Fewer reviews → wider band.

**Give-up rule.** No score is shown until there are enough graded reviews:
**≥ 20 per topic** and **≥ 60 for the deck overall** (`DEFAULT_TOPIC_MIN_REVIEWS`,
`DEFAULT_DECK_MIN_REVIEWS`; both tunable per request). Below the line the
Progress page shows "—" / "not enough data", never a fabricated number. A
graded review = a rated review that affects scheduling (cram/manual reschedules
excluded).

**Data.** FSRS stability/difficulty and last-review time per card; graded-review
counts from the revlog; topic membership from the card's `mcat::…` tag via the
same classifier the interleaving scheduler uses, so the numbers are consistent
across the app.

**Validation (brief §9 Step 1 — calibration).** We validate this model
held-out: [`../eval/calibration-report.md`](../eval/calibration-report.md)
reconstructs, for each past review, the predicted recall from the memory state
_before_ that review and compares it to the actual outcome, reporting a
reliability diagram, **Brier score**, **log loss**, and **ECE**. Held-out by
construction — a review never informs its own prediction.

**Honest limitations.**

- Retrievability is only as good as the FSRS parameters fit to the collection;
  with few reviews the estimate is noisy (hence the widening band and give-up
  rule).
- It is a **memory** number, not a score. It says nothing about whether the
  student can answer a _new_ question — that is the [performance model](performance.md).
