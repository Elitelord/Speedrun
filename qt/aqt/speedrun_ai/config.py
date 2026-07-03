# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: configuration + secret loading.

The OpenAI API key is read from ``OPENAI_API_KEY`` (or the common
``OPEN_AI_API_KEY`` misspelling) in a repo-root ``.env`` file (git-ignored) or
the process environment. Nothing here imports the ``openai``
SDK or any part of ``aqt`` — it is deliberately dependency-free so it can be
imported (and unit-tested) without the optional ``ai`` extra installed and
without a running Qt app.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Optional overrides; sensible defaults so the .env only needs the key.
DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_EMBED_MODEL = "text-embedding-3-small"

# How long to wait on any single OpenAI call before giving up (seconds).
DEFAULT_TIMEOUT = 8.0


def _parse_dotenv(path: Path) -> dict[str, str]:
    """Parse a minimal ``KEY=VALUE`` .env file. Blank lines and ``#`` comments
    are ignored; surrounding quotes on the value are stripped. Deliberately tiny
    so we don't take a runtime dependency on python-dotenv."""
    out: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            out[key] = value
    return out


def _find_dotenv() -> Path | None:
    """Walk up from the cwd and from this file looking for a ``.env``."""
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    seen: set[Path] = set()
    for start in starts:
        for parent in [start, *start.parents]:
            if parent in seen:
                continue
            seen.add(parent)
            candidate = parent / ".env"
            if candidate.is_file():
                return candidate
    return None


def _env() -> dict[str, str]:
    """The effective environment: .env values overlaid by the real process
    environment (the real environment wins)."""
    values: dict[str, str] = {}
    dotenv = _find_dotenv()
    if dotenv is not None:
        values.update(_parse_dotenv(dotenv))
    values.update(os.environ)
    return values


@dataclass(frozen=True)
class AiConfig:
    api_key: str
    chat_model: str
    embed_model: str
    timeout: float

    @property
    def has_key(self) -> bool:
        return bool(self.api_key)


# A key set by the user in the app's settings (persisted per-profile). Takes
# precedence over the .env/environment so a downloaded build works without a
# repo-root .env. Set via :func:`set_api_key_override`.
_api_key_override: str = ""


def set_api_key_override(key: str) -> None:
    global _api_key_override
    _api_key_override = (key or "").strip()


def get_config() -> AiConfig:
    env = _env()
    # Precedence: user-entered key (settings) > OPENAI_API_KEY > the common
    # OPEN_AI_API_KEY misspelling. This keeps a mistyped env var from silently
    # falling back to self-grading, and lets a shipped build use an in-app key.
    api_key = (
        _api_key_override
        or env.get("OPENAI_API_KEY")
        or env.get("OPEN_AI_API_KEY")
        or ""
    ).strip()
    return AiConfig(
        api_key=api_key,
        chat_model=env.get("OPENAI_MODEL", DEFAULT_CHAT_MODEL).strip()
        or DEFAULT_CHAT_MODEL,
        embed_model=env.get("OPENAI_EMBED_MODEL", DEFAULT_EMBED_MODEL).strip()
        or DEFAULT_EMBED_MODEL,
        timeout=DEFAULT_TIMEOUT,
    )
