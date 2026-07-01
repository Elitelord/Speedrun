# Post-MVP Roadmap — Speedrun (Friday & Sunday gates)

> Companion to [`prd.md`](./prd.md). The MVP is the assignment's **Wednesday
> no-AI core**. This file captures everything deliberately deferred past
> Wednesday — the **Friday** (AI + two-way sync) and **Sunday** (proofs + ship)
> gates — plus the **locked decisions** that shape them. Fold these sections into
> `prd.md` after the Wednesday submission as they are built.
>
> Source of truth for requirements: [`Speedrun_ A Desktop + Mobile Study App
> Built on Anki.md`](./Speedrun_%20A%20Desktop%20+%20Mobile%20Study%20App%20Built%20on%20Anki.md).
> Research / POVs: [`Speedrun_Brainlift_MCAT.md`](./Speedrun_Brainlift_MCAT.md).

## Locked decisions (carry forward into the PRD)

| Decision         | Choice                                                                                                                      | Rationale                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **MVP boundary** | MVP = Wednesday no-AI core only; all of the below is post-MVP.                                                              | Sequences scope by the assignment's phase gates.                              |
| **Rust change**  | Topic-aware **interleaving scheduler**.                                                                                     | Doubles as the learning-science **study feature** we ablation-test (SPOV #1). |
| **CARS**         | **Post-MVP**; built as seeded/importable passages first, later feeds the **Performance** signal.                            | Brainlift SPOV #2; CARS is reasoning, not memorization.                       |
| **Frontend**     | Stay on Anki's **Svelte + TS** stack; add new components only.                                                              | Max reuse, desktop/Android parity, lowest risk.                               |
| **AI provider**  | **Cloud LLM API** (OpenAI/Anthropic) + **RAG-style grounding** over MCAT source text, with a rule/keyword baseline to beat. | Brief requires named source, eval, beating a baseline, and AI-off operation.  |
| **Mobile**       | **Android** (AnkiDroid-based).                                                                                              | Windows dev host.                                                             |
| **Exam**         | **MCAT** (472–528; sections 118–132).                                                                                       | Stated up front in README/PRD.                                                |

---

## Friday gate — AI added & checked; phone syncs

### Desktop — AI (cloud API + grounding)

- **Card/question generation** from a real MCAT source (textbook chapter / notes)
  via a cloud LLM, with **RAG-style grounding**: every AI output **traces back to
  a named source**.
- **Pre-display eval gate:** accuracy + wrong-answer rate on a **held-out set**,
  with a **passing cutoff set before looking at results**; cards that fail are
  blocked.
- **Beat-a-baseline:** side-by-side showing the AI approach beats a **simpler
  method** (keyword or vector search).
- **AI-off invariant:** the app still gives a score with AI switched off; AI
  features turn off cleanly when the network/service is unavailable
  (offline, rate-limited, or broken output).
- Addresses **Brainlift SPOV #3** (uncalibrated LLMs mislead overconfident
  students): require sources, confidence, and explicit abstention.

### CARS practice module (seeded → AI later)

- Seeded/importable **CARS passages (≈500–600 words) + question sets** for the
  Critical Analysis & Reasoning section.
- Later contributes a **Performance** signal (reasoning accuracy), and becomes an
  AI-generation target once the grounding + eval harness exists.

### Performance model (the bridge from memory → new questions)

- Predict whether the student answers **held-out, exam-style questions** right,
  using topic mastery, question difficulty, timing, and coverage.
- **Paraphrase test (7d):** 30 cards × 2 reworded exam-style questions each;
  compare card recall vs. reworded-question accuracy and **report the gap** (if
  equal, performance is just copying memory).

### Mobile — sync

- **Two-way sync** desktop ↔ Android with **no lost or double-counted reviews**.
- **Offline review**, then sync on reconnect.
- Phone shows the **three scores with ranges** and follows the **give-up rule**.

### Readiness display (three honest scores)

- **Memory / Performance / Readiness** shown separately, each with a **range**,
  never one blended number. Readiness on the real MCAT scale, e.g.:
  > **Projected MCAT: 508** · Likely range 503–512 · Confidence: low (only 42% of
  > topics studied).
- Each score carries: point estimate, range, **% of exam covered**, a
  "how-sure" indicator, last-updated time, the **main reasons**, and the
  **give-up rule**.
- **Readiness give-up rule (draft):** _no readiness score until **≥200 graded
  reviews AND ≥50% topic coverage**._

---

## Sunday gate — prove it & ship both

### Models & evidence

