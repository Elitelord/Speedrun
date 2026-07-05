# Speedrun AI — CARS generation

CARS (Critical Analysis & Reasoning Skills) is the fourth MCAT section, and it is
_reasoning_, not recall: a ~500-600 word humanities/social-science passage plus
single-best-answer questions. This is a parallel, grounded, eval-gated generation
track alongside the recall-card pipeline in the parent folder.

## Why the grounding gate is different

The recall pipeline grounds a card by lexical overlap with its source chunk. That
is the wrong tool for CARS — a good inference question is deliberately _not_ a
word-for-word echo of the passage. So a CARS question is **supported** only if an
**independent** model re-read of the passage (given only the passage, stem, and
options) selects the keyed answer. That single check enforces two things at once:
the question is answerable _from the passage alone_ (no outside knowledge), and
the key is the single best answer. Questions that fail are blocked.

## Pipeline

```
python -m aqt.speedrun_ai.pipeline cars-generate   # draft passages + MC questions, grounded
python -m aqt.speedrun_ai.pipeline cars-eval       # gate vs pre-registered cars-cutoff.json
python -m aqt.speedrun_ai.pipeline cars-emit       # write eval-passed units for the deck
```

- `cars-eval` also runs as `just cars-eval` (needs `OPENAI_API_KEY`). It writes
  `cars-eval-report.md` + `cars-eval-result.json` and exits non-zero on failure.
- The **pre-registered cutoff** is `cutoff.json` (committed before results, git
  history is the proof): positive class = _bad question_, and the dangerous cell —
  a bad reasoning item shipped as good (false negative) — is capped.
- The offline `FakeClient` (`--fake`) produces zero units and cannot pass the
  reasoning eval; the real gate needs a key. This is the AI-off invariant.

## Data

- `source/*.txt` — named CC BY-SA humanities/social-science sources the passages
  are grounded in; `sources.json` maps each to the `mcat::cars` topic.
- `gold.jsonl` — hand-authored good/bad CARS questions (each self-contained with
  its passage) for the answer-key-correctness confusion matrix.
- `generated/units.json` — eval-passed units emitted for the deck builder.

## Into the deck and the app

`seed-deck/build_cars.py` creates a custom **"CARS (multiple choice)"** notetype
(Passage / Question / A–D / Answer / Explanation / Source) and `build_apkg.py`
folds the emitted units into the single `MCAT.apkg`, tagged `mcat::cars`. Because
`mcat::cars` is one of the four default MCAT topics, CARS then lights up as the
fourth section on the Progress page (coverage can reach 4/4) and interleaving
mixes CARS with the sciences.
