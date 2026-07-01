# Speedrun — Demo & Proof Video Script

> **One video does everything.** Per mentor guidance, the required Wednesday
> proofs (clean build, test results, clean-machine install, phone review session)
> are captured **inside the single demo video**, not stitched together from
> separate clips. This script runs the proofs live as part of the walkthrough.
>
> Target length **~5 minutes**. Read narration lines aloud to gauge pacing.
> **Reference commit:** `401f76dad` on `main` — show this hash on camera.
> Upload to YouTube (Unlisted is fine) or Vimeo and paste the link in the
> submission's Demo Video field.

Scenes that satisfy a **required Wednesday proof** are marked ⭐.

## What Speedrun is (say this in the first 20 seconds)

Speedrun is a desktop **and** Android MCAT study app forked from **Anki**. The
one idea to land:

> One custom Rust scheduler — **shared by desktop AND Android** — that
> **interleaves** MCAT topics and **weights study toward measured-weak areas**,
> plus an **honest memory score** that admits its own uncertainty. It's the
> **no-AI core**: everything runs locally, no network, no LLM.

---

## Recommended ordering (timestamped)

| Time      | Scene | Beat                                              | Proof captured                    |
| --------- | ----- | ------------------------------------------------- | --------------------------------- |
| 0:00–0:20 | A     | Cold open / hook                                  | —                                 |
| 0:20–1:05 | B ⭐  | Terminal: commit hash → `just check` → tests pass | Commit hash + clean build + tests |
| 1:05–1:35 | C     | The codebase change (one shared Rust engine)      | (the Rust diff, shown)            |
| 1:35–2:15 | D ⭐  | Install the MSI on a clean machine → launch       | Clean-machine install             |
| 2:15–3:20 | E     | Desktop: interleave toggle, study, weakness, dash | (review loop + honest score)      |
| 3:20–4:15 | F ⭐  | Android emulator: same build, on-device toggle    | Phone review session              |
| 4:15–4:45 | G     | Close: no-AI statement + Release + thesis recap   | —                                 |

