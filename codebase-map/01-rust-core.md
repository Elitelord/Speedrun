# 01 — Rust Core (Engine)

> **Scope:** Everything under `rslib/` — the core Anki engine. This is the source
> of truth for business logic (scheduling, storage, sync, notes/cards, search,
> import/export, media, stats, rendering, backend service layer).
> Out of scope: `rslib/i18n` codegen (see [06](./06-translations-i18n.md)) and
> the `.proto` definitions themselves (see [05](./05-protobuf-ipc.md)).

## Overview

`rslib` (crate `anki`) is the core Rust engine that holds all of Anki's business
logic. Higher layers (Python via `pylib/rsbridge`, the Qt GUI, and the TS frontend)
talk to it through a generated protobuf service API. The central type is
`Collection` (`rslib/src/collection/`), which owns the SQLite storage handle, i18n,
undo state, and the scheduler queues. RPCs defined in `.proto` are dispatched
through generated traits (`services.rs`) and implemented per-domain in the various
modules and their `service/` submodules.

## Directory layout

`rslib/src/`:

- `collection/` — the `Collection` type, builder, transactions, undo, backups; engine entry point.
- `backend/` — outward-facing backend layer; wires generated services, db proxy, sync/import glue, error conversion.
- `scheduler/` — spaced-repetition logic: queue building, card states, answering, FSRS, filtered decks.
- `storage/` — SQLite access layer; one subdir per entity (`card/`, `note/`, `deck/`, `notetype/`, `revlog/`, `config/`, `tag/`, `graves/`), `.sql` files, schema upgrades.
- `sync/` — collection + media sync: HTTP client, embedded HTTP server, request/response framing, protocols.
- `search/` — search query parser, builder, SQL writer, browser-table column logic; `.sql` ordering snippets.
- `import_export/` — apkg/colpkg packages, CSV/JSON text import/export, gather/insert helpers.
- `notes/`, `card/`, `notetype/`, `decks/`, `deckconfig/`, `tags/`, `revlog/` — core domain entities and their operations.
- `card_rendering/` — template rendering output, TTS, media/field substitution.
- `template.rs`, `template_filters.rs`, `cloze.rs`, `latex.rs`, `typeanswer.rs` — card template parsing/rendering and field filters.
- `media/` — media folder management, checks, references.
- `stats/` — collection statistics, including `graphs/` data.
- `image_occlusion/` — image occlusion note type support.
- `error/` — `AnkiError`/`Result` (snafu-based) error types.
- `config/` — collection-level config keys and accessors.
- `undo/`, `ops.rs`, `progress.rs` — undo/redo framework, operation outputs, progress reporting.
- `text.rs`, `markdown.rs`, `findreplace.rs`, `cloze.rs` — text processing helpers.
- `prelude.rs`, `types.rs`, `timestamp.rs`, `serde.rs`, `version.rs` — common imports and small shared types.
- `ankihub/`, `ankidroid/` — integration-specific helpers (AnkiHub HTTP client, AnkiDroid backend shims).
- `i18n/` — generated translation API (out of scope; see [06](./06-translations-i18n.md)).
- `services.rs` — `include!`s generated `*Service`/`Backend*Service` traits (the protobuf RPC surface).

Helper crates:

- `rslib/io` (crate `anki_io`) — filesystem helpers with better error context (`lib.rs`, `error.rs`).
- `rslib/process` (crate `anki_process`) — subprocess helpers with improved error messages.

## Key modules & entry points

