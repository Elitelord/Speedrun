# Speedrun — Demo Video Script & Shot List

> Hackathon MVP submission. Target length **3–5 minutes**. Read the narration
> lines aloud to gauge pacing; each is meant to be spoken in one breath.

## What Speedrun is (30-second framing)

Speedrun is a desktop **and** Android MCAT study app forked from **Anki**, the
spaced-repetition flashcard engine. Anki is multi-layer: a **core Rust engine**
(`rslib`), a PyO3 bridge, a Python + PyQt desktop app, a Svelte/TypeScript web
frontend, and protobuf IPC between layers. Android (AnkiDroid) builds its backend
from the **same Rust engine**.

**The one idea to land in this demo:**

> One custom Rust scheduler — **shared by desktop AND Android** — that
> **interleaves** MCAT topics and **weights study toward measured-weak areas**,
> plus an **honest memory score** that admits its own uncertainty.

Everything else on screen is in service of that sentence. Because the logic lives
in the shared engine and its config lives at the **collection** level, the phone
gets the same behavior with **zero Kotlin scheduler code**.

---

## Recommended ordering (timestamped)

| Time      | Scene | Beat                                           | Screen                                     |
| --------- | ----- | ---------------------------------------------- | ------------------------------------------ |
| 0:00–0:20 | A     | Cold open / hook                               | Title card → split desktop + phone         |
| 0:20–0:55 | B     | The codebase change — one shared Rust engine   | `interleaving.rs` in editor + arch diagram |
| 0:55–1:40 | C     | Desktop: import deck, toggle interleave, study | Anki desktop, MCAT deck, study screen      |
| 1:40–2:20 | D     | Desktop: MCAT Memory dashboard + honest score  | SvelteKit memory dashboard                 |
| 2:20–2:50 | E     | Weakness-weighted interleaving                 | Config field + study screen                |
| 2:50–3:40 | F     | Android: same build, on-device toggle          | Emulator, DeckPicker overflow menu, study  |
| 3:40–4:10 | G     | Close: installer/MSI + thesis recap            | MSI in Explorer → title card               |

Total ~4:10. Trim Scene B or E first if you need to hit 3:00.

---

## Scene-by-scene shot list

### Scene A — Cold open / hook (0:00–0:20)

- **Show:** Title card "Speedrun — one Rust scheduler, two devices." Cut to a
  split screen: Anki desktop on the left, the Android emulator on the right, both
  showing an MCAT deck.
- **Say:** "Cramming one subject at a time is how most people study for the MCAT.
  The research — and the real exam — say you should mix subjects. So we forked
  Anki and taught its Rust engine to interleave MCAT topics — on desktop _and_ on
  the phone, from the same code."
- **Have open:** Anki desktop (deck list), Android emulator (deck list).

### Scene B — The codebase change: one shared Rust engine (0:20–0:55)

- **Show:** `rslib/src/scheduler/queue/builder/interleaving.rs` in the editor.
  Scroll to the module doc-comment (top of file) and to
  `weighted_round_robin_by_topic`. Optionally overlay a simple diagram:
  **Rust core → PyO3 → Desktop** and **Rust core → JNI → AnkiDroid**.
- **Say:** "This is the whole trick. When interleaving is on, we take the day's
  already-gathered cards and deal them round-robin across the MCAT topics —
  Bio/Biochem, Chem/Phys, Psych/Soc. It's a _pure reordering_: it never touches a
  card's due date, interval, or FSRS memory state, so scheduling and undo are
  untouched. And because it lives in the core engine, the desktop and the Android
  build run the exact same code."
- **Have open:** `rslib/src/scheduler/queue/builder/interleaving.rs`;
  optionally `docs/speedrun/rust-change.md` for the "Why Rust" points.
- **Note:** Config is stored at collection level (`BoolKey::InterleaveTopics` +
  topic tags) and exposed via `Set/GetInterleaveConfig` RPCs — that is _why_ it
  ships to Android for free.

### Scene C — Desktop: import, toggle, study (0:55–1:40)

- **Show:**
  1. Import `docs/speedrun/seed-deck/MCAT.apkg` (File → Import). 72 original
     cards across the 3 topics.
  2. Open **Tools → "Interleave MCAT topics"** and check it (confirm the
     checkmark appears).
  3. Study the MCAT deck. Point the cursor at the tag on each card as you advance
     — show the topic changing every card: Bio → Chem → Psych → Bio…
  4. Uncheck the toggle, restart study, show cards now come in same-topic blocks.
- **Say:** "Here's the seed deck — 72 cards tagged across the three MCAT sections.
  I flip on 'Interleave MCAT topics' under Tools… and now watch the tags as I
  study: Bio, then Chem, then Psych, round and round. Turn it off, and it goes
  back to one topic at a time. Same cards, same schedule — just a smarter order."
- **Have open:** Anki desktop; Tools menu; the study screen with card tags
  visible.

### Scene D — Desktop: MCAT Memory dashboard, honest score (1:40–2:20)

- **Show:** **Tools → "MCAT Memory"** opens the SvelteKit dashboard
  (`ts/routes/memory-dashboard/`). Show the per-topic cards: each has an estimate,
  an **uncertainty band** (range low–high), and a review count. Then show a topic
  with too few graded reviews rendering the **"Not enough data yet"** give-up
  state.
- **Say:** "Most 'AI study scores' pretend to be certain. Ours won't. Each score
  is the mean FSRS predicted recall for a topic — always shown with an uncertainty
  band that shrinks as you do more reviews. And if there aren't enough graded
  reviews yet, it refuses to guess and says 'Not enough data yet.' Honest beats
  confident."
