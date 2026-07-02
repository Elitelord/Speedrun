# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""Speedrun AI: write passing generated cards to per-section TSVs.

Output mirrors the hand-authored seed-deck TSVs (``front<TAB>back``) but adds a
third ``source_name`` column so ``build_apkg.py`` can tag each card with both its
``mcat::<section>`` topic (for interleaving) and a ``source::<slug>`` citation.
Only *supported* (grounded) drafts are written — the eval gate blocks the rest.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .generate import CardDraft


def section_of(topic_tag: str) -> str:
    return topic_tag.split("::")[-1]


def _clean(text: str) -> str:
    # TSV is tab/newline delimited; flatten any stray whitespace in a field.
    return " ".join(text.split())


def write_tsvs(drafts: list[CardDraft], out_dir: Path) -> dict[str, int]:
    """Write grounded drafts to ``<out_dir>/<section>.tsv``; returns per-section
    counts. Unsupported drafts are skipped (blocked by the grounding gate)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    by_section: dict[str, list[CardDraft]] = defaultdict(list)
    for d in drafts:
        if d.supported:
            by_section[section_of(d.topic_tag)].append(d)
    counts: dict[str, int] = {}
    for section, ds in by_section.items():
        lines = [
            f"{_clean(d.front)}\t{_clean(d.back)}\t{_clean(d.source_name)}" for d in ds
        ]
        (out_dir / f"{section}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
        counts[section] = len(ds)
    return counts
