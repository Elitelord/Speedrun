# Submission notes

Copy the block below into the submission form's **Additional Notes** field. Fill
in the bracketed links before submitting.

---

**Speedrun — an MCAT study app built on Anki.** Desktop + Android spaced-
repetition app forked from Anki (AGPL-3.0-or-later; all engine credit to the Anki
project). Exam: **MCAT**.

**Wednesday no-AI core** — everything runs locally, no network / no LLM / no
generated content. The app also runs and gives a score with AI disabled (AI
features are post-MVP; see POST_MVP_ROADMAP.md in the repo).

**Core Rust change:** a topic-aware **interleaving scheduler** (plus an optional
**weakness-weighted** mode) in `rslib/src/scheduler/queue/builder/interleaving.rs`.
It is a pure queue reordering — it never changes due dates, intervals, or FSRS
memory state — so scheduling and undo are unaffected. Design note:
`docs/speedrun/rust-change.md`.

**Shared engine, two platforms:** the same Rust engine backs both the desktop app
and the Android (AnkiDroid) app; the interleave toggle is collection-level config
read by both.

**Deployed Site URL note:** Speedrun is a desktop + Android application, not a web
app. The "deployed site" link is a **GitHub Release** containing the installable
artifacts (Windows `.msi` + Android `.apk`).

**Commit:** `401f76dad` (branch `main`).

**Verification (run against that commit):**

- Rust core lib tests (`cargo test -p anki --lib`): pass (exit 0).
- Python suite (`just test-py`, `pylib/tests/`): 123 passed.
- Interleaving Rust unit + integration tests + a Python test that calls the
  scheduler change: pass.
- Full `just check` (Rust + Python + TypeScript + format + lints): green.

**Repositories:**

- Engine + desktop: [ENGINE REPO URL]
- Android app: [SPEEDRUN-ANDROID URL]
- Android backend: [SPEEDRUN-ANDROID-BACKEND URL]

---

## Field-by-field cheat sheet

| Form field        | What to put                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| Demo Video        | YouTube (Unlisted is fine) or Vimeo URL of the combined demo+proof video. |
| GitHub Repository | The engine/desktop repo (`Elitelord/Speedrun`).                           |
| Deployed Site URL | The **GitHub Release** page with the `.msi` + `.apk` attached.            |
| Login credentials | Leave blank — local app, no login.                                        |
| Brainlift         | `Speedrun_Brainlift_MCAT.pdf` (the version with finalized SPOVs + DOKs).  |
| Additional Notes  | The block above.                                                          |

## Making the GitHub Release (for the Deployed Site URL)

1. Attach the desktop installer `out/installer/dist/anki-26.05-win-x64.msi`.
2. Attach the Android APK (the debug/emulator build, or a signed release APK).
3. Tag it (e.g. `mvp-wednesday`) and use the Release page URL as the deployed
   site link.
