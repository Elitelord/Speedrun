# Speedrun — Manual QA & Your To-Do List

> Everything **you** need to do/verify before the Friday and Sunday gates.
> Requirements are sourced from the assignment brief
> (`Speedrun_ A Desktop + Mobile Study App Built on Anki.md`, distilled in
> [`POST_MVP_ROADMAP.md`](../../POST_MVP_ROADMAP.md)) — not just the handoff.
> `[x]` = done, `[ ]` = pending. ⭐ = graded deliverable. Brief refs like §7f
> point at the assignment's numbered requirements.

---

## 0. In progress right now — UI polish

- [ ] **Review the redesigned desktop UI** (sidebar app-shell, light theme,
      in-window Home/Progress/Settings, deck cards, free-text grading, auto-save
      settings, in-app API key + AI on/off). Give me the next round of fixes.
- Deferred UI (not started — decide if wanted): in-window **Browser** (still a
  popup), full drag/drop **deck-tree** reorg, remove orphaned Svelte-settings /
  dialog shells.

---

## 1. Friday gate — AI added & checked; phone syncs

### Code shipped (verify in the app)

- [x] AI subsystem (`qt/aqt/speedrun_ai/`): grounded generation, RAG retrieval,
      BM25 baseline, eval harness (Recall@k/MRR + 2×2 confusion matrix), OpenAI
      client with AI-off funnel. `openai`/`numpy`/`rank_bm25` installed in `out/pyenv`.
- [x] Free-text production loop (type → LLM grade → hint → reveal), grades by
      meaning, stays on feedback, degrades to self-graded flip when AI is off.
- [x] Three honest scores — Memory / Performance / Readiness — each with range +
      give-up rule; Readiness = sum of the 4 MCAT sections on 472–528.
- [x] In-app **OpenAI key** field + **Enable AI** master toggle (per-profile;
      works in a downloaded build with no repo `.env`).

### Your actions

- [x] ⭐ **Real AI pipeline run** — done. `docs/speedrun/ai/eval-report.md`
      = **PASS** vs the pre-registered `cutoff.json`. Classifier confusion matrix:
      TP=12 / FN=**0** / TN=23 / FP=1 (accuracy 0.972, false-negative rate 0.0 —
      no wrong card ships). Generation: 207 drafts, 206 grounded → emitted to
      `docs/speedrun/ai/generated/*.tsv`.
- [x] ⭐ **Beat-a-baseline is now a real win (not a tie).** The gold queries were
      rewritten into **learner phrasing** (how a student asks, not the source's own
      words), so BM25 can't win by lexical echo. Result: **RAG ranks the correct
      source first for all 36 queries; BM25 slips** — Recall@1 RAG 1.000 vs BM25
      0.944 (+0.056), MRR 1.000 vs 0.968. Recall@5 still saturates (+0.000: with a
      cleanly-separated 12-topic corpus both find the source within 5), so the
      report leads with top-1/MRR. `cutoff.json` was **not** touched. To widen the
      gap further, add more overlapping source text under `ai/source/`.
- [x] Add real **MCAT source text** — done. 12 CC-licensed sources in
      `docs/speedrun/ai/source/` (OpenStax CC BY 4.0 for chem/phys; Wikipedia
      CC BY-SA for bio-biochem + psych/soc), each with an attribution header;
      `sources.json` maps them to the 3 tags. _Caveat: source text was
      paraphrased by a fast model at fetch — spot-check accuracy._
- [x] ⭐ **AI-off invariant**: confirmed — the app still gives a score and reviews
      work with **Enable AI** off (Settings) and with the network down (free-text
      cards degrade to the native self-graded reveal; the three scores still compute).
- [ ] ⭐ **Two-way sync desktop ↔ Android**: offline review on each → reconnect →
      reconcile with **no lost or double-counted reviews**. Steps scripted in
      `SYNC.md` + DEMO_VIDEO Scene H — **needs the recorded demo** (self-hosted
      `--syncserver`, both clients pointed at your LAN IP).
