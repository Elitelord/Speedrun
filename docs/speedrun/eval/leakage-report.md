# Speedrun — leakage check (§7e)

**Result: CLEAN ✅**

A gold item is flagged as a near-copy when ≥ 50% of its word 4-grams also appear in the source text it is graded against (and, for CARS, its passage). Near-copies would let a keyword baseline win by lexical echo and would mean the test item leaked from the generation corpus.

| track | gold items | flagged | max overlap | mean overlap | verdict |
| --- | --- | --- | --- | --- | --- |
| recall cards | 36 | 0 | 0.235 | 0.013 | clean |
| CARS questions | 12 | 0 | 0.143 | 0.012 | clean |

Low overlap confirms the gold queries are genuine paraphrases (learner phrasing), so the retrieval beat-a-baseline result and the eval are not artifacts of copied text.

_Method: `docs/speedrun/eval/leakage.py` · re-run with `just leakage`._