- **Have open:** The memory dashboard; if convenient,
  `rslib/src/scheduler/memory_score.rs` (module doc + the give-up rule at
  `shown: self.graded_reviews >= min_reviews`) as a quick cutaway.
- **Note:** Fresh install with no reviews = every topic shows "Not enough data
  yet." That is the _correct_ state — feel free to show it first, then a populated
  one after reviewing.

### Scene E — Weakness-weighted interleaving (2:20–2:50)

- **Show:** **Tools → "Weight interleaving by weakness"** and check it (it is
  enabled only while "Interleave MCAT topics" is on). Then, on the study screen,
  point out that the weaker topic (lower measured recall in the dashboard) comes
  up more often in the round-robin.
- **Say:** "We can go one step further. Turn on weakness weighting and the
  round-robin leans on your _weakest_ topics — the ones with the lowest measured
  FSRS recall show up more often — so your minutes go where you're actually shaky,
  not where you already know the material."
- **Have open:** Interleave config / the toggle; the study screen; optionally the
  dashboard to point at which topic is weakest.

### Scene F — Android: same build, on-device toggle (2:50–3:40)

- **Show:**
  1. The Android emulator running the AnkiDroid build with the MCAT deck present.
  2. DeckPicker **overflow menu → "Interleave MCAT topics"** (`action_interleave_mcat`).
     Flip it on.
  3. Study on the phone; show the topics alternating just like desktop.
- **Say:** "Now the payoff. This is the phone — the _same_ build. I open the deck
  menu, flip 'Interleave MCAT topics', and study… and it interleaves, exactly like
  the desktop did. There's no Kotlin scheduler here — that toggle just writes the
  same collection config, and the same Rust engine compiled into the phone does
  the reordering. One change, two platforms."
- **Have open:** Android emulator (DeckPicker → overflow menu → the MCAT deck's
  study screen).
- **Emphasize:** The word "same" — same engine, same config key, same behavior.
  This is the spiky claim; make it land.

### Scene G — Close: installer + thesis recap (3:40–4:10)

- **Show:** The Windows MSI at `out/installer/dist/anki-26.05-win-x64.msi` in
  Explorer (proof it ships as a real installable app). Cut back to the title card.
- **Say:** "It ships as a real desktop installer and a real Android app. One
  custom Rust scheduler, shared by both — it interleaves MCAT topics, weights your
  time toward your measured-weak areas, and gives you a memory score honest enough
  to admit what it doesn't know. That's Speedrun."
- **Have open:** File Explorer at `out/installer/dist/`; title card.

---

## Pre-recording checklist

- [ ] Build & launch desktop: `just run` (see it fully up before recording).
- [ ] Import `docs/speedrun/seed-deck/MCAT.apkg` on desktop.
- [ ] Set a **generous daily new-card limit** on the MCAT deck so multiple topics
      surface in one session (a fresh import may not auto-apply a high limit — set
      it manually via deck options if only one topic appears).
- [ ] Do a handful of reviews first so the memory dashboard has both a populated
      state _and_ a "Not enough data yet" state to show.
- [ ] Android emulator booted, app installed, MCAT deck imported/created **on the
      phone** (Android is a separate collection — no sync in this demo).
- [ ] Confirm the MSI exists at `out/installer/dist/anki-26.05-win-x64.msi`.
- [ ] Screen recorder + mic tested; audio levels checked.
- [ ] Close all notifications (OS + chat), silence phone, hide anything private.
- [ ] Editor open to `interleaving.rs` and `memory_score.rs` on the relevant lines.
- [ ] Confirm the Tools menu shows "Interleave MCAT topics" (checkable), "Weight
      interleaving by weakness" (checkable), and "MCAT Memory".

---

## Talking points / thesis (for the judge)

> **Why this is novel — and spiky.**
>
> - **Interleaving weighted by _measured_ weakness.** Plenty of apps let you mix
>   subjects. Speedrun uses **FSRS predicted recall (retrievability)** to bias the
>   round-robin toward the topics you're actually weakest at — study time follows
>   the evidence, not a fixed rotation.
> - **An intentionally humble memory score.** Instead of a single confident
>   number, every score carries an **uncertainty band** that narrows with more
>   reviews, and a **give-up rule** that shows "Not enough data yet" rather than
>   fake precision. Honesty is the feature.
> - **One engine, two platforms.** The scheduler change is in the **shared Rust
>   core** with config at the **collection level** — so desktop and Android behave
>   identically with **no per-platform reimplementation**. The Android toggle just
>   flips the same config the desktop does.
> - **Safe by construction.** Interleaving is a **pure reordering**: it never
>   mutates due dates, intervals, or FSRS state, so scheduling correctness and
>   undo are provably unaffected (backed by unit + integration tests).

---

## Gotchas (call out or avoid on camera)

- **Android is a separate collection.** There's no sync in this demo, so the MCAT
  deck must be **imported/created on the phone separately** from desktop. Do this
  before recording.
- **Daily new-limit may not carry over.** A fresh desktop import might not
  auto-apply a high daily new-card limit — if only one topic shows up when
  studying, raise the limit manually in deck options so all three topics appear.
- **OS mismatch.** Development and this recording are on **Windows 11**; the
  submission's stated test target is **macOS**. Mention this as a caveat if asked
  — the shared Rust engine is the same across platforms, but note the discrepancy
  up front so it isn't a surprise.
- **Empty dashboard is correct.** With no reviews, "Not enough data yet" is the
  intended honest state — don't mistake it for a bug on camera; explain it.