Total ~4:45. If you must trim to hit a hard 5:00 ceiling, shorten Scene C or the
narration in E — **do not cut B, D, or F** (they're the required proofs).

> **Recording setup tip:** you don't need one unbroken take. Record each scene,
> then concatenate in order into **one uploaded video** — that's still "one demo
> video," not separate submissions. Scene D (clean VM) and Scene F (emulator) are
> naturally separate captures; just splice them into the timeline.

---

## Scene A — Cold open / hook (0:00–0:20)

- **Show:** Title card "Speedrun — one Rust scheduler, two devices." Then a split
  of Anki desktop + the Android emulator, both on an MCAT deck.
- **Say:** "Most people cram one MCAT subject at a time. The research — and the
  real exam — say mix them. So we forked Anki and taught its Rust engine to
  interleave MCAT topics, on desktop _and_ the phone, from the same code — no AI,
  all local."

## Scene B ⭐ — Clean build, tests, commit hash (0:20–1:05)

> Required proof: **commit hash + clean-build recording + test results.**
> **Close every running Anki / `just run` window first** — a running instance
> holds `_rsbridge.pyd` and makes `just check` fail on the file-copy step (an OS
> lock, not a code error).

- **Show, in a terminal:**
  1. `git log -1 --oneline` → hash `401f76dad` visible.
  2. `git status` → clean tree.
  3. `just check` → let it finish on **`Build succeeded`** / exit 0. (If you want
     it shorter on camera, `just test-rust` + `just test-py` is a solid "tests
     pass" clip; `just check` is the fuller proof.)
- **Say:** "Clean tree at this commit. Full build and checks pass — the Rust
  core, Python, TypeScript, formatting, and lints — including the scheduler's own
  unit tests and a Python test that drives the change end to end."

## Scene C — The codebase change (1:05–1:35)

- **Show:** `rslib/src/scheduler/queue/builder/interleaving.rs` — the module
  doc-comment and `weighted_round_robin_by_topic`. Optionally overlay a diagram:
  **Rust core → PyO3 → Desktop** and **Rust core → JNI → AnkiDroid**.
- **Say:** "Here's the whole trick. When interleaving is on, we deal the day's
  already-gathered cards round-robin across the MCAT topics. It's a _pure
  reordering_ — it never touches a card's due date, interval, or FSRS memory
  state, so scheduling and undo stay correct. And because it lives in the core
  engine with config at the collection level, desktop and Android run the exact
  same code."

## Scene D ⭐ — Clean-machine install (1:35–2:15)

> Required proof: **an installer that runs on a clean machine.** This guards a
> hard grading rule — _"either app does not run on a clean device: 50% maximum."_

- **Show:** on a **fresh** Windows VM / machine with no dev toolchain:
  1. Double-click `anki-26.05-win-x64.msi` → installer runs → finishes.
  2. Launch the installed app → it opens to the deck list.
- **Say:** "It ships as a real installer. Here it is installing and launching on
  a clean Windows machine — no developer setup." Then continue the desktop demo
  on this installed app.

> macOS note: dev + recording are on Windows 11. The shared Rust engine is
> identical across platforms; a macOS installer needs
> `git submodule update --init qt/installer/mac-template` + a Mac/CI build. State
> the platform up front.

## Scene E — Desktop review + honest score (2:15–3:20)

- **Show:**
  1. Import `docs/speedrun/seed-deck/MCAT.apkg` (File → Import) if not already —
     72 cards across 3 topics. **Raise the deck's daily new-card limit** (deck
     options → New cards/day → e.g. 200) so all topics gather (see gotchas).
  2. **Tools → "Interleave MCAT topics"** → check it.
  3. Study; keep the card's **tag** visible and advance — topics rotate
     **Bio → Chem → Psych → Bio…**. Toggle off → same-topic blocks return.
  4. **Tools → "Weight interleaving by weakness"** (enabled only while
     interleaving is on) → mention weaker topics surface more often.
  5. **Tools → "MCAT Memory"** → dashboard: per-topic estimate + uncertainty
     band, and the **"Not enough data yet"** give-up state where reviews are thin.
- **Say:** "Same cards, same FSRS schedule — the engine just reorders them to
  interleave, and can lean on your measured-weak topics. And the memory score
  shows its uncertainty band instead of faking a confident number — if there
  isn't enough data, it says so."

## Scene F ⭐ — Android: same engine, on device (3:20–4:15)

> Required proof: **a review session on the phone** running the shared engine.

- **Show:** on the emulator with the Speedrun APK installed and the MCAT deck
  imported **on the phone** (separate collection — no sync in the MVP):
  1. AnkiDroid deck list with the MCAT deck.
  2. DeckPicker **overflow menu → "Interleave MCAT topics"** → flip on.
  3. Study on the phone; topics **alternate** just like desktop.
  4. (Optional) `adb logcat | grep -i backend` once to show the backend version
     string = our engine build.
- **Say:** "This is the phone — the _same_ Rust engine, no Kotlin scheduler. The
  toggle writes the same collection config the desktop uses, and the shared
  engine does the interleaving. One change, two platforms."

> Android runs the engine at submodule commit `e6a435d7a` (uniform interleaving);
> weakness-weighting shipped after that pin, so demo _that_ on desktop (Scene E).

## Scene G — Close (4:15–4:45)

- **Show:** the GitHub **Release** page (the `.msi` + `.apk` — this is the
  submission's "deployed site"), then back to the title card.
- **Say:** "One custom Rust scheduler, shared by a desktop app and an Android
  app — it interleaves MCAT topics, weights your time toward your weak areas, and
  gives a memory score honest enough to admit what it doesn't know. All of it
  runs locally with no AI. That's Speedrun."

---

## Required-proof checklist (assignment → this video)

The Wednesday brief requires: _"Commit hash and a clean-build recording, the test
results, a clean-machine install recording, and a screen recording of a review
session on the phone."_ This video covers all of it:

- [ ] Commit hash on screen — Scene B
- [ ] Clean-build recording — Scene B
- [ ] Test results — Scene B
- [ ] Clean-machine install recording — Scene D
- [ ] Phone review-session recording — Scene F

---

## Pre-recording checklist

- [ ] `git status` clean; you're on `401f76dad` (or later).
- [ ] **Close all Anki / `just run` windows** before Scene B (pyd file lock).
- [ ] Clean Windows VM/machine ready with the `.msi` copied over (Scene D).
- [ ] Desktop app has `MCAT.apkg` imported **and the daily new-card limit raised**
      so multiple topics surface (Scene E).
- [ ] A few reviews done first so the dashboard shows both a populated state and
      a "Not enough data yet" state (Scene E).
- [ ] Emulator booted, APK installed, MCAT deck imported **on the phone**
      (Scene F).
- [ ] GitHub Release page open with `.msi` + `.apk` attached (Scene G).
- [ ] Screen recorder + mic tested; notifications silenced; nothing private on
      screen.

---

## Automated verification (say in Scene B / paste into submission notes)

Run against `401f76dad`:

| Check                    | Command                                        | Result         |
| ------------------------ | ---------------------------------------------- | -------------- |
| Rust core lib tests      | `cargo test -p anki --lib` (`just test-rust`)  | **exit 0**     |
| Python (pylib) suite     | `just test-py`                                 | **123 passed** |
| Interleaving unit/integ. | `cargo test -p anki --lib interleaving`        | **5 passed**   |
| Seed-deck integration    | `test_interleave_orders_the_shipped_seed_deck` | **passed**     |
| Full build + lints       | `just check` (Anki closed)                     | green / exit 0 |

---

## Talking points / thesis (for the judge)

> - **Interleaving weighted by _measured_ weakness.** Many apps mix subjects;
>   Speedrun biases the round-robin toward the topics you're weakest at, using
>   FSRS predicted recall — study time follows the evidence.
> - **An intentionally humble memory score.** Uncertainty band that narrows with
>   reviews + a give-up rule that shows "Not enough data yet" instead of fake
>   precision.
> - **One engine, two platforms.** Scheduler change in the shared Rust core,
>   config at the collection level — desktop and Android behave identically with
>   no per-platform reimplementation.
> - **Safe by construction.** Interleaving is a pure reordering — never mutates
>   due dates, intervals, or FSRS state — backed by unit + integration tests.

---

## Gotchas that will bite on camera

- **Close Anki before `just check`** — otherwise the pyd copy fails with a file
  lock (Scene B).
- **Raise the daily new-card limit after importing** `MCAT.apkg` (deck options →
  New cards/day → e.g. 200). A fresh import does **not** carry the deck's baked
  500/day limit, so the day fills from one section and nothing interleaves — the
  "only 20 new" trap (verified in the integration test).
- **Android is a separate collection** — import the deck on the phone too.
- **`ANKI_TEST_MODE=1`** if you re-run pytest by hand (otherwise three
  `test_schedv3.py` interval tests flake because interval fuzz is only disabled
  in test mode; the `just` harness sets it automatically).
