# Speedrun — Final Demo Video Script (Sunday)

> **One video, 3–5 minutes.** Goal per the mentor: _show the product, not just the
> idea, and make it easy to verify what's built._ So this is a product-first
> walkthrough of the full experience, then a tight evidence montage where every
> claim is a re-runnable command, then sync + clean-device installs.
>
> **Reference commit:** show your latest pushed `main` hash on camera (push the
> engine + Android app first). Upload to YouTube (Unlisted) or Vimeo; paste the
> link in the submission. **Never show your OpenAI key or AnkiWeb password.**

## What changed since the MVP (say this up front, prove it throughout)

- **CARS module** — grounded passage + multiple-choice _reasoning_ generation, its
  own eval gate, a custom notetype, wired in as the 4th MCAT section.
- **Free-text grading, upgraded** — the LLM now suggests the grade
  (Again/Hard/Good/Easy), feedback never leaks the answer, reveal shows the answer
  cleanly, and there's a feedback card + suggested-grade pill, bigger buttons, and a
  deck progress bar.
- **Evidence you can re-run** — memory **calibration** (Brier/log-loss + reliability
  chart), the interleaving **ablation** (3 builds), the **leakage** check, and the
  AI + CARS **eval gates**, each a single `just` command.

## Running order (~5 min)

| Time      | Scene | Beat                                                                              | Rubric proof                                     |
| --------- | ----- | --------------------------------------------------------------------------------- | ------------------------------------------------ |
| 0:00–0:20 | A     | Hook: one Rust engine, two apps, honest scores                                    | —                                                |
| 0:20–1:20 | B     | Review session: free-text grading + CARS                                          | AI review loop, product                          |
| 1:20–1:55 | C     | The Rust change in action: interleaving                                           | Rust change, learning science                    |
| 1:55–2:35 | D     | Three honest scores + AI-off                                                      | scores + ranges + give-up                        |
| 2:35–3:40 | E ⭐  | Evidence montage (commit, check, evals, baseline, leakage, calibration, ablation) | AI safety, re-runnable tests, honest uncertainty |
| 3:40–4:30 | F ⭐  | Two-way sync phone ↔ desktop                                                      | one engine + sync                                |
| 4:30–4:55 | G ⭐  | Clean-device installs (.msi + .apk)                                               | runs on clean device                             |
| 4:55–5:10 | H     | Close                                                                             | —                                                |

---

## Scene A — Hook (0:20)

- **Show:** Title "Speedrun — an MCAT study app on Anki's engine." Split screen:
  desktop + Android emulator on the MCAT deck.
- **Say:** "Speedrun is an MCAT study app I forked from Anki. One shared Rust engine
  drives both desktop and phone: it interleaves topics, computes three honest
  readiness scores, and grades free-text answers with a source-grounded LLM. Let me
  show it, then prove it."

## Scene B — Review session: free-text grading + CARS (0:20–1:20)

_The product. Show it working._

- **Show:**
  1. Start reviewing the MCAT deck. A **type-in** card: **type an answer → the LLM
     grades it by meaning** → the **feedback card** appears with a **suggested grade
     pill** (Again/Hard/Good/Easy). A wrong attempt gets a **hint that doesn't give
     the answer away** → re-attempt → reveal shows the answer **cleanly** (no
     red/green diff). The **deck progress bar** ticks up at the top.
  2. A **CARS** card: a passage + **multiple-choice** reasoning question; reveal
     shows the correct option + explanation.
- **Say:** "Instead of flipping a card, you _produce_ the answer and an LLM grades it
  by meaning — and it suggests the grade, so the card comes back at the right time.
  CARS is different: a generated passage with multiple-choice reasoning questions,
  the fourth MCAT section. Both are new since the MVP."

## Scene C — The Rust change in action: interleaving (1:20–1:55)

- **Show:** **Settings → Study → Interleave topics** on (tags include
  `mcat::biobiochem/chemphys/psychsoc/cars`). Study; topics **rotate** Bio → Chem →
  Psych → CARS. Toggle **Weight by weakness**; note weak topics come up more while a
  new section still gets in. Briefly show `interleaving.rs`.
