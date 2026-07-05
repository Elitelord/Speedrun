# Speedrun — interleaving ablation (study-feature test, brief §8)

> **SIMULATION — assumptions stated in full.** The three study *orders* come from the real shipped scheduler; the *learner* is a stated model. We have no real learners by the deadline, so this is a fair test that *could* show no effect — not a claim that it definitely works.

## Pre-registered before results

- **Hypothesis:** interleaving related MCAT topics raises accuracy on new mixed-topic questions at equal study trials, vs. blocked practice and vs. plain Anki.
- **Primary metric:** mean accuracy on a held-out set of mixed-topic questions after equal study trials (3 whole passes over the deck).
- **Confusability c** (how much a question depends on telling related topics apart) is unknown without real learners, so it is **swept**; c=0 is the honest null where order cannot matter.

## The three builds (orders from the real scheduler)

Deck: 96 cards across 3 studied topics. Topic-switch rate = fraction of consecutive study trials that change topic (the mechanism interleaving drives):

| build | topic-switch rate |
| --- | --- |
| full app (interleave ON) | 1.000 |
| ablation (interleave OFF) | 0.021 |
| plain Anki (baseline) | 0.021 |

> **Note (a real finding):** the *ablation* and *plain Anki* orders are **identical**. Interleaving is our *only* scheduler change, so turning it off returns the exact upstream Anki queue. This cleanly isolates the feature — any difference below is attributable to interleaving alone.

## Result at the headline confusability (c = 0.5)

| build | mean accuracy | 10–90% range |
| --- | --- | --- |
| full app (interleave ON) | 0.603 | 0.530–0.670 |
| ablation (interleave OFF) | 0.335 | 0.275–0.380 |
| plain Anki (baseline) | 0.335 | 0.275–0.380 |

## Confusability sweep (where the effect appears — and vanishes)

| c | ON | OFF | plain | ON − OFF |
| --- | --- | --- | --- | --- |
| 0.0 | 0.639 | 0.639 | 0.639 | +0.000 |
| 0.2 | 0.634 | 0.526 | 0.526 | +0.108 |
| 0.4 | 0.625 | 0.404 | 0.404 | +0.221 |
| 0.6 | 0.599 | 0.275 | 0.275 | +0.324 |
| 0.8 | 0.573 | 0.136 | 0.136 | +0.438 |

## Honest reporting — results that did not work / caveats

- **At c = 0 the effect is exactly zero** (ON = OFF = plain). If mixed-topic questions don't require discriminating confusable topics, interleaving buys nothing here — a genuine null the metric was designed to be able to show.
- The **magnitude depends entirely on the assumed confusability c**, which we cannot estimate without real students taking mixed-topic tests. We report the sweep rather than pick a flattering c.
- Per-card mastery is identical across arms by construction (same cards, same passes), so this measures *only* the ordering effect — not more reviews or better cards.
- This is a simulation. The real test (same learners, same questions, same time, on all three builds) is future work; see the model-description pages.

_Method: `docs/speedrun/eval/ablation.py`. Re-run with `just ablation`._
