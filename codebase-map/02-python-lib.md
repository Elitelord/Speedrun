# 02 — Python Library

> **Scope:** Everything under `pylib/` — the `anki` Python package that wraps the
> Rust engine, plus `pylib/rsbridge` (the PyO3 bridge) and `pylib/tests`.
> Out of scope: the Qt GUI in `qt/` (see [03](./03-qt-gui.md)).

## Overview

`pylib/` contains the `anki` Python package — the public, importable API used by
the Qt GUI and add-ons. It is a relatively thin wrapper that delegates almost all
real work to the Rust core in `rslib/` (see [01](./01-rust-core.md)). The bridge is
`pylib/rsbridge`, a small PyO3 crate that compiles to the native `_rsbridge`
extension module; `anki._backend.RustBackend` calls into it, sending/receiving
protobuf (or JSON for DB ops) over a single `command`/`db_command` entry point.
Most user-facing code goes through `Collection` (`collection.py`), which owns a
backend handle and exposes manager objects for decks, notes, cards, models, etc.

## Directory layout

| Path                       | Description                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `pylib/anki/`              | The `anki` Python package (collection, scheduler, importing, media, …).             |
| `pylib/anki/scheduler/`    | Spaced-repetition scheduler wrappers (`base.py`, `v3.py`, `legacy.py`, `dummy.py`). |
| `pylib/anki/importing/`    | Legacy importers (`anki2`, `apkg`, `csvfile`, `noteimp`, `mnemo`, `base`).          |
| `pylib/anki/foreign_data/` | Foreign-deck import helpers (e.g. `mnemosyne.py`).                                  |
| `pylib/anki/_vendor/`      | Vendored third-party helpers (e.g. `stringcase.py`).                                |
| `pylib/rsbridge/`          | PyO3 crate (`lib.rs`) building the `_rsbridge` native extension.                    |
| `pylib/tests/`             | Pytest suite + fixtures under `support/`.                                           |
| `pylib/tools/`             | Build/codegen helpers (`genhooks.py`, `genbuildinfo.py`, `hookslib.py`).            |
| `pylib/pyproject.toml`     | Package metadata, deps, and tooling config for the `anki` wheel.                    |
| `pylib/hatch_build.py`     | Hatch build hook used when packaging the wheel.                                     |

## Key modules & entry points

- `pylib/anki/collection.py` — `Collection`, the main entry point; owns the backend and the manager objects.
- `pylib/anki/_backend.py` — `RustBackend`; encodes/decodes protobuf and calls `_rsbridge`. Its `RustBackendGenerated` base exposes snake_case methods for each protobuf RPC (see [05](./05-protobuf-ipc.md)).
- `pylib/rsbridge/lib.rs` — PyO3 `Backend` class with `command` (protobuf) and `db_command` (JSON) methods, plus `open_backend`, `buildhash`, `syncserver`, `initialize_logging`.
- `pylib/anki/decks.py`, `notes.py`, `cards.py`, `models.py`, `tags.py`, `config.py` — manager classes accessed via `col.decks`, `col.notes`, etc.
- `pylib/anki/find.py` & `browser.py` — search/finding and browser-row support.
- `pylib/anki/scheduler/` — review scheduling; `v3.py` is current, `legacy.py`/`dummy.py` for compatibility.
- `pylib/anki/importing/` & `pylib/anki/exporting.py` — deck/note import and export.
- `pylib/anki/media.py` — media file management.
- `pylib/anki/db.py` & `dbproxy.py` — DB access proxy routed through the backend's `db_command`.
- `pylib/anki/storage.py` — collection open/create helpers.
- `pylib/anki/sync.py` & `syncserver.py` — sync types and the self-hosted sync server entry.
- `pylib/anki/hooks.py` & `_legacy.py` — generated hook points and deprecation/back-compat shims.
- `pylib/anki/errors.py` — Python exception types mirroring backend errors.
- `pylib/anki/lang.py` — language/translation helpers (`_fluent` generated API).

## Find it fast

| I want to…                         | Look here                                                                     |
| ---------------------------------- | ----------------------------------------------------------------------------- |
| Open/create a collection           | `pylib/anki/collection.py`, `pylib/anki/storage.py`                           |
| Call a backend RPC from Python     | `pylib/anki/_backend.py` (snake_case methods; see [05](./05-protobuf-ipc.md)) |
| Understand the Python↔Rust bridge  | `pylib/rsbridge/lib.rs`                                                       |
| Search the collection (queries)    | `pylib/anki/find.py`, `pylib/anki/browser.py`                                 |
| Work with notes/cards/decks/models | `pylib/anki/notes.py`, `cards.py`, `decks.py`, `models.py`                    |
| Add/edit note types                | `pylib/anki/models.py`, `pylib/anki/stdmodels.py`                             |
| Schedule reviews                   | `pylib/anki/scheduler/v3.py` (+ `base.py`, `legacy.py`)                       |
| Import decks/notes                 | `pylib/anki/importing/`, `pylib/anki/foreign_data/`                           |
| Export decks/notes                 | `pylib/anki/exporting.py`                                                     |
| Manage media files                 | `pylib/anki/media.py`                                                         |
| Run raw DB queries                 | `pylib/anki/db.py`, `pylib/anki/dbproxy.py`                                   |
| Handle config/preferences          | `pylib/anki/config.py`                                                        |
| Hook into events / deprecations    | `pylib/anki/hooks.py`, `pylib/anki/_legacy.py`                                |
| Render card templates              | `pylib/anki/template.py`                                                      |
| Sync / run a sync server           | `pylib/anki/sync.py`, `pylib/anki/syncserver.py`                              |
| Find error/exception types         | `pylib/anki/errors.py`                                                        |
| Run/inspect Python tests           | `pylib/tests/`                                                                |

## Cross-references

- [01 — Rust Core](./01-rust-core.md) — the `rslib/` engine that pylib wraps.
- [05 — Protobuf & IPC](./05-protobuf-ipc.md) — how `_backend.py`'s snake_case RPCs and generated bindings work.
- [03 — Qt GUI](./03-qt-gui.md) — the `aqt` GUI that consumes this package.