- **Memory calibration:** calibration chart + **Brier or log-loss** on held-out
  reviews (when it says 80%, recall ≈ 80%).
- **Performance accuracy:** on held-out exam-style questions.
- **Score mapping:** method written down, **with a range** (honest about not
  having longitudinal practice-test data — per brief §9).
- **Study-feature ablation (interleaving), 3 builds, equal study time:**
  1. full app (interleaving **on**), 2. app with interleaving **off** (ablation),
  2. **plain unmodified Anki** (baseline). State the main metric **ahead of
     time**; report a range and **results that didn't work**.
     (Hypothesis: _interleaving raises accuracy on new mixed-topic questions at equal
     study time._)
- **Leakage check (7e):** script that flags any test item (or near-copy) in
  training data; show it's clean.
- **AI card check (7f):** 50-pair gold set; generate 50 cards from one source and
  report correct-and-useful / wrong / correct-but-bad-teaching counts against a
  pre-set cutoff. _(See Parked Idea #2 — report this as a 2×2 confusion matrix
  with TP/FP/TN/FN rates for the good/bad question classifier.)_

### Ship both

- **Desktop installer** + **packaged Android build** (signed APK, or sideload),
  both installing/running on **clean devices**.
- **Sync conflict handling:** same card reviewed on both devices offline →
  documented, correct **conflict-rule winner** (7b).
- **AI-off:** both apps run and still give a score with AI disabled.

### Reliability & performance targets (brief §10)

- Button press ack **p95 < 50 ms**; next card **p95 < 100 ms**; dashboard first
  load **p95 < 1 s**, refresh **p95 < 500 ms**; normal-session sync **< 5 s**;
  cold start **< 5 s desktop / < 4 s phone**; nothing freezes UI **> 100 ms**.
- **Zero corrupted collections** in the crash test (kill mid-review ×20 each
  platform).
- **One-command benchmark (7h):** e.g. `make bench` on a shared 50,000-card deck
  printing p50 / p95 / worst-case per action.
- **Coverage map (7c):** every official MCAT outline topic, marked covered or
  not, with **% covered** on the dashboard; abstain below the line.

### Hand-in (Sunday 10:59 PM CT)

- Public AGPL-3.0-or-later **GitHub fork** (Anki credit, exam stated up front,
  build instructions for both apps, architecture overview, Rust-change note,
  touched-files list).
- **Demo video (3–5 min):** review session, Rust change in action, phone→desktop
  sync, three scores with ranges, AI features, test results.
- **Model descriptions:** one page each (memory, performance, readiness) incl.
  give-up rule.
- **Brainlift.**

---

## Stretch (only if core is solid — brief §13)

- Real-time sync (<1 s, no manual sync); E2E-encrypted or conflict-free merge.
- 100,000 cards within speed targets, with profiling.
- Signed/notarized installers for macOS/Windows/Linux + store-ready phone build.
- Upstream a change into Anki/AnkiDroid, or publish an add-on.
- Knowledge-graph study planning **proven** to beat keyword + vector search.

---

## Parked ideas (revisit later — not yet scheduled)

> Captured so they aren't lost. Not assigned to a gate yet; pull into Friday/
> Sunday or a later milestone when revisited.

1. **Fluency-gated interleaving** _(enhancement to the interleaving scheduler)._
   Don't interleave a card/topic from the start — only begin mixing it into
   interleaved sessions **after it crosses a fluency threshold** (e.g., a minimum
   FSRS stability/retrievability or N successful reviews). Rationale: blocked
   practice first builds the initial representation; interleaving then strengthens
   discrimination + transfer. So the lifecycle is **block → (threshold) →
   interleave**. Open questions: what signal defines "fluent" (FSRS stability vs.
   review count vs. lapse-free streak), whether the threshold is per-card or
   per-topic, and how this interacts with the on/off toggle used in the ablation
   test. Lives in the same Rust queue-builder as the base interleaving feature.

2. **2×2 confusion matrix for LLM question-quality classification**
   _(enhancement to the AI card check, brief 7f)._ When validating generated
   questions, evaluate the **good/bad classifier** with a proper **2×2 confusion
   matrix** — true positive, false positive, true negative, false negative — and
   report the derived rates (precision/recall, FPR/FNR), not just raw counts.
   The most dangerous cell is a **false negative**: a wrong/bad question the
   classifier passed as good (a wrong fact is worse than no card). Set the
   accept/reject cutoff to control that cell explicitly. Ties to **Brainlift
   SPOV #3** (uncalibrated LLMs mislead) and the brief's eval-before-display +
   beat-a-baseline requirements.
