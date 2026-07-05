# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: the shared OpenAI client wrapper.

One :class:`OpenAIClient` is shared by both AI features (card generation and
free-text grading). The ``openai`` SDK is imported lazily inside ``__init__`` so
the base app never fails to start when the optional ``ai`` extra is missing.

Every network failure — missing SDK, missing key, timeout, rate-limit, or
malformed output — is funnelled into a single :class:`AiUnavailable` exception so
callers have exactly one thing to catch and degrade on. This is the mechanism
behind the "AI-off invariant": review and scoring flows never see anything but
``AiUnavailable``.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, cast

from .config import AiConfig, get_config

# Verdicts the grader may return; the reviewer maps these onto an FSRS ease.
VERDICT_CORRECT = "correct"
VERDICT_PARTIAL = "partial"
VERDICT_WRONG = "wrong"


class AiUnavailable(Exception):
    """Raised for any condition that means the AI cannot be used right now:
    no key, SDK not installed, network/timeout/rate-limit, or unusable output.
    Callers catch this and fall back to the non-AI path."""


@dataclass
class GradeResult:
    verdict: str  # one of VERDICT_*
    correct: bool
    ease: int | None  # 1-4 if the grader wants to force an ease, else None
    feedback: str  # short, shown to the learner
    hint: str  # conceptual nudge, must not reveal the answer
    abstained: bool = False  # the model declined to grade (ungrounded)


# Prompt for short-answer grading. The rubric/expected/source are all supplied
# so the critique stays grounded (Brainlift 4.5: no ungrounded feedback).
_GRADE_SYSTEM = (
    "You are an MCAT tutor grading a student's free-text answer. Grade ONLY "
    "against the provided expected answer and rubric — never introduce facts "
    "that are not supported by them. If the expected answer/rubric is empty or "
    "does not let you judge the response, abstain.\n"
    "Judge by MEANING, not exact wording. Be generous: if the student's answer "
    "names the same key terms or conveys the same core idea as the expected "
    'answer, mark it "correct" — ignore articles (a/the), plurals, word '
    "order, capitalisation, synonyms, brevity, and minor missing detail. A "
    "near-verbatim answer, or one that lists the same key terms, is ALWAYS "
    '"correct". Only use "partial" when a distinct required element is entirely '
    'missing, and "wrong" only when the answer is essentially incorrect or '
    "unrelated. When unsure between correct and partial, choose correct.\n"
    "Also suggest how well the student knew it, as a spaced-repetition grade so "
    "the card comes back at the right time — judge the ANSWER quality, not just "
    "right/wrong:\n"
    '  "easy"  = fully correct, complete, and confident/effortless;\n'
    '  "good"  = correct with the key idea, the normal pass;\n'
    '  "hard"  = essentially right but shaky, partial, or missing a detail;\n'
    '  "again" = wrong, unrelated, or blank.\n'
    "CRITICAL — do NOT give the answer away. The student may still be "
    "attempting, so neither 'feedback' nor 'hint' may state, paraphrase, spell "
    "out, or name the correct answer or any distinctive key term / proper noun / "
    "synonym from it. Comment only on the student's own attempt and point toward "
    "the underlying concept in general terms. If you cannot write a hint without "
    "naming the answer, make the hint an empty string.\n"
    'Return a compact JSON object with keys: verdict (one of "correct", '
    '"partial", "wrong"), grade (one of "again", "hard", "good", "easy"), '
    "feedback (one short sentence about THEIR attempt, never revealing the "
    "answer), hint (a conceptual nudge that does NOT contain the answer or its "
    "key terms; empty when verdict is correct or when any hint would give it "
    "away), abstain (boolean). Output JSON only."
)

# Map the grader's spaced-repetition grade onto an FSRS ease (1-4).
_GRADE_TO_EASE = {"again": 1, "hard": 2, "good": 3, "easy": 4}