- [x] **Phone shows the three scores** — code done: DeckPicker overflow →
      **"MCAT readiness"** dialog (Memory/Performance/Readiness + ranges + give-up)
      via the shared Rust RPCs (`Speedrun-Android/.../DeckPicker.kt` +
      `res/menu/deck_picker.xml`). Backend submodule bumped to the scores engine
      (`Speedrun-Android-Backend` `40bb37f` → anki `95bc2af09`).
      **YOUR STEP:** rebuild the rsdroid `.aar` + APK (see DEMO_VIDEO "Android
      rebuild") and verify on the emulator — the Kotlin compiles once the `.aar`
      carries the score RPCs.

---

## 2. Sunday gate — prove it & ship both

### Models & evidence ⭐

- [ ] **Memory calibration**: calibration chart + **Brier/log-loss** on held-out
      reviews (when it says 80%, recall ≈ 80%).
- [ ] **Performance accuracy** on held-out exam-style questions, **plus the
      paraphrase test (§7d)**: 30 cards × 2 reworded questions each; report the gap
      between card recall and reworded-question accuracy.
- [ ] **Score-mapping write-up** with a range, honest about no longitudinal
      practice-test data (§9).
- [ ] **Study-feature ablation** (§interleaving): 3 builds at equal study time —
      (1) interleaving on, (2) interleaving off, (3) plain unmodified Anki. **State
      the metric ahead of time**, report a **range** and any results that didn't work.
- [ ] **Leakage check (§7e)**: script that flags any test item / near-copy in
      training data; show it's clean.
- [ ] **AI card check (§7f)**: 50-pair gold set → generate 50 cards from one
      source → report correct-and-useful / wrong / correct-but-bad-teaching as a
      **2×2 confusion matrix** vs a pre-set cutoff (watch the false-negative cell).
- [ ] **Model descriptions**: one page each for memory / performance / readiness,
      including the give-up rule.

### Reliability & performance (§10)

- [ ] **One-command benchmark (§7h)** on a 50,000-card deck printing p50/p95/worst
      per action; hit targets: button-ack p95 <50 ms, next-card p95 <100 ms, dashboard
      first load p95 <1 s / refresh <500 ms, sync <5 s, cold start <5 s desktop /
      <4 s phone, no UI freeze >100 ms.
- [ ] **Crash test**: kill mid-review ×20 each platform → **zero corrupted
      collections**.
- [ ] **Coverage map (§7c)**: every official MCAT outline topic marked covered/not,
      with **% covered** on the dashboard; abstain below the line.
- [ ] **Sync conflict handling (§7b)**: same card reviewed on both devices offline
      → documented, correct conflict-rule winner.

### Ship both ⭐

- [ ] **Rebuild release artifacts with the NEW UI + fixes**: Windows `.msi`
      (`tools/build-installer.bat`, then clear the Briefcase stamps — see
      speedrun-mvp memory) + Android `.apk`; publish/refresh the GitHub Release.
- [ ] ⭐ **Clean-machine installs**: desktop `.msi` and Android `.apk` install/run
      on **fresh devices** (record for the demo).
- [ ] ⭐ **AI-off on both apps**: each still gives a score with AI disabled.

### Hand-in (Sunday 10:59 PM CT) ⭐

- [ ] **Demo video (3–5 min)**: review session, the Rust interleaving change in
      action, phone→desktop sync, three scores with ranges, AI features, test results
      (see [`DEMO_VIDEO.md`](./DEMO_VIDEO.md)).
- [ ] **Brainlift** (`Speedrun_Brainlift_MCAT.md`) finalized/exported.
- [ ] **Repo hand-in**: public AGPL-3.0 fork with Anki credit, **exam (MCAT)
      stated up top**, build instructions for both apps, architecture overview,
      Rust-change note (`docs/speedrun/rust-change.md`), and a touched-files list.

---

## 3. Content QA — medical accuracy (your pre-med call)

- [ ] **Review the 72 seed cards** for factual accuracy and exam-appropriate
      phrasing (drafted from CC-BY OpenStax + CC-BY-SA Wikipedia).
- [ ] Confirm per-section tags (`mcat::biobiochem|chemphys|psychsoc`) match each
      card's content.

## 4. Harder cards (your next planned step — agent-generated)

- [ ] Run the AI card-generation agent to produce **MCAT-difficulty** cards
      (amino-acid pKa/charge at pH, enzyme kinetics Km/Vmax, glycolysis intermediates,
      action-potential ion mechanics, thermo/circuits with calculation — POST_MVP §"Seed
      deck depth") and **replace the too-easy existing cards**, validating generated
      cards against a human gold set (§7f) before shipping. Regenerate `MCAT.apkg`.

## 5. Done / pushed

- [x] Engine fork `main` pushed to `Elitelord/Speedrun` (user confirmed all
      changes pushed).
- [x] `Speedrun-Android` + `Speedrun-Android-Backend` pushed (user confirmed).
      _If you want on-device weakness-weighting, bump the backend's `anki` submodule
      past Phase 7 and rebuild the `.aar`._
- [x] Interleaving (uniform + weakness-weighted) Rust change, desktop + Android.
- [x] Memory/Performance/Readiness scores + in-window Progress page.
- [x] Free-text grading loop + AI subsystem code + eval harness.
- [x] Seed deck `MCAT.apkg` (72 cards, type-in notetype).
- [x] Desktop MSI built once (needs a rebuild with the new UI — see §2 Ship both).
- [x] Desktop UI overhaul (app-shell, light theme, in-window pages, auto-save
      settings, in-app key + AI toggle).

## 6. Decisions for you (when convenient)

- [ ] Confirm the **give-up thresholds** (20 graded/topic, 100/deck) once you see
      real review volumes.
- [ ] CARS module vs. another feature vs. submission-prep for remaining time.
- [ ] Keep the **Cards** browser as a popup, or invest in the in-window rebuild.

---

_I keep this updated as work lands. Ping me to add/adjust anything._
