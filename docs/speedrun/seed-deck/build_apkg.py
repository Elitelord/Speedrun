#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Speedrun: build the pre-seeded interleaved MCAT deck (.apkg) from the section
TSVs in this folder.

Each TSV line is `front<TAB>back`; every card in a section file is tagged with
that section's tag so the topic-aware interleaving scheduler can round-robin
across them. Run with the built pylib on PYTHONPATH, e.g.:

    PYTHONPATH="pylib;out/pylib" out/pyenv/scripts/python.exe \
        docs/speedrun/seed-deck/build_apkg.py
"""

from __future__ import annotations

import os
import tempfile

from anki.collection import Collection, DeckIdLimit, ExportAnkiPackageOptions

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [
    ("biobiochem", "mcat::biobiochem"),
    ("chemphys", "mcat::chemphys"),
    ("psychsoc", "mcat::psychsoc"),
]


def main() -> None:
    out_apkg = os.path.join(HERE, "MCAT.apkg")
    tmpdir = tempfile.mkdtemp()
    col = Collection(os.path.join(tmpdir, "build.anki2"))
    try:
        deck_id = col.decks.id("MCAT")
        assert deck_id is not None
        basic = col.models.by_name("Basic")
        assert basic is not None

        total = 0
        for fname, tag in SECTIONS:
            path = os.path.join(HERE, f"{fname}.tsv")
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    front, back = line.split("\t", 1)
                    note = col.new_note(basic)
                    note["Front"] = front
                    note["Back"] = back
                    note.tags = [tag]
                    col.add_note(note, deck_id)
                    total += 1

        col.export_anki_package(
            out_path=out_apkg,
            options=ExportAnkiPackageOptions(
                with_scheduling=False,
                with_deck_configs=False,
                with_media=False,
                legacy=False,
            ),
            limit=DeckIdLimit(deck_id),
        )
        print(f"wrote {out_apkg} ({total} cards across {len(SECTIONS)} topics)")
    finally:
        col.close()


if __name__ == "__main__":
    main()