- `rslib/src/collection/mod.rs` — `Collection` & `CollectionBuilder`; everything hangs off this.
- `rslib/src/services.rs` — pulls in generated service traits; the RPC dispatch surface.
- `rslib/src/backend/mod.rs` — `Backend` struct that fronts a `Collection` for callers; per-domain backend files alongside it.
- `rslib/src/storage/sqlite.rs` — `SqliteStorage`, the database connection/setup core.
- `rslib/src/storage/mod.rs` — storage module root tying entity subdirs together.
- `rslib/src/scheduler/mod.rs` — scheduler root; `answering/`, `queue/`, `states/`, `fsrs/`, `filtered/` submodules.
- `rslib/src/scheduler/queue/builder/mod.rs` — how the day's study queue is gathered and ordered.
- `rslib/src/scheduler/answering/mod.rs` — applying an answer/rating to a card.
- `rslib/src/scheduler/fsrs/mod.rs` — FSRS memory-state, params, simulation, rescheduling.
- `rslib/src/sync/mod.rs` — sync root; `collection/`, `media/`, `http_client/`, `http_server/`.
- `rslib/src/search/mod.rs` + `parser.rs`/`sqlwriter.rs` — parse search syntax then translate to SQL.
- `rslib/src/import_export/mod.rs` — import/export root; `package/` (apkg/colpkg) and `text/` (csv/json).
- `rslib/src/error/mod.rs` — `AnkiError`, `Result`, error variants.
- `rslib/src/lib.rs` — crate module list / top-level wiring.

## Find it fast

| Task                                         | Location                                                                                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Change how new/review cards are scheduled    | `rslib/src/scheduler/states/`, `rslib/src/scheduler/answering/`                                             |
| Tune FSRS params / memory state / simulation | `rslib/src/scheduler/fsrs/`                                                                                 |
| Change how the study queue is built/ordered  | `rslib/src/scheduler/queue/builder/`                                                                        |
| Filtered/custom-study deck behavior          | `rslib/src/scheduler/filtered/`, `rslib/src/scheduler/states/filtered.rs`                                   |
| Add/modify a SQL query or table access       | `rslib/src/storage/<entity>/*.sql` + matching `mod.rs`                                                      |
| Database schema migration/upgrade            | `rslib/src/storage/upgrades/`, `rslib/src/storage/sqlite.rs`                                                |
| Change search query syntax/parsing           | `rslib/src/search/parser.rs`, `rslib/src/search/sqlwriter.rs`                                               |
| Browser table columns/sorting                | `rslib/src/search/service/browser_table.rs`, `rslib/src/browser_table.rs`                                   |
| Card template rendering / cloze / filters    | `rslib/src/template.rs`, `rslib/src/cloze.rs`, `rslib/src/template_filters.rs`, `rslib/src/card_rendering/` |
| apkg/colpkg import or export                 | `rslib/src/import_export/package/`                                                                          |
| CSV/JSON import or export                    | `rslib/src/import_export/text/`                                                                             |
| Collection sync (up/download, chunks)        | `rslib/src/sync/collection/`                                                                                |
| Media sync / embedded sync server            | `rslib/src/sync/media/`, `rslib/src/sync/http_server/`                                                      |
| Add/modify a backend RPC implementation      | `rslib/src/backend/*.rs` + the relevant `*/service/` module                                                 |
| Note/notetype/deck/config CRUD logic         | `rslib/src/notes/`, `rslib/src/notetype/`, `rslib/src/decks/`, `rslib/src/deckconfig/`                      |
| Add a new error variant                      | `rslib/src/error/mod.rs`                                                                                    |
| Undo/redo behavior                           | `rslib/src/undo/`, `rslib/src/collection/undo.rs`                                                           |
| Stats / graph data                           | `rslib/src/stats/`, `rslib/src/stats/graphs/`                                                               |

## Cross-references

- [05 — Protobuf & IPC](./05-protobuf-ipc.md): the `.proto` definitions that generate
  the service traits included by `services.rs` and consumed by `backend/`.
- [06 — Translations / i18n](./06-translations-i18n.md): `rslib/src/i18n` generated
  translation API and the `ftl/` source files.
- [02 — Python library](./02-python-lib.md): `pylib`/`rsbridge` is the primary caller
  of this engine; the generated backend API surfaces here as snake_case methods.
