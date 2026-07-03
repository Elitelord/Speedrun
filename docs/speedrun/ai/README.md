# Speedrun AI — grounded card generation + eval gate

Desktop-only cloud-AI features for the MCAT fork. Card generation is a
reproducible pipeline (like `seed-deck/build_apkg.py`): chunk + embed a named
MCAT source, generate cards **grounded** in it, evaluate against a **held-out
gold set with a pre-registered cutoff**, and only then emit passing cards.

## What we built, why, and what we skipped (the Friday AI note)

**What we built.** Two AI features, both guarded the same way:

1. **Grounded card generation** — chunk + embed named MCAT sources (OpenStax
   CC-BY, Wikipedia CC-BY-SA), generate cards from a specific source chunk, and
   **block any card whose answer isn't supported by that source**. Every emitted
   card traces back to a named source.
2. **Free-text grading in review** — instead of a flip-card, the learner types an
   answer, an LLM grades it **by meaning**, a miss gets a scaffolded hint before
   the reveal, and reappearance is keyed to how it was answered. (Lives in the
   desktop reviewer; this pipeline is the generation + eval half.)

Both sit behind a **pre-display eval gate**: a held-out gold set, a cutoff
committed *before* any results (git history is the proof), a 2×2 good/bad-card
confusion matrix with the false-negative cell capped, and a **beat-a-baseline**
retrieval check (embeddings vs. BM25). Cards that fail don't ship.

**Why.** Producing an answer beats recognizing one (generation effect), and it
moves review closer to how the MCAT tests. The guardrails exist because the
dangerous LLM failure isn't silence — it's confident, ungrounded fabrication; so
every feature requires **source-grounding, held-out evaluation, and explicit
abstention**. Beating a keyword baseline is how we show the embedding retrieval
earns its added complexity rather than assuming it.

**What we skipped (and why).**

- **No open-ended chatbot / tutor** — hard to ground and evaluate; out of scope
  for a graded, safe-by-construction feature.
- **No fine-tuning, no vector DB** — a cloud API + a JSON embedding index and a
  numpy cosine pass are deterministic, dependency-light, and enough at this corpus
  size.
- **CARS passage generation & the AI performance model** — deferred to the Sunday
  gate / post-MVP (`POST_MVP_ROADMAP.md`); seeded content first.
- **No AI on the phone** — Android stays offline-first; AI is desktop-only.
- **AI is fully optional** — with **Enable AI** off (or no key / network down),
  generation and grading **abstain**, the reviewer falls back to the native
  self-graded reveal, and the three scores still compute.

## Setup

The AI features are an opt-in extra so the base app never pulls them. Install
the three packages into the built engine's venv (`out/pyenv`) — the environment
`just run` and the pipeline use:

```
uv pip install --python out/pyenv/Scripts/python.exe openai numpy rank_bm25
```

(`uv sync --extra ai` won't work: the extra is defined on the `aqt` workspace
member and `uv sync` targets a separate root `.venv`, not `out/pyenv`.)

Put your key in a repo-root `.env` (git-ignored):

```
OPENAI_API_KEY=sk-...
# optional overrides:
# OPENAI_MODEL=gpt-4o-mini
# OPENAI_EMBED_MODEL=text-embedding-3-small
```

## Run the pipeline

```
PYTHONPATH="pylib;out/pylib" out/pyenv/Scripts/python.exe \
    -m aqt.speedrun_ai.pipeline build-index    # chunk + embed docs/speedrun/ai/source/*
PYTHONPATH=... -m aqt.speedrun_ai.pipeline generate   # grounded drafts -> generated/drafts.json
PYTHONPATH=... -m aqt.speedrun_ai.pipeline eval        # writes eval-report.md + eval-result.json; exit 0/1
PYTHONPATH=... -m aqt.speedrun_ai.pipeline emit        # writes PASSING cards -> generated/<section>.tsv (only if eval passed)
```

Add `--fake` to any command to use the deterministic offline stub (no network,
no key) — this is what the CI test uses.

## What the eval gate measures (`eval-report.md`)

1. **Beat-a-baseline** — retrieval Recall@1 / @3 / @5 + MRR for the embedding RAG
   path vs. the BM25 keyword baseline on the gold set. The gold queries are phrased
   the way a **learner** would ask (paraphrased), not copied from the source, so a
   keyword baseline can't win by lexical echo. The AI path must clear the
   pre-registered `min_rag_minus_bm25_recall` margin. _Note: at k=5 a cleanly-
   separated corpus saturates (both find the source), so the discriminating point
   is **top-1**, where RAG ranks the correct source first for every query and BM25
   slips (RAG 1.000 vs BM25 0.944; MRR 1.000 vs 0.968). A larger, denser corpus
   would widen the gap — add more overlapping source text under `source/`._
2. **Good/bad card classifier (2×2 confusion matrix)** — the grounding gate is
   run over the labelled gold cards. Positive = _bad card_; the **false negative**
   (a wrong card shipped as good) is the dangerous cell and is capped explicitly
   by `max_false_negative_rate`.

## The pre-registered cutoff

`cutoff.json` is committed **before** any generation/eval run — git history is
the enforcement that the cutoff was set before looking at results. A run that
fails the cutoff makes `emit` refuse to write cards and exit non-zero, so a
fabricated fact cannot ship.

## Guardrails (Brainlift 4.5)

- **Source-grounding:** every card is generated from a named source chunk and
  auto-blocked if its answer isn't supported by that source, regardless of any
  LLM judgement.
- **Held-out evaluation:** the gold set is separate from generation and never
  used to tune the cutoff.
- **Abstention:** generation returns no card when the source doesn't support one;
  the shared grader abstains rather than inventing a grade.

## Files

- `source/*.txt` — named MCAT source text (drop in CC-BY OpenStax text for real
  runs; the committed samples are original factual prose).
- `sources.json` — manifest mapping each source file to its `name` + topic tag.
- `index.json` — embedding index (generated by `build-index`).
- `gold.jsonl` — held-out labelled gold set (`{front, back, source_name, label}`).
- `cutoff.json` — pre-registered accept/reject thresholds.
- `generated/` — `drafts.json` and the emitted per-section TSVs (passing cards).
- `eval-report.md` / `eval-result.json` — the run report + machine-checkable result.

Emitted TSVs are `front<TAB>back<TAB>source_name`; `seed-deck/build_apkg.py`
tags each card `mcat::<section>` (for interleaving) + `source::<slug>` (citation)
and uses a type-in notetype so the free-text review loop works on them.
