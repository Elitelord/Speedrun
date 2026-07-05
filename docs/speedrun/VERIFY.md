# Speedrun — how to verify every claim

One page, one command per claim. Everything here is re-runnable from a clean
checkout with the built engine on the path. Where a command needs the built
Python env, use the `just` recipe (it sets `PYTHONPATH`/`PYTHONUTF8` for you) or
the raw form shown.

> Setup once: `just check` builds the engine + runs all gates. AI-eval and
> CARS-eval need `OPENAI_API_KEY` in a repo-root `.env`; everything else runs
> offline. Close the Anki app before `just check` (a running instance locks the
> Rust binding it copies).

## The Rust change (20%)

| Claim                                                                 | Command / artifact                                                                                      |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Topic-aware interleaving + weakness weighting is a real engine change | `rslib/src/scheduler/queue/builder/interleaving.rs`; design note `docs/speedrun/rust-change.md`         |
| ≥3 Rust unit tests + a Python test that calls it                      | `cargo test -p anki --lib interleaving` (5 tests); `just test-py` runs `pylib/tests/test_interleave.py` |
| Undo works / no corruption                                            | Rust tests `interleaving_keeps_undo_intact`, `interleaving_preserves_fsrs_scheduling`                   |
| Ships to the phone (shared engine)                                    | Android backend submodule points at this fork; uniform interleave runs on-device                        |

## Scores + honest uncertainty (20%)

| Claim                                                             | Command / artifact                                                                                                                                                       |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Three separate scores, each with a range + give-up rule           | Model pages `docs/speedrun/models/{memory,performance,readiness}.md`; RPCs in `rslib/src/scheduler/{memory_score,readiness}.rs`; pylib test `pylib/tests/test_scores.py` |
| Memory model is calibrated (Brier / log-loss / reliability chart) | `just calibration` → `docs/speedrun/eval/calibration-report.md` + `calibration.svg`. Hybrid real+simulated, both reported separately and labelled                        |
| Readiness is honest (no made-up number)                           | `docs/speedrun/models/readiness.md` — states it is an uncalibrated affine map with no longitudinal data; UI abstains below 50% coverage                                  |

## Study feature on learning science (15%)

| Claim                                                                    | Command / artifact                                                                                                                                                               |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Interleaving ablation: 3 builds, equal study time, pre-registered metric | `just ablation` → `docs/speedrun/eval/ablation-report.md`. Orders come from the real scheduler; learner is a labelled simulation with a confusability sweep + honest null at c=0 |

## AI checking + safety (15%)

| Claim                                                           | Command / artifact                                                                                                                                                                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Grounded generation, held-out eval, beats a baseline, FN-capped | `just cars-eval` and the recall pipeline (`python -m aqt.speedrun_ai.pipeline eval`) → `docs/speedrun/ai/eval-report.md` (PASS), `docs/speedrun/ai/cars/cars-eval-report.md` (PASS) vs pre-registered `cutoff.json` |
| 2×2 good/bad confusion matrix, false-negative cell capped       | both eval reports (recall: FN=0; CARS: FN=0)                                                                                                                                                                        |
| No leaked test data                                             | `just leakage` → `docs/speedrun/eval/leakage-report.md` (CLEAN — max n-gram overlap 0.24)                                                                                                                           |
| AI-off invariant (still gives a score)                          | `qt/tests/test_speedrun_ai.py` (AI-off path); disable AI in Settings and the three scores + review still work                                                                                                       |

## Re-runnable tests (12%)

| Claim                      | Command                                                                                                                      |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Full build + lints + tests | `just check`                                                                                                                 |
| Rust / Python / TS suites  | `just test-rust` · `just test-py` · `just test-ts`                                                                           |
| Speedrun tests             | `pylib/tests/{test_interleave,test_scores}.py`, `qt/tests/{test_speedrun_ai,test_speedrun_cars,test_reviewer_production}.py` |
| Every eval is one command  | `just calibration` · `just ablation` · `just cars-eval` · `just leakage`                                                     |

## One engine, two apps, sync (10%)

| Claim                                        | Command / artifact                                                                                               |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Shared Rust engine on desktop + Android      | Android app repo builds `rsdroid` from this `rslib`                                                              |
| Two-way sync, no lost/double-counted reviews | via Anki's own sync (AnkiWeb or self-hosted `--syncserver`); steps in `docs/speedrun/SYNC.md`; shown in the demo |

## Product / UX (8%)

| Claim                                                       | Artifact                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| In-window app shell, Progress page, free-text grading, CARS | `just run`; deck browser + reviewer; import `docs/speedrun/seed-deck/MCAT.apkg` (108 cards, 4 sections incl. CARS) |

## What changed since the MVP (for the demo)

- **CARS module** — grounded passage + multiple-choice reasoning generation, its own eval gate, custom notetype, wired as the 4th MCAT section.
- **Free-text grading upgrades** — AI now suggests the grade (Again/Hard/Good/Easy), feedback never leaks the answer, reveal shows the answer cleanly (no char-diff), feedback card + suggested-grade pill, larger grade/ease buttons, top progress bar.
- **Evidence** — calibration (hybrid), interleaving ablation, leakage check, CARS eval, all one-command.
- **Interleaver** — untouched topics get a fair share so new sections ingest; deck-level score give-up lowered to 60.
