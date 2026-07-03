# Speedrun — Demo Video Script

> **Two videos, two deadlines.** Wednesday's submission already proved the no-AI
> core — clean build + tests, the interleaving Rust change, the clean-machine
> installer, and a phone review session. **This Friday video shows only what's
> *new* since then: the AI layer, the three honest scores, and two-way sync.**
> Target **~3–4 minutes**. The Wednesday/Sunday-only scenes (build, interleaving,
> installer) are preserved in the
> [appendix](#appendix--scenes-for-the-full-sunday-video) so the fuller Sunday
> video can reuse them.
>
> **Reference commit:** show your latest pushed `main` hash on camera (push the
> engine + Android app first). Upload to YouTube (Unlisted) or Vimeo; paste the
> link in the submission. **Don't show your OpenAI key or AnkiWeb password.**

The brief's Friday **proof** is exactly two things, marked ⭐ below:
**(1)** the AI eval numbers + baseline comparison, and **(2)** a review done on the
phone showing up on desktop after sync (and back).

## What's new since Wednesday (all this video shows)

> - **AI, safe by construction** — cards **generated from named sources**, a
>   **pre-registered eval gate** (beats a keyword baseline; no wrong card ships),
>   and **free-text grading** with an LLM. Still works with **AI switched off**.
> - **Three honest scores** — Memory / Performance / Readiness, each a range with a
>   give-up rule, on the real 472–528 scale — on **both** desktop and phone.
> - **Two-way sync** desktop ↔ phone with no lost or double-counted reviews.

*(The interleaving Rust change, the installer, and the phone review session were
Wednesday's proofs — deliberately **not** re-shown here.)*

## Ordering (Friday cut, ~3–4 min)

| Time      | Scene | Beat                                                  | Proof captured             |
| --------- | ----- | ---------------------------------------------------- | -------------------------- |
| 0:00–0:15 | A     | Cold open / hook                                     | —                          |
| 0:15–0:55 | B ⭐  | Commit hash + AI eval report (PASS, beats baseline)  | AI eval + baseline         |
| 0:55–1:40 | C     | Desktop: free-text grading                           | new AI review loop         |
| 1:40–2:20 | D     | Desktop: three scores + ranges + AI-off              | honest scores + AI-off     |
| 2:20–3:00 | E ⭐  | Phone: the three scores (Progress tab)               | phone shows scores         |
| 3:00–4:00 | F ⭐  | Two-way sync: offline → reconnect → reconcile        | sync, no lost/double-count |
| 4:00–4:20 | G     | Close                                                | —                          |

---

## Scene A — Cold open (0:15)

- **Show:** Title "Speedrun — one Rust engine, two devices, honest scores." Split
  of desktop + Android emulator on the MCAT deck.
- **Say:** "Speedrun is an MCAT study app I forked from Anki. The core — one shared
  Rust engine that interleaves topics across desktop and phone — shipped Wednesday.
  Since then I added an AI layer, three honest scores, and two-way sync. Here's the
  new stuff."

## Scene B ⭐ — AI eval + baseline (0:15–0:55)

> The brief's Friday AI proof. No need to re-run the full `just check` build — that
> was Wednesday's proof; just anchor the commit and show the eval report.

- **Show, in a terminal:**
  1. `git log -1 --oneline` → your latest pushed hash.
  2. `cat docs/speedrun/ai/eval-report.md` → **PASS**: the beat-a-baseline table
     (RAG top-1 **1.000** vs BM25 **0.944**, MRR 1.000 vs 0.968) and the 2×2
     confusion matrix (**FN=0**).
- **Say:** "Every AI card is generated from a named source and graded against a
  held-out gold set, with a cutoff I committed *before* seeing results. It caught
  every bad card — zero shipped — and its embedding retrieval beats a plain keyword
  search at finding the right source for a student's paraphrased question."

## Scene C — Desktop: free-text grading (0:55–1:40)

- **Show:** **Settings → Review → Free-text grading** (on). Study a type-in card:
  **type an answer → the LLM grades it by meaning → a wrong attempt gets a hint →
  re-attempt → reveal**, and it waits on the feedback for you to pick a grade.
- **Say:** "Instead of a flip-card, you *produce* the answer. An LLM grades what you
  typed by meaning, and a miss gets a scaffolded hint before the reveal — closer to
  how the MCAT actually tests."

## Scene D — Desktop: three scores + AI-off (1:40–2:20)

- **Show:**
  1. **Progress** page — **Memory / Performance / Readiness** as cards with
     **ranges** + **per-section bars**, the **Readiness total on 472–528** with
     coverage (and the CARS placeholder), and the **"not enough data"** give-up
     state where reviews are thin.
  2. **AI-off invariant:** **Settings → AI → Enable AI = off** → review a type-in
     card → it falls back to the **native self-graded reveal**, and the Progress
     scores **still compute**. (The OpenAI key lives in Settings → AI, so a
     downloaded build uses the user's own key.)
- **Say:** "Three honest scores, never one blended number — each a range with a rule
  that says 'not enough data' instead of faking confidence. And every AI feature
  degrades cleanly: turn AI off and the app still grades and still scores."

## Scene E ⭐ — Phone shows the three scores (2:20–3:00)

> Friday mobile requirement: **the phone shows the three scores with ranges.**

- **Show:** on the emulator with the Speedrun APK and the MCAT deck present:
  1. The AnkiDroid **home screen** — the **three-score header** (Memory /
     Performance / Readiness) on top, **decks as cards**, and the **bottom nav**
     (Decks / Browse / Progress / More) mirroring the desktop rail.
  2. Tap the **Progress tab** → the three scores as cards with **ranges**, each
     **expandable per MCAT section**, the **Readiness total on 472–528** with
     coverage + the give-up state, and a **"View detailed graphs"** button.
- **Say:** "The same three scores on the phone — computed by the **same Rust RPCs**
  as desktop, no Kotlin scheduler. One engine, two platforms."

## Scene F ⭐ — Two-way sync (3:00–4:00)

> Friday sync proof: **a review done on the phone shows up on desktop (and the
> reverse)**, with **offline review** and **no lost or double-counted reviews.**
> Full detail in [`SYNC.md`](./SYNC.md).

- **Setup (before recording):** sign both apps into the **same sync account** —
  simplest is **AnkiWeb** (desktop **Sync** rail; Android **More → Settings →
  Sync**). _(Self-hosted alternative: `SYNC_USER1=demo:demo … --syncserver`, both
  clients pointed at `http://<LAN-ip>:8080/`.)_ Sync both once so they start from
  the **same deck**. **Don't show the password.**
- **Show — the beat is a *review* crossing devices, not just the deck:**
  1. Both devices open on the MCAT deck with **matching due counts**.
  2. Put **Android in airplane mode**; **review several cards offline** (due count
     drops with no connection).
  3. On **desktop**, review a few *different* cards.
  4. **Reconnect Android → Sync**, then **Sync on desktop**.
  5. The phone's offline reviews are **now on desktop** and the desktop's reviews
     **on the phone** — **identical due/review state**, nothing lost or
     double-counted. _(Strong optional: open one card in the browser on both and
     show the same review-log entry.)_
- **Say:** "No new sync code — I reuse Anki's own sync; AnkiWeb here, the same
  protocol as the self-hosted server. Reviews are keyed by their millisecond
  timestamp and merged insert-or-ignore, so a review arriving twice can't be
  double-counted. Offline on the phone, different cards on desktop, reconnect,
  sync — both reconcile to the exact same state."

## Scene G — Close (4:00–4:20)

- **Show:** the GitHub **Release** page (`.msi` + `.apk`), then the title card.
- **Say:** "Source-grounded AI that still works with AI off, three honest scores on
  both devices, and two-way sync — all on the shared Rust engine that shipped
  Wednesday. That's what's new in Speedrun this week."

---

## Friday required-proof checklist

- [ ] ⭐ AI eval numbers + beats-a-baseline comparison (+ still scores with AI
      off) — Scenes B, D
- [ ] ⭐ A review synced **phone ↔ desktop** (offline → reconnect, no lost/
      double-counted reviews) — Scene F
- [ ] Free-text / production review loop — Scene C
- [ ] Three honest scores with ranges + give-up rule — Scene D (desktop), E (phone)
- [ ] Commit hash on screen — Scene B

## Pre-recording checklist

- [ ] On your latest pushed `main` (show the hash).
- [ ] `eval-report.md` present and **PASS** (run the pipeline first — see AI README).
- [ ] Desktop: a few reviews done so Progress shows both populated and "not enough
      data" states; **OpenAI key set in Settings → AI** for the AI scenes.
- [ ] Emulator: APK rebuilt (`assemblePlayDebug`) + installed; MCAT deck present.
- [ ] Both apps signed into the **same sync account** (AnkiWeb or self-hosted) and
      synced once so they share the deck (Scene F).
- [ ] GitHub Release open with `.msi` + `.apk` (Scene G).
- [ ] Screen recorder + mic tested; notifications silenced; **OpenAI key / AnkiWeb
      password NOT on screen**.

## Gotchas that will bite on camera

- **The deck auto-loads on first run** (desktop) — no manual import step.
- **Android is a separate collection until you sync** — Scene F unifies them.
- **Rebuild the `.apk`** from the current commit so it has the new UI + scores.
- **`ANKI_TEST_MODE=1`** if you re-run pytest by hand (interval-fuzz flake).
- **Don't show the OpenAI key or AnkiWeb password** on camera.

## Talking points / thesis (for the judge)

> - **AI safe by construction** — source-grounded generation, a pre-registered eval
>   gate (beats a baseline + confusion matrix, FN capped), and a clean AI-off fallback.
> - **Three intentionally humble scores** — Memory / Performance / Readiness, each a
>   range with a give-up rule, on the real 472–528 scale, on both devices.
> - **Sync reuses Anki's own server** — reviews keyed by ms timestamp + insert-or-
>   ignore, so they can't be lost or double-counted.
> - **One engine, two platforms** — scheduler + scores in the shared Rust core.

---

## Appendix — scenes for the full Sunday video (reuse)

These were **Wednesday's** proofs (and Sunday re-shows the installs on clean
devices). Keep them for the fuller Sunday cut — **not needed in the Friday video.**

### Clean build + tests + commit hash

> **Close every running Anki / `just run` first** — a running instance holds
> `_rsbridge.pyd` and makes `just check` fail on the file-copy step (an OS lock,
> not a code error).

- `git log -1 --oneline` (hash) → `git status` (clean) → `just check` → **`Build
  succeeded`** / exit 0.
- **Say:** "Clean tree, full build and checks pass — Rust, Python, TypeScript,
  lints, and the scheduler's own tests."

### The codebase change — one shared Rust engine

- **Show:** `rslib/src/scheduler/queue/builder/interleaving.rs` —
  `weighted_round_robin_by_topic`. Overlay: **Rust core → PyO3 → Desktop** and
  **Rust core → JNI → AnkiDroid**.
- **Say:** "When interleaving is on we deal the day's gathered cards round-robin
  across MCAT topics, optionally weighting toward weak topics. It's a pure
  reordering — never touches due dates, intervals, or FSRS state — and it's in the
  shared engine, so desktop and Android run the exact same code."

### Interleaving in action

- **Desktop:** **Settings → Study → Interleave topics** (+ **Weight by weakness**).
  Study; topics rotate **Bio → Chem → Psych**; toggle off → same-topic blocks
  return. **Phone:** **⋮ overflow → "Interleave MCAT topics"**.

### Clean-machine install (also a Sunday proof)

- **Fresh** Windows VM (no dev toolchain): double-click
  `anki-26.05-win-x64.msi` → installs → launch → opens to the app. Rebuild the
  `.msi` from the **current** build so it includes the new UI + AI. Android: install
  the `.apk` (`adb install -r AnkiDroid-play-x86_64-debug.apk` for emulator, or an
  arm64 build sideloaded on a phone).

### Automated verification table (paste into submission notes)

| Check                    | Command                                   | Result         |
| ------------------------ | ----------------------------------------- | -------------- |
| Full build + lints       | `just check` (Anki closed)                | green / exit 0 |
| Rust core lib tests      | `just test-rust`                          | pass           |
| Python (pylib) suite     | `just test-py`                            | pass           |
| Interleaving unit/integ. | `cargo test -p anki --lib interleaving`   | pass           |
| AI subsystem tests       | `qt/tests/test_speedrun_ai.py`            | 22 passed      |
| AI eval gate             | `docs/speedrun/ai/eval-report.md`         | **PASS**       |

### Android rebuild (before recording Scene E/F)

The backend submodule is already bumped to a scores-capable engine commit and the
`.aar` is built, so you normally only need **step 3** (rebuild the APK). Re-do
steps 1–2 only if you re-bump the engine:

```bash
# 1) (only if re-bumping) init the bumped engine submodule
cd Speedrun-Android-Backend && git submodule update --init anki
# 2) (only if re-bumping) rebuild the rsdroid .aar (NDK/cargo-ndk; long native build)
./gradlew :rsdroid:assembleRelease
# 3) build the APK against the local backend
cd ../Speedrun-Android && echo "local_backend=true" >> local.properties
./gradlew assemblePlayDebug   # x86_64 emulator; use an arm64 variant for a phone
```
