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


# -- generation: grounding + card parsing ----------------------------------


def test_is_grounded() -> None:
    from aqt.speedrun_ai.generate import is_grounded

    source = "A peptide bond joins two amino acids by a dehydration reaction."
    assert is_grounded("A peptide bond joins two amino acids.", source) is True
    assert is_grounded("Silicon crystals form the ribosome nucleus.", source) is False


def test_parse_cards_grounds_each() -> None:
    from aqt.speedrun_ai.generate import parse_cards

    chunk = rag.Chunk("s#0", "s", "The alpha helix is stabilised by hydrogen bonds.")
    raw = (
        '{"cards": [{"front": "What stabilises the alpha helix?",'
        ' "back": "hydrogen bonds"}, {"front": "made of?", "back": "unicorn dust"},'
        ' {"front": "", "back": "skipped"}]}'
    )
    cards = parse_cards(raw, "mcat::biobiochem", chunk)
    assert len(cards) == 2  # empty-front card dropped
    assert cards[0].supported is True
    assert cards[1].supported is False  # "unicorn dust" not in source
    assert cards[0].source_name == "s" and cards[0].chunk_id == "s#0"


def test_parse_cards_malformed() -> None:
    from aqt.speedrun_ai.generate import parse_cards

    chunk = rag.Chunk("s#0", "s", "text")
    assert parse_cards("not json", "t", chunk) == []


# -- eval: confusion matrix + retrieval + gate -----------------------------


def test_confusion_metrics() -> None:
    from aqt.speedrun_ai.eval import Confusion

    c = Confusion(tp=4, fp=1, tn=4, fn=1)
    m = c.metrics()
    assert abs(m["accuracy"] - 0.8) < 1e-6
    assert abs(m["false_negative_rate"] - 0.2) < 1e-6  # fn/(tp+fn)=1/5
    assert abs(m["wrong_answer_rate"] - 0.2) < 1e-6  # fn/(tn+fn)=1/5


def test_classify_cards_catches_bad() -> None:
    from aqt.speedrun_ai.eval import classify_cards

    index = {
        "entries": [
            {
                "chunk_id": "s#0",
                "source_name": "s",
                "text": "peptide bonds join amino acids",
            },
        ]
    }
    gold = [
        {"back": "peptide bonds join amino acids", "source_name": "s", "label": "good"},
        {
            "back": "quartz lattice spins the nucleus",
            "source_name": "s",
            "label": "bad",
        },
    ]
    c = classify_cards(gold, index)
    assert c.tn == 1  # good card shipped
    assert c.tp == 1  # bad card blocked
    assert c.fn == 0 and c.fp == 0


def test_recall_and_mrr() -> None:
    from aqt.speedrun_ai.eval import recall_and_mrr
    from aqt.speedrun_ai.rag import Retrieved

    gold = [{"front": "q1", "source_name": "a"}, {"front": "q2", "source_name": "b"}]

    def retriever(q: str) -> list[Retrieved]:
        # q1 -> a at rank 1; q2 -> b at rank 2
        if q == "q1":
            return [Retrieved("a#0", "a", "", 1.0)]
        return [Retrieved("c#0", "c", "", 1.0), Retrieved("b#0", "b", "", 0.5)]

    recall, mrr = recall_and_mrr(gold, retriever)
    assert abs(recall - 1.0) < 1e-6
    assert abs(mrr - 0.75) < 1e-6  # (1/1 + 1/2) / 2


def test_run_eval_pass_and_fail() -> None:
    from aqt.speedrun_ai.eval import run_eval
    from aqt.speedrun_ai.rag import Retrieved

    index = {
        "entries": [
            {"chunk_id": "s#0", "source_name": "s", "text": "peptide amino acids"}
        ]
    }
    gold = [
        {
            "front": "q",
            "back": "peptide amino acids",
            "source_name": "s",
            "label": "good",
        },
        {
            "front": "q",
            "back": "moon cheese reactor",
            "source_name": "s",
            "label": "bad",
        },
    ]
    hit = lambda q: [Retrieved("s#0", "s", "", 1.0)]  # noqa: E731
    miss = lambda q: []  # noqa: E731
    cutoff = {
        "min_accuracy": 0.8,
        "max_false_negative_rate": 0.1,
        "min_recall_at_5": 0.7,
        "min_rag_minus_bm25_recall": 0.0,
    }
    good = run_eval(gold, index, cutoff, hit, miss)
    assert good["passed"] is True
    # RAG worse than baseline -> beats_baseline fails.
    bad = run_eval(gold, index, cutoff, miss, hit)
    assert bad["passed"] is False
    assert bad["checks"]["beats_baseline"] is False


# -- emit ------------------------------------------------------------------


def test_write_tsvs_only_supported(tmp_path: Path) -> None:
    from aqt.speedrun_ai.emit import write_tsvs
    from aqt.speedrun_ai.generate import CardDraft

    drafts = [
        CardDraft("f1", "b1", "mcat::biobiochem", "src", "src#0", supported=True),
        CardDraft("f2", "b2", "mcat::biobiochem", "src", "src#0", supported=False),
    ]
    counts = write_tsvs(drafts, tmp_path)
    assert counts == {"biobiochem": 1}
    content = (tmp_path / "biobiochem.tsv").read_text(encoding="utf-8")
    assert content.strip() == "f1\tb1\tsrc"
