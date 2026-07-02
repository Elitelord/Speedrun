# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Tests for the Speedrun AI subsystem — all network-free and CI-safe.

Exercises the AI-off invariant (no key / disabled -> non-AI path, never a
crash), the .env parsing + env precedence, deterministic RAG retrieval and the
BM25 baseline via the FakeClient, and grade parsing/abstention.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import aqt.speedrun_ai as ai
from aqt.speedrun_ai import config as config_mod
from aqt.speedrun_ai import rag
from aqt.speedrun_ai.client import FakeClient, GradeResult, parse_grade
from aqt.speedrun_ai.config import AiConfig


def _cfg(key: str) -> AiConfig:
    return AiConfig(api_key=key, chat_model="m", embed_model="e", timeout=8.0)


# -- config / .env ---------------------------------------------------------


def test_parse_dotenv(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "# a comment\n\nOPENAI_API_KEY = sk-abc \nOPENAI_MODEL='gpt-x'\nBAD LINE\n",
        encoding="utf-8",
    )
    parsed = config_mod._parse_dotenv(env)
    assert parsed["OPENAI_API_KEY"] == "sk-abc"
    assert parsed["OPENAI_MODEL"] == "gpt-x"
    assert "BAD LINE" not in parsed


def test_env_wins_over_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config_mod, "_find_dotenv", lambda: None)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    assert config_mod.get_config().api_key == "sk-from-env"


def test_no_key_means_no_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config_mod, "_find_dotenv", lambda: None)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert config_mod.get_config().has_key is False


# -- AI-off invariant ------------------------------------------------------


def test_ai_disabled_when_no_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "get_config", lambda: _cfg(""))
    assert ai.ai_enabled() is False
    assert ai.get_client() is None


def test_grade_raises_when_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai, "get_config", lambda: _cfg(""))
    with pytest.raises(ai.AiUnavailable):
        ai.grade("q", "expected", "typed")


# -- grade parsing / abstention -------------------------------------------


def test_parse_grade_malformed_abstains() -> None:
    r = parse_grade("not json")
    assert r.abstained is True and r.correct is False


def test_parse_grade_explicit_abstain() -> None:
    assert parse_grade('{"abstain": true}').abstained is True


def test_parse_grade_normalises_verdict() -> None:
    r = parse_grade('{"verdict": "correct", "feedback": "yes", "hint": ""}')
    assert r.verdict == "correct" and r.correct is True
    bad = parse_grade('{"verdict": "banana"}')
    assert bad.verdict == "wrong" and bad.correct is False


def test_fake_grader_empty_expected_abstains() -> None:
    assert FakeClient().grade("q", "", "anything").abstained is True


def test_fake_grader_overlap() -> None:
    fc = FakeClient()
    assert fc.grade("q", "peptide bond", "peptide bond").correct is True
    assert fc.grade("q", "peptide bond", "banana split").correct is False


# -- chunking --------------------------------------------------------------


def test_chunk_text_ids_and_overlap() -> None:
    text = "\n\n".join(f"para {i} " + "word " * 100 for i in range(4))
    chunks = rag.chunk_text(text, "src", target_words=120, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0].chunk_id == "src#0"
    assert all(c.source_name == "src" for c in chunks)


# -- RAG retrieval (deterministic via FakeClient) --------------------------


def test_rag_retrieve_ranks_relevant_chunk_first() -> None:
    pytest.importorskip("numpy")
    fc = FakeClient()
    chunks = [
        rag.Chunk("s#0", "s", "glycolysis produces pyruvate and atp"),
        rag.Chunk("s#1", "s", "amino acids form peptide bonds in proteins"),
        rag.Chunk("s#2", "s", "the nephron filters blood in the kidney"),
    ]
    index = rag.build_index(chunks, fc)
    top = rag.retrieve("peptide bonds between amino acids", index, fc, k=1)
    assert top[0].chunk_id == "s#1"


# -- BM25 baseline (skipped if rank_bm25 not installed) --------------------


def test_bm25_retrieve_ranks_relevant_chunk_first() -> None:
    pytest.importorskip("rank_bm25")
    from aqt.speedrun_ai.baseline import Bm25Index

    chunks = [
        rag.Chunk("s#0", "s", "glycolysis produces pyruvate and atp"),
        rag.Chunk("s#1", "s", "amino acids form peptide bonds in proteins"),
        rag.Chunk("s#2", "s", "the nephron filters blood in the kidney"),
    ]
    top = Bm25Index(chunks).retrieve("peptide bonds amino acids", k=1)
    assert top[0].chunk_id == "s#1"


def test_gradeResult_shape() -> None:
    r = GradeResult("correct", True, None, "fb", "")
    assert r.verdict == "correct" and r.ease is None
