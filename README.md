# Speedrun — an MCAT study app built on Anki

> **Exam: MCAT** (Medical College Admission Test). Speedrun is a desktop **and**
> Android spaced-repetition study app that adapts Anki's proven engine for MCAT
> prep: it **interleaves** the three science sections the way the real exam mixes
> them, can **weight study toward your measured-weak topics**, and reports an
> **honest memory score** that shows its own uncertainty instead of a fake number.

This is a fork of **[Anki](https://apps.ankiweb.net)** by Ankitects Pty Ltd.
Anki is a spaced repetition flashcard program; all credit for the underlying
engine, apps, and FSRS scheduler goes to the Anki project and its contributors.
See **[Attribution & License](#attribution--license)**.

## What's new in this fork (the MCAT layer)

All of the following ships in the **no-AI core** — everything runs locally, with
no network calls, no LLM, no generated content:

- **Topic-aware interleaving scheduler** (the core Rust change). Reorders the
  study queue into a round-robin across MCAT topic tags
  (`mcat::biobiochem`, `mcat::chemphys`, `mcat::psychsoc`) so a session mixes
  sections like the exam does. It is a **pure reordering** — it never mutates
  due dates, intervals, or FSRS memory state, so scheduling correctness and undo
  are unaffected. See the design note: **[docs/speedrun/rust-change.md](./docs/speedrun/rust-change.md)**.
- **Weakness-weighted interleaving.** Optionally weights the round-robin by
  measured weakness (`1 − mean FSRS recall`) so shakier topics surface more
  often.
- **Honest memory score.** Mean FSRS predicted recall per topic, always paired
  with an uncertainty band and a "give-up rule" that shows _"Not enough data
  yet"_ below a review threshold rather than a confident-looking guess.
- **Shared engine, two platforms.** The scheduler change lives in the core Rust
  engine with config at the **collection** level, so the desktop app and the
  Android app (built from the same engine) behave identically — no per-platform
  scheduler code.
- **Seed MCAT deck** (`docs/speedrun/seed-deck/MCAT.apkg`) tagged by section.

## Architecture

Anki (and therefore Speedrun) is multi-layered:

- **Core Rust engine** — `rslib/` (the MCAT scheduler change is in
  `rslib/src/scheduler/queue/builder/interleaving.rs` + `.../memory_score.rs`).
- **PyO3 bridge** — `pylib/rsbridge/` exposes the Rust API to Python.
- **Python library + PyQt desktop app** — `pylib/anki/`, `qt/aqt/`.
- **Svelte / TypeScript web frontend** — `ts/` (the memory dashboard is
  `ts/routes/memory-dashboard/`).
- **Protobuf IPC** — `proto/` defines the API between layers.
- **Android** — a separate AnkiDroid-based fork whose backend is compiled from
  this same Rust engine (see below).

## Building & running

Everything is wrapped in `just` recipes (run `just --list` to see them all):

```bash
just run       # build pylib + qt and launch the desktop app
just check     # format + full build & checks (Rust, Python, TS)
just test-rust # Rust tests   (includes the interleaving unit/integration tests)
just test-py   # Python tests (includes pylib/tests/test_interleave.py)
```

The desktop app requires a normal Anki dev toolchain; the build system downloads
its own dependencies. For a packaged desktop build, the Windows installer is
produced under `out/installer/dist/`.

### Android

The Android app is maintained in two companion repositories (AnkiDroid-based):

- **`Speedrun-Android`** — the app (wires `local_backend`, points
  `BackendDependencies.kt` at the backend, adds the on-device interleave toggle).
- **`Speedrun-Android-Backend`** — builds the Rust `.aar` backend from this
  fork; its `anki` submodule pins the engine commit used for the build.

Build the backend `.aar` from this engine, then build the AnkiDroid APK; see
**[docs/speedrun/android-spike.md](./docs/speedrun/android-spike.md)** for the
exact steps and the emulator setup used.

## Documentation for this fork

- **[docs/speedrun/rust-change.md](./docs/speedrun/rust-change.md)** — why the
  scheduler change is in Rust and how it works.
- **[docs/speedrun/DEMO_VIDEO.md](./docs/speedrun/DEMO_VIDEO.md)** — demo +
  proof-capture recording script.
- **[docs/speedrun/MANUAL_QA.md](./docs/speedrun/MANUAL_QA.md)** — manual QA
  checklist.
- **[POST_MVP_ROADMAP.md](./POST_MVP_ROADMAP.md)** — AI features (free-text
  grading, CARS, generation), sync, and everything deferred past the no-AI core.
- **[Speedrun_Brainlift_MCAT.md](./Speedrun_Brainlift_MCAT.md)** — the research /
  spiky points of view behind the design.

## Attribution & License

Speedrun is a fork of **Anki** (© Ankitects Pty Ltd and contributors) and is
distributed under the same license: **GNU AGPL, version 3 or later**. See
[LICENSE](./LICENSE). The list of upstream and fork contributors is in
[CONTRIBUTORS](./CONTRIBUTORS). Anki's project site: <https://apps.ankiweb.net>;
developer docs: <https://dev-docs.ankiweb.net>.

This fork is an independent educational project and is **not affiliated with or
endorsed by** Ankitects or the Anki project.