- **Say:** "The core engine change: when interleaving is on, the day's cards are
  dealt round-robin across MCAT topics, optionally weighted toward your weak ones.
  It's a pure reordering — never touches due dates or FSRS state — and it lives in
  the shared Rust engine, so the phone runs the exact same code."

## Scene D — Three honest scores + AI-off (1:55–2:35)

- **Show:**
  1. **Progress** page: **Memory / Performance / Readiness**, each a **range**, with
     **per-section bars**, the **Readiness total on 472–528** + **coverage (N/4
     sections)**, and the **"not enough data"** give-up state on sections you
     haven't studied enough.
  2. **AI-off:** Settings → **Enable AI = off** → review a type-in card → it falls
     back to the **native self-graded reveal**, and the three scores **still
     compute**.
- **Say:** "Three separate scores, never one blended number — each a range with a
  rule that says 'not enough data' instead of faking confidence. Readiness is an
  honest projection on the real scale, and I'm explicit that it's not calibrated to
  practice-test data. And every AI feature degrades cleanly — turn AI off and the app
  still grades and still scores."

## Scene E ⭐ — Evidence montage (2:35–3:40)

_This is the mentor's ask: make it verifiable. Terminal, one command per claim._

- **Show, briefly, in a terminal:**
  1. `git log -1 --oneline` → your pushed hash; `git status` clean.
  2. `just check` → **green / exit 0** (Rust + Python + TS + lints + tests). _(Have
     this pre-run; show the tail.)_
  3. `cat docs/speedrun/ai/eval-report.md` → **PASS**: **beats the baseline**
     (RAG top-1 **1.000** vs BM25 **0.944**, MRR 1.000 vs 0.968) + the 2×2 matrix
     (**FN=0**).
  4. `cat docs/speedrun/ai/cars/cars-eval-report.md` → CARS **PASS** (FN=0).
  5. `just leakage` → **CLEAN** (max n-gram overlap 0.24 — gold isn't copied from
     the source, so the baseline win is real).
  6. `just calibration` → reliability table + **Brier / log-loss / ECE**, open
     `calibration.svg`. Note it's a **labelled real+simulated hybrid** (no
     longitudinal data yet — honest).
  7. `just ablation` → interleaving **3-build** table (on / off / plain), a
     **pre-registered** metric, a confusability sweep with an honest **null at c=0**.
- **Say:** "Everything is one command. The AI is source-grounded and gated by a
  cutoff I committed before seeing results — zero bad cards ship, and it beats a
  keyword baseline. The leakage check proves that win isn't from copied text. Memory
  is calibrated with Brier and log-loss; the interleaving study feature is tested
  with three builds and a pre-registered metric — and I report the null, not just the
  win."

## Scene F ⭐ — Two-way sync (3:40–4:30)

> Full detail in [`SYNC.md`](./SYNC.md). Reuses Anki's own sync.

- **Setup (before recording):** both apps signed into the **same sync account**
  (AnkiWeb simplest); sync once so they share the deck. **Don't show the password.**
- **Show:**
  1. Both devices on the MCAT deck, **matching due counts**.
  2. **Android → airplane mode**; **review several cards offline**.
  3. On **desktop**, review a few _different_ cards.
  4. **Reconnect Android → Sync**, then **Sync desktop**.
  5. Both reconcile to the **exact same state** — the phone's reviews on desktop and
     vice-versa, nothing lost or double-counted.
- **Say:** "No new sync code — I reuse Anki's own sync. Reviews are keyed by their
  millisecond timestamp and merged insert-or-ignore, so a review can't be
  double-counted. Offline on the phone, different cards on desktop, reconnect — both
  reconcile to the same state."

## Scene G ⭐ — Clean-device installs (4:30–4:55)

- **Show:** on a **fresh** Windows machine (no dev toolchain), double-click
  `anki-26.05-win-x64.msi` → installs → launches to the app. Then the Android
  `.apk` installing/running on the emulator (or a phone).
- **Say:** "Both apps install and run on a clean device from the GitHub Release."

## Scene H — Close (4:55–5:10)

- **Show:** GitHub Release page (`.msi` + `.apk`), then title card.
- **Say:** "Source-grounded AI that still works with AI off, three honest scores on
  both devices, interleaving in the shared Rust engine, and everything verifiable in
  one command. That's Speedrun."