class OpenAIClient:
    def __init__(self, config: AiConfig | None = None) -> None:
        self._config = config or get_config()
        if not self._config.has_key:
            raise AiUnavailable("no OPENAI_API_KEY configured")
        try:
            import openai  # type: ignore[import-not-found,import-untyped]
        except Exception as exc:  # SDK not installed (ai extra missing)
            raise AiUnavailable(f"openai SDK not available: {exc}") from exc
        self._openai = openai
        self._client = openai.OpenAI(
            api_key=self._config.api_key, timeout=self._config.timeout
        )

    # -- low level ---------------------------------------------------------

    def _with_retries(self, fn: Any, attempts: int = 3) -> Any:
        last: Exception | None = None
        for i in range(attempts):
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 - normalise everything
                last = exc
                # Exponential backoff; kept short so a wedged call still bails.
                time.sleep(min(2.0, 0.5 * (2**i)))
        raise AiUnavailable(f"OpenAI call failed after {attempts} attempts: {last}")

    def chat(self, messages: list[dict[str, str]], **opts: Any) -> str:
        def call() -> str:
            resp = self._client.chat.completions.create(
                model=self._config.chat_model,
                # The SDK's message param is a strict union; our plain dicts are
                # accepted at runtime, so widen the static type here.
                messages=cast("Any", messages),
                temperature=opts.pop("temperature", 0),
                **opts,
            )
            content = resp.choices[0].message.content
            if not content:
                raise ValueError("empty completion")
            return content

        return str(self._with_retries(call))

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        def call() -> list[list[float]]:
            resp = self._client.embeddings.create(
                model=self._config.embed_model, input=texts
            )
            return [list(d.embedding) for d in resp.data]

        return list(self._with_retries(call))

    # -- shared grading ----------------------------------------------------

    def grade(
        self,
        question: str,
        expected: str,
        typed: str,
        rubric: str = "",
        source: str = "",
    ) -> GradeResult:
        if not expected.strip():
            # Nothing to ground the grade in -> abstain rather than invent one.
            return GradeResult(VERDICT_WRONG, False, None, "", "", abstained=True)
        user = json.dumps(
            {
                "question": question,
                "expected_answer": expected,
                "rubric": rubric,
                "source": source,
                "student_answer": typed,
            }
        )
        raw = self.chat(
            [
                {"role": "system", "content": _GRADE_SYSTEM},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        return parse_grade(raw)


def parse_grade(raw: str) -> GradeResult:
    """Parse the grader's JSON reply into a :class:`GradeResult`. Malformed
    output is treated as an abstention rather than a crash."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return GradeResult(VERDICT_WRONG, False, None, "", "", abstained=True)
    if data.get("abstain"):
        return GradeResult(VERDICT_WRONG, False, None, "", "", abstained=True)
    verdict = str(data.get("verdict", VERDICT_WRONG)).lower()
    if verdict not in (VERDICT_CORRECT, VERDICT_PARTIAL, VERDICT_WRONG):
        verdict = VERDICT_WRONG
    ease = _GRADE_TO_EASE.get(str(data.get("grade", "")).lower())
    return GradeResult(
        verdict=verdict,
        correct=verdict == VERDICT_CORRECT,
        ease=ease,
        feedback=str(data.get("feedback", "")),
        hint=str(data.get("hint", "")),
        abstained=False,
    )


class FakeClient:
    """Deterministic, network-free stand-in used by tests and the CI eval
    fixture. Embeddings are hashed bag-of-words vectors (stable across runs);
    grading is a trivial token-overlap heuristic."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            vec[hash(token) % self.dim] += 1.0
        return vec

    def chat(self, messages: list[dict[str, str]], **opts: Any) -> str:
        return "{}"

    def grade(
        self,
        question: str,
        expected: str,
        typed: str,
        rubric: str = "",
        source: str = "",
    ) -> GradeResult:
        if not expected.strip():
            return GradeResult(VERDICT_WRONG, False, None, "", "", abstained=True)
        exp = set(expected.lower().split())
        got = set(typed.lower().split())
        overlap = len(exp & got) / max(1, len(exp))
        if overlap >= 0.85:
            return GradeResult(VERDICT_CORRECT, True, 4, "Correct.", "")
        if overlap >= 0.6:
            return GradeResult(VERDICT_CORRECT, True, 3, "Correct.", "")
        if overlap >= 0.25:
            return GradeResult(
                VERDICT_PARTIAL,
                False,
                2,
                "Partly right.",
                "Reconsider the key term.",
            )
        return GradeResult(
            VERDICT_WRONG, False, 1, "Not quite.", "Think about the core concept."
        )
