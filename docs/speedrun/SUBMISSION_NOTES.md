# Submission notes

Copy the block below into the submission form's **Additional Notes** field. Fill
in the bracketed links + commit hash before submitting.

---

**Speedrun — an MCAT study app built on Anki.** Desktop + Android spaced-
repetition app forked from Anki (AGPL-3.0-or-later; all engine credit to the Anki
project). Exam: **MCAT** (472–528; sections 118–132).

**Core Rust change:** a topic-aware **interleaving scheduler** (plus an optional
**weakness-weighted** mode) in `rslib/src/scheduler/queue/builder/interleaving.rs`.
It is a pure queue reordering — it never changes due dates, intervals, or FSRS
memory state — so scheduling and undo are unaffected. The **three scores** are
also Rust RPCs in the shared engine. Design note + touched-files list:
`docs/speedrun/rust-change.md`.

**Shared engine, two platforms:** the same Rust engine backs both the desktop app
and the Android (AnkiDroid) app; interleaving config is collection-level and read
by both, so there is no per-platform scheduler code.

**Friday — AI added & checked; phone syncs.**

- **Grounded card generation:** cards are generated from named MCAT sources
  (OpenStax CC-BY, Wikipedia CC-BY-SA) and every output traces back to its source;
  answers not supported by the source are blocked. Pipeline + note:
  `docs/speedrun/ai/README.md`.
- **Pre-display eval gate** (`docs/speedrun/ai/eval-report.md`, **PASS**): a
  held-out gold set graded against a cutoff committed _before_ results
  (`cutoff.json`, enforced by git history). Good/bad-card 2×2 confusion matrix:
  **FN=0** (no wrong card ships), accuracy 0.972. **Beats the baseline:** embedding
  retrieval ranks the correct source first for every learner-phrased query
  (Recall@1 1.000) vs. the BM25 keyword baseline (0.944); MRR 1.000 vs 0.968.
- **Free-text production review:** the learner types an answer, an LLM grades it by
  meaning and **suggests the grade** (Again/Hard/Good/Easy), and a miss gets a
  scaffolded hint (that never reveals the answer) before a clean reveal.
- **CARS module:** grounded generation of passage + multiple-choice **reasoning**
  questions (the 4th MCAT section), gated by its own held-out eval
  (`docs/speedrun/ai/cars/cars-eval-report.md`, **PASS**, FN=0) and interleaved with
  the sciences.
- **Leakage check (§7e):** `docs/speedrun/eval/leakage-report.md` — **CLEAN**: no
  gold test item is a near-copy of its source, so the beat-a-baseline result is real.
- **AI-off invariant:** with AI disabled (or no key / network down) generation and
  grading abstain, review falls back to the native self-graded reveal, and the
  three scores still compute.
- **Two-way sync** desktop ↔ Android via Anki's own sync (AnkiWeb, or a self-hosted
  `--syncserver` — same protocol): offline review, sync on reconnect, and reviews
  keyed by millisecond timestamp + merged insert-or-ignore so none are lost or
  double-counted.
- **Three honest scores on both platforms:** Memory / Performance / Readiness, each
  with a range and a give-up rule ("not enough data"), Readiness on the 472–528
  scale — never one blended number. On Android these are the home-screen header +
  the **Progress** tab.

**Deployed Site URL note:** Speedrun is a desktop + Android application, not a web
app. The "deployed site" link is a **GitHub Release** containing the installable
artifacts (Windows `.msi` + Android `.apk`).

**Commit:** `[your latest pushed main hash]` (branch `main`).

**Verification (run against that commit):**

- Full `just check` (Rust + Python + TypeScript + format + lints): green.
- Rust core lib tests (`cargo test -p anki --lib`, incl. interleaving unit +
  integration tests): pass.
- Python suite (`just test-py`, incl. a test that calls the scheduler change): pass.
- AI + CARS subsystem tests (`qt/tests/test_speedrun_{ai,cars}.py`): pass.
- AI eval gate (`docs/speedrun/ai/eval-report.md`) + CARS eval gate
  (`docs/speedrun/ai/cars/cars-eval-report.md`): **PASS** vs pre-registered cutoffs.
- Leakage check (`just leakage`): **CLEAN**.
- Memory calibration (`just calibration`): Brier / log-loss + reliability chart.
- Interleaving ablation (`just ablation`): 3 builds, pre-registered metric.

**Every claim → its command:** `docs/speedrun/VERIFY.md`.

**Repositories:**

- Engine + desktop: [ENGINE REPO URL]
- Android app: [SPEEDRUN-ANDROID URL]
- Android backend: [SPEEDRUN-ANDROID-BACKEND URL]

---

## Field-by-field cheat sheet

| Form field        | What to put                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| Demo Video        | YouTube (Unlisted is fine) or Vimeo URL of the demo+proof video.         |
| GitHub Repository | The engine/desktop repo (`Elitelord/Speedrun`).                          |
| Deployed Site URL | The **GitHub Release** page with the `.msi` + `.apk` attached.           |
| Login credentials | Leave blank — local app, no login.                                       |
| Brainlift         | `Speedrun_Brainlift_MCAT.pdf` (the version with finalized SPOVs + DOKs). |
| Additional Notes  | The block above.                                                         |

## Making the GitHub Release (for the Deployed Site URL)

1. Attach the desktop installer `out/installer/dist/anki-26.05-win-x64.msi`
   (rebuilt from the current commit so it has the new UI + AI).
2. Attach the Android APK (`AnkiDroid-play-x86_64-debug.apk` for emulators, or an
   arm64 / signed release APK for phones).
3. Tag it (e.g. `friday-ai-sync`) and use the Release page URL as the deployed
   site link.