---

## Rubric proof checklist (map to §11–12)

- [ ] ⭐ Rust change in action + its tests — Scene C, E (`cargo test … interleaving`)
- [ ] ⭐ AI eval + **beats a baseline** + FN-capped matrix — Scene E
- [ ] ⭐ **Leakage** check clean — Scene E
- [ ] ⭐ Memory **calibration** (Brier/log-loss + chart) — Scene E
- [ ] ⭐ Study-feature **ablation**, 3 builds, pre-registered, reports the null — Scene E
- [ ] ⭐ Three honest scores with ranges + give-up rule — Scene D (both devices)
- [ ] ⭐ Two-way **sync**, offline → reconnect, no lost/double-count — Scene F
- [ ] ⭐ Runs on a **clean device** (both apps) — Scene G
- [ ] AI-off still gives a score — Scene D
- [ ] Commit hash on screen — Scene E

## Pre-recording checklist

- [ ] On your latest pushed `main` (show the hash); `git status` clean.
- [ ] `just check` pre-run green (close any running Anki first — it locks the
      Rust binding the copy step touches).
- [ ] Reports present + passing: `ai/eval-report.md`, `ai/cars/cars-eval-report.md`,
      `eval/leakage-report.md`, `eval/calibration-report.md`, `eval/ablation-report.md`
      (run `just cars-eval`, `just leakage`, `just calibration`, `just ablation`; AI
      evals need `OPENAI_API_KEY`).
- [ ] Desktop: import `MCAT.apkg`; set the MCAT deck **New cards/day high** and add
      **`mcat::cars`** to interleave tags; study enough that at least 2 sections show
      scores and one section shows the give-up state (best of both on screen).
- [ ] Emulator: APK rebuilt + installed; MCAT deck present.
- [ ] Both apps on the **same sync account**, synced once (Scene F).
- [ ] Screen recorder + mic tested; notifications off; **no OpenAI key / AnkiWeb
      password on screen**.

## Gotchas that will bite on camera

- **Add `mcat::cars` to the interleave tags** or CARS trails to the end and won't
  appear in rotation; also raise **New cards/day** so all sections gather.
- **Failed cards (Again) recycle as learning cards before new cards** — if you've
  been failing a lot, clear that backlog or start fresh so CARS/new cards flow.
- **Rebuild the `.msi` and `.apk`** from the current commit so they include the new
  UI, CARS, and scores.
- **Close Anki before `just check`** (file-lock, not a code error).
- **`ANKI_TEST_MODE=1`** if you re-run pytest by hand (interval-fuzz flake).

## Automated verification table (paste into submission notes)

| Check                         | Command                                     | Result                   |
| ----------------------------- | ------------------------------------------- | ------------------------ |
| Full build + lints + tests    | `just check` (Anki closed)                  | green / exit 0           |
| Rust core lib tests           | `just test-rust`                            | pass                     |
| Python (pylib) suite          | `just test-py`                              | pass                     |
| Interleaving unit/integ.      | `cargo test -p anki --lib interleaving`     | 5 pass                   |
| AI + CARS subsystem tests     | `qt/tests/test_speedrun_{ai,cars}.py`       | pass                     |
| AI eval gate (beats baseline) | `docs/speedrun/ai/eval-report.md`           | **PASS**                 |
| CARS eval gate                | `docs/speedrun/ai/cars/cars-eval-report.md` | **PASS**                 |
| Leakage check                 | `just leakage`                              | **CLEAN**                |
| Memory calibration            | `just calibration`                          | Brier/log-loss + chart   |
| Interleaving ablation         | `just ablation`                             | 3 builds, pre-registered |

## Android rebuild (before recording Scenes F/G)

```bash
# 1) (only if re-bumping the engine) init the bumped submodule
cd Speedrun-Android-Backend && git submodule update --init anki
# 2) (only if re-bumping) rebuild the rsdroid .aar (NDK/cargo-ndk; long native build)
./gradlew :rsdroid:assembleRelease
# 3) build the APK against the local backend
cd ../Speedrun-Android && echo "local_backend=true" >> local.properties
./gradlew assemblePlayDebug   # x86_64 emulator; arm64 variant for a phone
```
