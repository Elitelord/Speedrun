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

### Core (offline, no-AI)

Everything below runs locally — no network calls, no LLM, no generated content:

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

### AI & two-way sync (Friday layer)

Cloud-AI features on desktop, all **safe by construction** and **fully optional**:

- **Three honest scores** — **Memory / Performance / Readiness**, each with a
  range and a give-up rule ("not enough data"), Readiness on the real **472–528**
  scale — never one blended number. On the **Progress** page (desktop) and the
  **Progress** tab + home header (Android).
- **Grounded card generation + pre-display eval gate.** Cards are generated from
  **named** MCAT sources (OpenStax CC-BY, Wikipedia CC-BY-SA); anything not
  supported by its source is blocked, and a held-out gold set is graded against a
  cutoff committed _before_ results (beats a keyword baseline; no wrong card
  ships). See **[docs/speedrun/ai/README.md](./docs/speedrun/ai/README.md)** and
  **[eval-report.md](./docs/speedrun/ai/eval-report.md)**.
- **Free-text production review.** Type an answer → an LLM grades it by meaning
  and **suggests the grade** (Again/Hard/Good/Easy) → a miss gets a scaffolded
  hint (that never gives the answer away) before a clean reveal — not a silent
  flip.
- **CARS module.** Grounded generation of **passage + multiple-choice reasoning**
  questions (the 4th MCAT section), with its own eval gate and a custom notetype;
  interleaves alongside the sciences. See
  **[docs/speedrun/ai/cars/README.md](./docs/speedrun/ai/cars/README.md)**.
- **AI-off invariant.** With AI disabled (or no key / offline), generation and
  grading abstain, review degrades to the native self-graded reveal, and the
  three scores still compute.
- **Two-way sync** desktop ↔ Android via Anki's own sync (AnkiWeb or a self-hosted
  server): offline review, sync on reconnect, no lost or double-counted reviews.

### Evidence — every claim is re-runnable

Models are validated, not asserted, and each check is one command
(**[docs/speedrun/VERIFY.md](./docs/speedrun/VERIFY.md)** maps every claim to its
command and artifact):

- **Memory calibration** — `just calibration` → reliability chart + Brier / log-loss
  / ECE (a labelled real+simulated hybrid; honest about limited longitudinal data).
- **Study-feature ablation** — `just ablation` → interleaving on / off / plain Anki,
  a pre-registered metric, and the honest null where it makes no difference.
- **Leakage check** — `just leakage` → no gold test item is a near-copy of its
  source (so the beat-a-baseline result is real).
- **AI + CARS eval gates** — held-out gold sets vs pre-registered cutoffs, 2×2
  confusion matrices with the false-negative cell capped (FN=0).
- **Model descriptions** — one page each for memory / performance / readiness in
  **[docs/speedrun/models/](./docs/speedrun/models/)**, including give-up rules and
  honest limitations.

## Architecture

Anki (and therefore Speedrun) is multi-layered:

- **Core Rust engine** — `rslib/` (interleaving in
  `rslib/src/scheduler/queue/builder/interleaving.rs`; the three scores in
  `rslib/src/scheduler/memory_score.rs` + `readiness.rs`).
- **PyO3 bridge** — `pylib/rsbridge/` exposes the Rust API to Python.
- **Python library + PyQt desktop app** — `pylib/anki/`, `qt/aqt/`.
- **Svelte / TypeScript web frontend** — `ts/` (Anki's shared web components).
  Speedrun's Home / Progress / Settings views are rendered in-window by the deck
  browser app-shell (`qt/aqt/deckbrowser.py`); the AI pipeline lives in
  `qt/aqt/speedrun_ai/`.
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

**After installing:** the desktop app **auto-loads the MCAT deck on first run**
(no import step). On Android the deck arrives via **sync**, or import
`MCAT.apkg` from the **+ (add-deck) menu**. The two apps are **separate
collections** until you sign both into the same sync account. Enable **FSRS**
(Deck options) to power the scores, and turn interleaving on via **Settings →
Interleave** (desktop) or the **⋮ overflow → "Interleave MCAT topics"**
(Android). The three scores live on the **Progress** page (desktop) and the
**Progress** tab / home header (Android).

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

- **[docs/speedrun/VERIFY.md](./docs/speedrun/VERIFY.md)** — every claim mapped to
  the one command that reproduces it.
- **[docs/speedrun/rust-change.md](./docs/speedrun/rust-change.md)** — why the
  scheduler change is in Rust and how it works.
- **[docs/speedrun/models/](./docs/speedrun/models/)** — one-page descriptions of
  the memory / performance / readiness models (with give-up rules + limitations).
- **[docs/speedrun/eval/](./docs/speedrun/eval/)** — the re-runnable evidence:
  calibration, interleaving ablation, and leakage-check scripts + reports.
- **[docs/speedrun/DEMO_VIDEO.md](./docs/speedrun/DEMO_VIDEO.md)** — final demo
  recording script.
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
