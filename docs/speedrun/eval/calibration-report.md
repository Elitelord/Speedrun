# Speedrun — memory calibration report

Does the memory model's predicted recall match what actually happens? (brief §9 Step 1). Predicted recall is the shipped FSRS forgetting curve, with the model's stability reconstructed from the schedule it set.

> **Honest hybrid.** A week-long project has no months-long review history, so this combines **real** reviews (however many exist) with a **labelled simulation** that fills the prediction range same-day study can't reach. Real and simulated points are reported separately and marked on the chart (● combined line, ○ real-only points). Nothing simulated is passed off as real.

- Collection: `collection.anki2`
- Real cards scanned: 108 · real usable reviews: **0** (skipped: 18 first-of-card, 25 no-interval, 0 cram)

See `calibration.svg` for the reliability diagram.

## Scores

### Real reviews

_No reviews in this source._

### Simulated reviews

_No reviews in this source._

### Combined

_No reviews in this source._

> ⚠️ Only 0 real reviews — the real-only scores carry wide sampling error and the real points cluster at short (same-day) intervals. The combined curve leans on the simulation for the low- and mid-probability bins; treat it as a methodology demonstration until more real multi-day reviews accumulate.

## Reliability by decile (combined)

| predicted bin | n | mean predicted | observed | gap |
| --- | --- | --- | --- | --- |
| 0.0–0.1 | 0 | — | — | — |
| 0.1–0.2 | 0 | — | — | — |
| 0.2–0.3 | 0 | — | — | — |
| 0.3–0.4 | 0 | — | — | — |
| 0.4–0.5 | 0 | — | — | — |
| 0.5–0.6 | 0 | — | — | — |
| 0.6–0.7 | 0 | — | — | — |
| 0.7–0.8 | 0 | — | — | — |
| 0.8–0.9 | 0 | — | — | — |
| 0.9–1.0 | 0 | — | — | — |

A well-calibrated model tracks the diagonal (observed ≈ predicted in every bin). A consistent negative gap means over-confidence; positive means under-confidence.

_Method: `docs/speedrun/eval/calibration.py` · re-run with `just calibration`._
