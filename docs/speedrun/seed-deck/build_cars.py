#!/usr/bin/env python
# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""Speedrun: add CARS (Critical Analysis & Reasoning) multiple-choice cards to
the MCAT deck.

CARS items are passage + single-best-answer questions, so they need a custom
notetype (Anki ships no multiple-choice type). This module creates that notetype
and adds the eval-passed CARS units emitted by the AI pipeline
(`docs/speedrun/ai/cars/generated/units.json`, written by `pipeline cars-emit`).

It is imported by `build_apkg.py`, which folds CARS into the single `MCAT.apkg`
so one import demos all four MCAT sections and interleaving mixes CARS with the
sciences. Each question becomes one card, tagged `mcat::cars` (+ a `source::`
citation) so the topic-aware scheduler and the readiness score pick it up as the
fourth section.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re

CARS_NOTETYPE = "CARS (multiple choice)"
CARS_FIELDS = [
    "Passage",
    "Question",
    "A",
    "B",
    "C",
    "D",
    "Answer",
    "Explanation",
    "Source",
]
CARS_TAG = "mcat::cars"

_QFMT = """<div class="cars-passage">{{Passage}}</div>
<div class="cars-question">{{Question}}</div>
<ol type="A" class="cars-options">
<li>{{A}}</li>
<li>{{B}}</li>
<li>{{C}}</li>
<li>{{D}}</li>
</ol>"""

_AFMT = """{{FrontSide}}
<hr id="answer">
<div class="cars-answer"><b>Answer: {{Answer}}</b></div>
<div class="cars-explanation">{{Explanation}}</div>
<div class="cars-source">Source: {{Source}}</div>"""

_CSS = """.card { font-family: sans-serif; text-align: left; }
.cars-passage { line-height: 1.5; margin-bottom: 1em; }
.cars-question { font-weight: bold; margin-bottom: 0.5em; }
.cars-options li { margin: 0.2em 0; }
.cars-answer { margin-top: 0.5em; }
.cars-source { color: #888; font-size: 0.85em; margin-top: 0.5em; }"""


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unknown"


def _guid(passage: str, stem: str) -> str:
    digest = hashlib.sha1(f"cars\x1f{passage}\x1f{stem}".encode()).digest()
    return base64.urlsafe_b64encode(digest).decode()[:16]


def ensure_cars_notetype(col):  # type: ignore[no-untyped-def]
    """Return the CARS notetype, creating it if the collection lacks it."""
    existing = col.models.by_name(CARS_NOTETYPE)
    if existing is not None:
        return existing
    mm = col.models
    nt = mm.new(CARS_NOTETYPE)
    for field in CARS_FIELDS:
        mm.add_field(nt, mm.new_field(field))
    tmpl = mm.new_template("CARS")
    tmpl["qfmt"] = _QFMT
    tmpl["afmt"] = _AFMT
    mm.add_template(nt, tmpl)
    nt["css"] = _CSS
    mm.add(nt)
    return mm.by_name(CARS_NOTETYPE)


def _letter(idx: int) -> str:
    return "ABCD"[idx] if 0 <= idx < 4 else "?"


def add_cars_notes(col, deck_id, units_path: str) -> int:  # type: ignore[no-untyped-def]
    """Add one card per (supported) CARS question from the emitted units file.
    Returns the number of cards added. No-op (returns 0) if the file is absent."""
    if not os.path.exists(units_path):
        return 0
    units = json.loads(open(units_path, encoding="utf-8").read())
    notetype = ensure_cars_notetype(col)
    added = 0
    for unit in units:
        passage = unit.get("passage", "").strip()
        source = unit.get("source_name", "")
        if not passage:
            continue
        for q in unit.get("questions", []):
            options = q.get("options", [])
            if len(options) != 4:
                continue
            note = col.new_note(notetype)
            note.guid = _guid(passage, q.get("stem", ""))
            note["Passage"] = passage
            note["Question"] = q.get("stem", "")
            note["A"], note["B"], note["C"], note["D"] = options
            note["Answer"] = _letter(int(q.get("answer_index", -1)))
            note["Explanation"] = q.get("explanation", "")
            note["Source"] = source
            note.tags = [CARS_TAG]
            if source.strip():
                note.tags.append(f"source::{_slug(source)}")
            col.add_note(note, deck_id)
            added += 1
    return added


if __name__ == "__main__":
    print(
        "build_cars.py is imported by build_apkg.py to fold CARS into MCAT.apkg.\n"
        "Run: python docs/speedrun/seed-deck/build_apkg.py"
    )
