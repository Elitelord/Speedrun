#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Speedrun: build the pre-seeded interleaved MCAT deck (.apkg) from the section
TSVs in this folder.

Each TSV line is `front<TAB>back` (with an optional third `source_name` column
written by the AI pipeline's emit step); every card in a section file is tagged
with that section's tag so the topic-aware interleaving scheduler can round-robin
across them, plus a `source::<slug>` tag when a source is present. Cards use the
built-in "Basic (type in the answer)" notetype so the free-text production loop
works out of the box — no Change Notetype needed. Run with the built pylib on
PYTHONPATH, e.g.:

    PYTHONPATH="pylib;out/pylib" out/pyenv/scripts/python.exe \
        docs/speedrun/seed-deck/build_apkg.py
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import tempfile

from anki.collection import Collection, DeckIdLimit, ExportAnkiPackageOptions

# Built-in notetype with a {{type:Back}} field, so the free-text grading loop
# triggers automatically on every seed card.
TYPE_IN_NOTETYPE = "Basic (type in the answer)"


def _source_slug(name: str) -> str:
    """Turn a free-text source name into a tag-safe slug (no whitespace)."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unknown"


def _stable_guid(tag: str, front: str) -> str:
    """Deterministic note GUID from the section tag + front. Keeping the GUID
    stable across rebuilds means re-importing a regenerated MCAT.apkg *updates*
    the matching notes instead of creating duplicates."""
    digest = hashlib.sha1(f"{tag}\x1f{front}".encode()).digest()
    return base64.urlsafe_b64encode(digest).decode()[:16]

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

        # Give the deck a high daily new-card limit so all topics are gathered
        # (Anki's default ~20/day would otherwise gather only the first section,
        # leaving interleaving nothing to mix). Exported with the deck below.
        conf_id = col.decks.add_config_returning_id("MCAT Interleaved")
        conf = col.decks.get_config(conf_id)
        assert conf is not None
        conf["new"]["perDay"] = 500
        conf["rev"]["perDay"] = 1000
        col.decks.update_config(conf)
        deck = col.decks.get(deck_id)
        assert deck is not None
        col.decks.set_config_id_for_deck_dict(deck, conf_id)
        col.decks.save(deck)

        notetype = col.models.by_name(TYPE_IN_NOTETYPE)
        assert notetype is not None, f"missing built-in notetype {TYPE_IN_NOTETYPE!r}"

        total = 0
        for fname, tag in SECTIONS:
            path = os.path.join(HERE, f"{fname}.tsv")
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    fields = line.split("\t")
                    front, back = fields[0], fields[1]
                    source = fields[2] if len(fields) > 2 else ""
                    note = col.new_note(notetype)
                    note.guid = _stable_guid(tag, front)
                    note["Front"] = front
                    note["Back"] = back
                    note.tags = [tag]
                    if source.strip():
                        note.tags.append(f"source::{_source_slug(source)}")
                    col.add_note(note, deck_id)
                    total += 1

        # Fold in CARS (passage + multiple-choice) cards if the AI pipeline has
        # emitted an eval-passed units file. Same deck, so one import demos all
        # four MCAT sections and interleaving mixes CARS with the sciences.
        from build_cars import add_cars_notes

        cars_units = os.path.join(
            HERE, "..", "ai", "cars", "generated", "units.json"
        )
        cars_added = add_cars_notes(col, deck_id, cars_units)
        total += cars_added

        col.export_anki_package(
            out_path=out_apkg,
            options=ExportAnkiPackageOptions(
                with_scheduling=False,
                # carry the high-limit deck config so interleaving is visible on import
                with_deck_configs=True,
                with_media=False,
                legacy=False,
            ),
            limit=DeckIdLimit(deck_id),
        )
        topic_count = len(SECTIONS) + (1 if cars_added else 0)
        print(
            f"wrote {out_apkg} ({total} cards across {topic_count} topics; "
            f"{cars_added} CARS)"
        )
    finally:
        col.close()


if __name__ == "__main__":
    main()
