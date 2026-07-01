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

## Download & install (prebuilt)

Prebuilt installers are attached to the
[latest GitHub Release](../../releases/latest).

**Desktop (Windows):**

1. Download `anki-26.05-win-x64.msi` from the release.
2. Double-click it and follow the installer. The build is unsigned, so Windows
   SmartScreen may warn — choose **More info → Run anyway**.
3. Launch **Anki** from the Start menu.

**Android:**

- **Physical device:** download `AnkiDroid-play-arm64-v8a-debug.apk`, allow
  "Install unknown apps" for your browser/file manager, then open the file to
  install.
- **Emulator (x86_64):** download `AnkiDroid-play-x86_64-debug.apk` and install
  with `adb install -r AnkiDroid-play-x86_64-debug.apk`.

**After installing (both platforms):** the desktop and Android apps are
**separate collections**, so import the MCAT deck
(`docs/speedrun/seed-deck/MCAT.apkg`) on each. Then, in **Deck options**, raise
**New cards/day** so all three topics appear, and enable **FSRS** to power the
memory score. Turn interleaving on via **Tools → "Interleave MCAT topics"**
(desktop) or the DeckPicker overflow menu (Android).

## Build from source

### Prerequisites

`git` plus the standard
[Anki development prerequisites](./docs/development.md) — the build system
downloads its own Rust / Python / Node toolchains through `just`, so there is
little to install beyond that. Build from a normal shell at the repo root.

### Desktop

Everything is wrapped in `just` recipes (run `just --list` to see them all):

```bash
just run       # build pylib + qt and launch the desktop app
just check     # format + full build & checks (Rust, Python, TS)
just test-rust # Rust tests   (includes the interleaving unit/integration tests)
just test-py   # Python tests (includes pylib/tests/test_interleave.py)
```

To produce the Windows installer yourself, **close any running Anki** (a running
instance locks a build artifact), then run `tools/build-installer.bat`; the
`.msi` is written to `out/installer/dist/`.

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
