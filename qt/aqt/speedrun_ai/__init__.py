# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI subsystem (desktop-only).

Cloud LLM features for the MCAT fork: grounded card generation and free-text
answer grading, both backed by OpenAI. Everything degrades cleanly when the key
is absent, the ``ai`` extra isn't installed, or the network is down — callers
check :func:`ai_enabled` / treat a ``None`` client as "AI off", and any live
failure surfaces as :class:`AiUnavailable`.
"""

from __future__ import annotations

from .client import AiUnavailable, GradeResult, OpenAIClient
from .config import get_config

__all__ = [
    "AiUnavailable",
    "GradeResult",
    "OpenAIClient",
    "ai_enabled",
    "get_client",
    "grade",
    "set_ai_enabled",
]

# Master on/off switch, driven by the app's settings (per-profile). When off,
# every AI feature degrades to its non-AI path regardless of the key.
_ai_enabled_override: bool = True


def set_ai_enabled(enabled: bool) -> None:
    global _ai_enabled_override
    _ai_enabled_override = enabled


def ai_enabled() -> bool:
    """True if AI features are switched on AND a usable OpenAI key is configured.
    Feature-specific toggles (e.g. the reviewer's production-mode flag) are
    checked separately at their call sites; this is the single "is AI usable at
    all" gate."""
    return _ai_enabled_override and get_config().has_key


def get_client() -> OpenAIClient | None:
    """Return a shared client, or ``None`` when AI is off/unavailable. Never
    raises — a ``None`` return is the signal to take the non-AI path."""
    if not ai_enabled():
        return None
    try:
        return OpenAIClient()
    except AiUnavailable:
        return None


def grade(
    question: str,
    expected: str,
    typed: str,
    rubric: str = "",
    source: str = "",
) -> GradeResult:
    """Grade a free-text answer. Raises :class:`AiUnavailable` when AI is off or
    the call fails, so the reviewer's background-op failure handler can fall
    back to the classic self-graded flip."""
    client = get_client()
    if client is None:
        raise AiUnavailable("AI is disabled or unavailable")
    return client.grade(question, expected, typed, rubric, source)
