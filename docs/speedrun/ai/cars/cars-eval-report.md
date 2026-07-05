# Speedrun AI — CARS eval report

**Result: PASS ✅** (measured against pre-registered `cars-cutoff.json`)

Gold set: 12 labelled CARS questions. The classifier is the grounding gate — an independent model re-read of the passage must agree with the answer key for a question to ship.

## Answer-key correctness (2×2 confusion matrix)

Positive class = *bad question* (wrong or ambiguous key). FN (a bad question shipped as good) is the dangerous cell — a wrong reasoning item is worse than none.

| | predicted block | predicted ship |
| --- | --- | --- |
| **actually bad** | TP=4 | FN=0 |
| **actually good** | FP=0 | TN=8 |

- accuracy: 1.000
- false-negative rate: 0.000
- wrong-answer rate (of shipped): 0.000
- precision: 1.000 · recall: 1.000

## Cutoff checks

- ✅ accuracy
- ✅ false_negative_rate
