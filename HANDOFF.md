# Handoff — Speedrun MVP (for the planning agent)

> **You are planning the implementation of the Speedrun MVP.** Speedrun is a
> desktop + Android study app **forked from Anki** for the **MCAT**. Read the
> docs below, then produce an implementation plan for the **MVP only** (the
> assignment's "Wednesday no-AI core"). Do **not** plan AI, CARS, two-way sync,
> performance, or readiness work beyond what the MVP requires — those are
> deferred (see roadmap).

## Read these first (in order)

| Doc                                                                                                                                      | Why it matters                                                                                                                          |
| ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| [`prd.md`](./prd.md)                                                                                                                     | The MVP spec — scope, features, Rust change, user stories, tech stack, Wednesday deliverables. **This is your primary input.**          |
| [`POST_MVP_ROADMAP.md`](./POST_MVP_ROADMAP.md)                                                                                           | What's deferred to Friday/Sunday. Read it so the MVP plan doesn't paint us into a corner, but **do not plan this work**.                |
| [`Speedrun_ A Desktop + Mobile Study App Built on Anki.md`](./Speedrun_%20A%20Desktop%20+%20Mobile%20Study%20App%20Built%20on%20Anki.md) | The actual grading rubric & hard constraints. The PRD only summarizes it — confirm the Wednesday proof list and the "hard limits" here. |
| [`codebase-map/README.md`](./codebase-map/README.md)                                                                                     | Index for finding code. **Use this instead of grepping broadly.** Then open the area files below.                                       |
| [`CLAUDE.md`](./CLAUDE.md) / [`AGENTS.md`](./AGENTS.md)                                                                                  | Project conventions: the `just`-recipe workflow, Rust error handling, build/check/test commands. Plan around these.                     |
| [`Speedrun_Brainlift_MCAT.md`](./Speedrun_Brainlift_MCAT.md)                                                                             | _Optional._ Research & rationale (the "why" behind interleaving, honesty, etc.). Not requirements.                                      |

### Most relevant codebase-map area files

- [`codebase-map/01-rust-core.md`](./codebase-map/01-rust-core.md) — scheduler (`rslib/src/scheduler/queue/builder/`, `scheduler/fsrs/`), `Collection`, storage, undo.
- [`codebase-map/05-protobuf-ipc.md`](./codebase-map/05-protobuf-ipc.md) — how to add the new protobuf message/RPC and reach Python + TS.
- [`codebase-map/04-web-frontend.md`](./codebase-map/04-web-frontend.md) — Svelte/TS frontend for the new memory dashboard + review UI.
- [`codebase-map/03-qt-gui.md`](./codebase-map/03-qt-gui.md) — PyQt host that embeds the webviews.
- [`codebase-map/07-build-system.md`](./codebase-map/07-build-system.md) — `just` recipes, ninja, run scripts, installer.

## Decisions already locked (do not re-litigate)

- **MVP = the Wednesday no-AI gate only.** Forked Anki building on desktop + a
  running Android build; everything else is post-MVP.
- **Exam: MCAT** (472–528; four sections 118–132). Interleave the first three
  sections: Bio/Biochem, Chem/Phys, Psych/Soc.
- **Rust change = a topic-aware interleaving scheduler** in
  `rslib/src/scheduler/queue/builder/`, exposed via a **new protobuf RPC** and
  **called from Python**. It must keep FSRS intervals valid and undo working.
  _(This same feature is the learning-science feature for the later ablation
  test — design it so it can be toggled on/off.)_
- **Frontend stays on Anki's Svelte + TS** stack. **No framework swap.** New
  screens = new Svelte components/pages under `ts/`.
- **Mobile target = Android (AnkiDroid)**, chosen because the dev host is
  Windows. iOS is out.
- **Android build path = fork AnkiDroid (Path A).** See the dedicated section
  below.
- **Honest memory score** = derived from existing FSRS memory state; always a
  point estimate **+ a range**; governed by a **give-up rule** (MVP draft:
  no per-topic score < 20 graded reviews, no deck score < 100). These thresholds
  are tunable.
- **License:** AGPL-3.0-or-later, credit to Anki.

## Android build path (DECIDED: fork AnkiDroid)

**Two apps, one engine.** The Android app lives in a **separate repo** from this
one, but it shares the Rust core (`rslib/`) that lives here. This repo already
contains `rslib/src/ankidroid/` (backend shims for the Android client),
confirming the model: _this_ repo's Rust is compiled into a backend artifact
(a `rsdroid`-style JNI/FFI bridge, talking protobuf) that the Android app
consumes.

**Decision: fork AnkiDroid (`ankidroid/Anki-Android`)** and point its backend
dependency at our **modified `rslib`** compiled for Android targets — rather than
writing a custom Android app from scratch. Rationale: maximum reuse — we inherit
AnkiDroid's existing native review UI, so the Wednesday Android gate ("loads the
MCAT deck + runs a real review session on the shared engine") becomes mostly a
**build/wiring** problem, not a UI build.

> **Repo status:** the maintainer will create the AnkiDroid fork on GitHub before
> this handoff is sent. Assume a forked `Anki-Android` repo will be available; if
> it is not yet present locally, plan a "clone fork + wire to our Android backend"
> setup step.

Implications the plan must account for:

- **The interleaving Rust change ships to Android for free** (it's in the shared
  engine / queue builder) — no Kotlin work needed for the scheduler itself.
- **The Svelte memory dashboard does NOT carry to Android.** That reuse only
  helps the desktop (Qt webviews); AnkiDroid's UI is native Kotlin. A score
  dashboard _on the phone_ is therefore separate work — but it's a **Friday**
  item, so it is out of MVP scope. The Wednesday Android gate is only build +
  load deck + run a review session.
- **Two repos to keep in sync:** our `anki` fork (engine + Rust change) and our
  `Anki-Android` fork (depends on our Android-built backend). Pin/document how
  the Android build resolves our modified backend artifact.

## Resolve these EARLY (highest-risk / longest-lead — spike before committing the plan)

1. **AnkiDroid backend wiring (path already decided — see section above).**
   Sharing our _modified_ Rust engine on-device is the riskiest, longest-lead
   item in the MVP. Plan a spike: how do we compile our `rslib` change for
   Android and make our AnkiDroid fork build against that backend artifact, and
   what does "loads the MCAT deck + runs a real review session on the shared
   engine" concretely require? The Wednesday gate does **not** require two-way
   sync — only reviewing the same deck on the phone.
2. **Seed deck sourcing + licensing.** The pre-seeded interleaved MCAT decks are
   an open dependency. Identify openly licensed/importable content and the
   topic-tagging scheme the scheduler will interleave on.
3. **Memory "range" method.** Decide how the uncertainty band is computed from
   FSRS predicted recall (e.g., percentile spread vs. n-based interval).
4. **Protobuf → Python → TS plumbing.** Adding a `.proto` message likely needs a
   full `just check` build to regenerate bindings; sequence this so frontend and
   Python work isn't blocked.

## Definition of done for the MVP (from the brief's Wednesday gate)

Plan toward producing all of this proof:

- Forked Anki **building from source** on desktop (commit hash + clean-build).
- Rust change working end-to-end: **the diff + ≥3 Rust unit tests + 1 Python
  test**, undo intact, no collection corruption; a one-page "why Rust" note; a
  list of upstream files touched + merge-difficulty notes.
- A **review loop** running on the interleaved MCAT deck.
- An **honest memory score** on screen: estimate + range + give-up-rule behavior.
- A **desktop installer** that runs on a clean machine.
- An **Android build** that loads the MCAT deck and runs a real review session
  on the shared engine.

## Build/tooling reminders (from CLAUDE.md)

- Use **`just` recipes**, not raw `./ninja` / `./run` / `tools/` scripts.
  Key: `just run`, `just check` (format + build + checks), `just test-rust` /
  `just test-py` / `just test-ts`, `just web-watch` for live frontend reload.
- Rust errors in `rslib`: use `error/mod.rs`'s `AnkiError`/`Result` + snafu.
- Changes to `.proto` files generally need a full `just check` first.
- A diagram of the target architecture lives in `prd.md` (and
  `prd-techstack.mmd`).

## Output expected from you (the planner)

A phased implementation plan for the MVP that:

- Front-loads the **Android engine-sharing spike** and the **protobuf plumbing**.
- Breaks the **interleaving scheduler** into: Rust queue-builder change →
  protobuf message → Python call → tests (3 Rust + 1 Python) → toggle for
  ablation.
- Specifies the **Svelte memory-dashboard + review UI** work and how it reads the
  score from the backend.
- Includes **deck seeding/tagging**, the **desktop installer**, and the
  **clean-build / clean-install** verification steps.
- Maps each task back to a **Wednesday deliverable** above, and flags anything
  that can't make Wednesday.
