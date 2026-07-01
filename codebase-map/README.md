# Codebase Map — Table of Contents

This folder is an **index/table of contents for the Anki codebase**. It exists so
that agents and developers can quickly find _where_ a given piece of
functionality lives, without having to grep the entire (very large) repository.

> **How to use this map:** Start here. Pick the area that matches what you are
> looking for, open that area's file, and use its "Directory layout" and "Find
> it fast" sections to jump straight to the relevant files. Each area file links
> to concrete paths in the repo.

## Areas

| #  | Area                          | File                                                   | Covers (top-level dirs)                                                                  |
| -- | ----------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| 01 | Rust core (engine)            | [`01-rust-core.md`](./01-rust-core.md)                 | `rslib/` (scheduler, storage, sync, notes, search, import/export, media, stats, backend) |
| 02 | Python library                | [`02-python-lib.md`](./02-python-lib.md)               | `pylib/` (the `anki` package + `rsbridge`)                                               |
| 03 | Qt desktop GUI                | [`03-qt-gui.md`](./03-qt-gui.md)                       | `qt/` (`aqt` app, forms, web assets, mac, installer)                                     |
| 04 | Web frontend                  | [`04-web-frontend.md`](./04-web-frontend.md)           | `ts/` (Svelte/TypeScript: routes, lib, editor, graphs)                                   |
| 05 | Protobuf & cross-language IPC | [`05-protobuf-ipc.md`](./05-protobuf-ipc.md)           | `proto/` + generated bindings, how layers talk                                           |
| 06 | Translations & i18n           | [`06-translations-i18n.md`](./06-translations-i18n.md) | `ftl/` + `rslib/i18n` codegen                                                            |
| 07 | Build system & tooling        | [`07-build-system.md`](./07-build-system.md)           | `build/`, `tools/`, `justfile`, ninja, run scripts                                       |
| 08 | Docs, CI & repo config        | [`08-docs-and-tooling.md`](./08-docs-and-tooling.md)   | `docs/`, `docs-site/`, `.github/`, root config                                           |

## Architecture at a glance

Anki is layered. Data and logic flow roughly bottom-to-top:

```
proto/  ── defines the API surface (messages + RPC services)
  │
rslib/  ── core engine in Rust (the source of truth for logic)
  │  (exposed via pylib/rsbridge, a PyO3 module)
pylib/  ── Python wrapper (the `anki` package) over the Rust backend
  │
qt/aqt/ ── PyQt desktop app; embeds web views
  │  (web views are served locally and built from ts/)
ts/     ── Svelte/TypeScript frontend (talks to Rust over POST/protobuf)
```

`ftl/` provides translations consumed by all layers via generated, type-safe
APIs. `build/` + `tools/` + the `justfile` orchestrate building all of this.

## Maintaining this map

- Each area file is **owned** by its section so edits don't collide.
- When you add or significantly move code, update the matching area file (and
  this TOC if a new top-level area appears).
- Keep entries pointing at directories/modules and short descriptions — this is
  an index, not a place to duplicate the code or full docs.
