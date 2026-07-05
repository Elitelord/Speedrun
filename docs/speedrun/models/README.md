# Speedrun — model descriptions

The assignment asks us to show **memory, performance, and readiness as three
separate numbers**, each with a range and a give-up rule, and never one blended
"78% ready". These are the one-page descriptions of each model as **shipped** —
formulas, data, ranges, give-up rules, and honest limitations. They describe the
Rust that actually runs (`rslib/src/scheduler/memory_score.rs`,
`rslib/src/scheduler/readiness.rs`) and the numbers the Progress page shows
(`qt/aqt/deckbrowser.py`), not an aspiration.

| Model           | One line                                                  | Page                             |
| --------------- | --------------------------------------------------------- | -------------------------------- |
| **Memory**      | Chance the student recalls a fact we already taught.      | [memory.md](memory.md)           |
| **Performance** | Chance they get a new exam-style question right.          | [performance.md](performance.md) |
| **Readiness**   | Projected MCAT total (472–528) with a range and coverage. | [readiness.md](readiness.md)     |

**Cross-cutting honesty rules (all three):**

- Every score ships with a **range**, not just a point estimate.
- Each has a **give-up rule** — below a data threshold it shows nothing
  (`shown = false`) rather than a confident-looking guess. Making up a readiness
  number is an automatic fail in the brief; we would rather show "—".
- We **do not have longitudinal practice-test data** (student study history
  paired with real MCAT scores). Per the brief's §9, we therefore grade the
  _steps of the bridge_ and are explicit about what is calibrated (memory) and
  what is an honest, uncalibrated mapping (readiness).

**Evidence backing these models:**

- Memory calibration: [`../eval/calibration-report.md`](../eval/calibration-report.md) (+ `calibration.svg`).
- Study-feature (interleaving) ablation: [`../eval/ablation-report.md`](../eval/ablation-report.md).
- AI card quality + retrieval: [`../ai/eval-report.md`](../ai/eval-report.md).
