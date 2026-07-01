# 05 — Protobuf & Cross-Language IPC

> **Scope:** The `proto/` directory (`.proto` message + service definitions) and
> the mechanism by which the Rust, Python, and TypeScript layers communicate:
> how protobuf is compiled, where generated bindings land
> (`out/{pylib/anki,ts/lib/generated}`, `rslib/proto`), how `_backend.py` exposes
> snake_case RPCs, and how the TS frontend posts to the Rust backend.
> Out of scope: deep internals of the Rust engine (see [01](./01-rust-core.md)).

## Overview

Protobuf is Anki's **single source of truth for the API surface** between the
Rust core, the Python library, and the TS web frontend (and external clients
like AnkiDroid). Each `.proto` file declares messages plus gRPC-style `service`
blocks; a single backend acts as the implementation. At build time these
definitions are compiled into Rust types (`prost`), Python bindings
(`*_pb2.py`) and TS bindings (`protobuf-es`), plus thin per-language RPC
wrappers. A call serializes its request message to bytes, dispatches to the
Rust backend by `(service_index, method_index)` (Python/FFI) or by an HTTP POST
(TS), and the response message comes back as bytes to be deserialized.

## Where definitions live

All definitions are under `proto/anki/` (package `anki.<module>`). `proto/README.md`
gives a one-line intro; `proto/.clang-format` formats them. Key files:

| File                                                                                           | Contents                                                                                           |
| ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `proto/anki/backend.proto`                                                                     | `BackendInit`, `BackendError` (error `Kind` enum) — backend bootstrap/error envelope.              |
| `proto/anki/collection.proto`                                                                  | `CollectionService` / `BackendCollectionService` — open/close, undo/redo, backups, progress.       |
| `proto/anki/cards.proto`, `notes.proto`, `notetypes.proto`, `decks.proto`, `deck_config.proto` | Core object CRUD services + their messages.                                                        |
| `proto/anki/scheduler.proto`                                                                   | Scheduling/FSRS RPCs and messages.                                                                 |
| `proto/anki/search.proto`, `tags.proto`                                                        | Search/browse and tag services.                                                                    |
| `proto/anki/import_export.proto`                                                               | Import/export (apkg, CSV, `CsvMetadata`).                                                          |
| `proto/anki/sync.proto`, `ankiweb.proto`, `ankihub.proto`                                      | Sync + remote-service messages.                                                                    |
| `proto/anki/stats.proto`, `card_rendering.proto`, `image_occlusion.proto`                      | Stats graphs, template rendering, image occlusion.                                                 |
| `proto/anki/config.proto`, `media.proto`, `i18n.proto`, `links.proto`                          | Config storage, media, translations, help links.                                                   |
| `proto/anki/generic.proto`                                                                     | Shared primitives (`Empty`, `Bool`, `String`, `UInt32`, `StringList`, …) used as RPC in/out types. |
| `proto/anki/frontend.proto`                                                                    | `FrontendService` / `BackendFrontendService` — handled in TS/Python, skipped by some codegen.      |
| `proto/anki/ankidroid.proto`, `github.proto`                                                   | AnkiDroid-specific and tooling messages.                                                           |

Note: services come in pairs — a plain `XService` (collection-backed methods)
and a `BackendXService` (methods callable without an open collection).

## Code generation & generated outputs

Codegen is driven by the **`rslib/proto`** build crate (`rslib/proto/build.rs`
→ `rust.rs`, `python.rs`, `typescript.rs`) using the helper crate
`anki_proto_gen`. `just check`/the build system runs it; don't edit generated
files by hand. Outputs:

