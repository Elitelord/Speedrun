# Performance model

**What it measures.** The probability that the student gets a **new, exam-style
question right** — including ones they have never seen — as opposed to merely
recalling a memorized card. This is the bridge from memory to a score.

**Source & formula** (`rslib/src/scheduler/readiness.rs`, `performance_value`).
For each card with an FSRS state:

```
value = R · (1 − PERF_DIFFICULTY_WEIGHT · clamp((difficulty − 1) / 9, 0, 1))
```

where `R` is the FSRS retrievability (same as the [memory model](memory.md)),
`difficulty` is the card's FSRS difficulty (1–10), and
`PERF_DIFFICULTY_WEIGHT = 0.4`. Intuition: a fact you recall but find _hard_
transfers less reliably to a reworded question than one you find _easy_, so
difficulty discounts recall. At maximum difficulty a card keeps `1 − 0.4 = 0.6`
of its retrievability; at minimum difficulty it keeps all of it. The topic/deck
estimate is the **mean value across cards with state**.

**Range & give-up rule.** Identical machinery to the memory model: band
half-width `min(0.5, 0.5 / √graded_reviews)`; shown only at **≥ 20 graded
reviews per topic** / **≥ 60 for the deck**. Below the line: "not enough data".

**Data.** Same gathered card facts as memory (retrievability + difficulty +
graded counts + topic tag), computed in one shared pass so memory and
performance never disagree about which cards exist.

**Honest limitations (important).**

- This is a **memory-derived proxy**, not yet a model trained on held-out
  exam-style questions. It discounts recall by difficulty, but it does not (yet)
  incorporate item difficulty of _unseen_ questions, timing, or a trained
  transfer model.
- **Paraphrase gap (brief §7d) not yet measured.** The real test of a performance
  model is that recall on a card and accuracy on 2 reworded exam-style questions
  for that card _differ_ — if they're identical, performance is just copying
  memory. We have not yet run the 30-card × 2-question paraphrase study, so we do
  **not** claim performance is distinct from memory beyond the difficulty
  discount. This is the honest next step, called out in the roadmap.
- Because it shares FSRS inputs with memory, the two numbers are correlated by
  construction; treat the current performance number as "memory, difficulty-
  adjusted", not an independent question-answering predictor.