| Target                               | Generator                              | Lands in                                                                                   |
| ------------------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------ |
| Rust message types                   | `rust.rs` (`prost_build`)              | `$OUT_DIR/anki.<module>.rs`, re-exported via `rslib/proto/src/lib.rs` (`protobuf!` macro). |
| Rust backend service traits/dispatch | `rslib/rust_interface.rs`              | `$OUT_DIR/backend.rs`.                                                                     |
| Python message classes               | protobuf compiler                      | `out/pylib/anki/*_pb2.py`.                                                                 |
| Python RPC wrappers                  | `python.rs` → `write_python_interface` | `out/pylib/anki/_backend_generated.py` (`class RustBackendGenerated`).                     |
| TS message classes                   | `protobuf-es`                          | `out/ts/lib/generated/anki/*_pb.ts`.                                                       |
| TS RPC wrappers                      | `typescript.rs` → `write_ts_interface` | `out/ts/lib/generated/backend.ts` (each method calls `postProto`).                         |

Hand-written runtime glue lives at `ts/lib/generated/post.ts` (the `postProto`
helper) and `pylib/anki/_backend.py`.

## How a call flows

**Python → backend:**

1. Caller uses a typed method on `RustBackendGenerated` (subclassed by
   `RustBackend` in `pylib/anki/_backend.py`); usually reached via
   `col.<area>.*` rather than the backend directly.
2. The wrapper builds the request `*_pb2` message, serializes it, and calls
   `self._run_command(service_idx, method_idx, bytes)`.
3. `_run_command` → `_rsbridge` FFI → Rust dispatches by index to the matching
   `XService` impl in `rslib/src/<area>/service.rs`.
4. Rust returns serialized response bytes (or a `BackendError`), which the
   wrapper parses back into a `*_pb2` message (often unwrapping a single field).

**TS → backend:**

1. TS calls a generated function in `out/ts/lib/generated/backend.ts`.
2. It calls `postProto(method, input, OutputType)` (`ts/lib/generated/post.ts`),
   which `fetch`-POSTs the binary message to `/_anki/<method>`
   (`Content-Type: application/binary`).
3. `qt/aqt/mediasrv.py` routes the path via `post_handlers` /
   `exposed_backend_list` (`raw_backend_request`) into the same Rust backend.
4. Response bytes are returned and decoded by `OutputType.fromBinary`.

## Find it fast

| Goal                                                 | Where to go                                                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Add a new RPC                                        | Add `rpc` to the relevant `service` in `proto/anki/<area>.proto`, implement in `rslib/src/<area>/service.rs`, rebuild (`just check`). |
| Add a message / field                                | Edit the message in `proto/anki/<area>.proto`; bindings regenerate on build.                                                          |
| Find where an X service is implemented               | `rslib/src/<area>/service.rs` (e.g. `rslib/src/collection/service.rs`).                                                               |
| Inspect generated Python RPC wrappers                | `out/pylib/anki/_backend_generated.py` (generated by `rslib/proto/python.rs`).                                                        |
| Inspect generated TS RPC wrappers                    | `out/ts/lib/generated/backend.ts` (generated by `rslib/proto/typescript.rs`).                                                         |
| Inspect generated Rust types                         | `out/rslib/.../anki.<module>.rs`; module list in `rslib/proto/src/lib.rs`.                                                            |
| Change Python FFI dispatch / error mapping           | `pylib/anki/_backend.py` (`_run_command`, `backend_exception_to_pylib`).                                                              |
| Change the TS POST transport                         | `ts/lib/generated/post.ts` (`postProto`).                                                                                             |
| Add/route a TS-callable backend method               | `qt/aqt/mediasrv.py` (`exposed_backend_list` / `post_handler_list`).                                                                  |
| Tune codegen behavior (naming, destructuring, skips) | `rslib/proto/{python.rs,typescript.rs,rust.rs}`, `rslib/rust_interface.rs`.                                                           |
| Define a shared primitive in/out type                | `proto/anki/generic.proto`.                                                                                                           |
| Read protobuf conventions / gotchas                  | `docs-site/developers/protobuf.mdx`.                                                                                                  |

## Cross-references

- [01 — Rust core](./01-rust-core.md): service implementations and engine logic.
- [02 — Python library](./02-python-lib.md): `_backend.py` consumers, `col.*` API.
- [04 — Web frontend](./04-web-frontend.md): TS callers of the generated backend.
