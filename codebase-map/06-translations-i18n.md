# 06 — Translations & i18n

> **Scope:** The `ftl/` directory (Fluent translation files: `ftl/core`,
> `ftl/qt`, usage data, helper scripts) and the i18n code generation in
> `rslib/i18n` that produces type-safe translation APIs for Rust, Python, and
> TypeScript.
> Out of scope: how individual UI layers call the generated APIs (note those
> briefly, but link to [01](./01-rust-core.md)/[03](./03-qt-gui.md)/[04](./04-web-frontend.md)).

## Overview

Anki's translations use Mozilla's [Fluent](https://projectfluent.org/) format.
English source strings ("templates") live in `.ftl` files in this repo; the
translated variants for other languages live in git submodules
(`ftl/core-repo`, `ftl/qt-repo`) pulled from the translation server. At build
time, the `anki_i18n` crate (`rslib/i18n`) parses every `.ftl` file, extracts
each message key and its variables, and emits **type-safe accessor APIs** for
Rust, Python, and TypeScript. This means a string like
`adding-added = Added` becomes a generated `added()` / `adding_added()` /
`addingAdded()` function in each language, with typed arguments for any
`{ $var }` placeholders.

## Directory layout

### `ftl/`

- `ftl/core/*.ftl` — English source strings shared across all platforms (core/library); add most strings here. Each file (e.g. `adding.ftl`, `browsing.ftl`) is a "module".
- `ftl/qt/*.ftl` — English source strings specific to the desktop Qt GUI (e.g. `about.ftl`, `addons.ftl`, `qt-misc.ftl`).
- `ftl/core-repo/`, `ftl/qt-repo/` — submodules holding translated languages (`<lang>/...`); not edited by hand (managed via `ftl-sync`).
- `ftl/usage/no-deprecate.json` — keys exempted from automatic deprecation/garbage collection.
- `ftl/src/` — the `ftl` Rust CLI tool: `main.rs` (clap subcommands), `garbage_collection.rs` (write-json / garbage-collect / deprecate), `string/` (copy/move/transform keys), `sync.rs`, `serialize.rs`.
- `ftl/Cargo.toml` — crate manifest for the `ftl` CLI tool.
- Helper scripts: `remove-unused.sh`, `copy-core-string.sh`, `move-from-ankimobile`, `update-ankidroid-usage.sh`, `update-ankimobile-usage.sh`.

### `rslib/i18n/`

- `build.rs` — build-script entry point: gathers data, checks, then writes Rust/Python/TS outputs.
- `gather.rs` — reads all `.ftl` files into a `lang -> module -> text` map (honors `EXTRA_FTL_ROOT` for mobile clients).
- `extract.rs` — parses Fluent AST, extracts each message's key, text, and typed variables (`VariableKind`).
- `write_strings.rs` — emits `strings.rs` (compiled into the Rust binary via `OUT_DIR`).
- `python.rs` / `typescript.rs` — emit the Python and TypeScript accessor modules.
- `check.rs` — validation of the gathered translation data.
- `src/lib.rs`, `src/generated.rs` — runtime `I18n` type and generated glue used by the rest of `rslib`.

## Adding/editing strings

1. **Pick the file.** Prefer `ftl/core/` (shared with all platforms); only use `ftl/qt/` for strings exclusive to the desktop Qt interface. Group by topic — add to the existing module file that matches (e.g. a deck-browser string goes in `ftl/core/decks.ftl`).
2. **Key naming & style.** Keys are kebab-case prefixed with the module name (e.g. `adding-the-first-field-is-empty`). Match the surrounding entries; keep alphabetical-ish grouping, use `{ $val }` / named variables for interpolation, and end the file with a trailing newline (the build asserts this).
3. **Rebuild to regenerate APIs.** Run `just check` (or any build that triggers `rslib:i18n`) so the generated Rust/Python/TS accessors pick up the new key. `.ftl` changes are tracked as build inputs and force a rebuild.
4. **Sync / deprecate.** `just ftl-sync` updates submodule commit references to the latest translations and copies source files to the translation repos (needs i18n repo access). `just ftl-deprecate` moves no-longer-referenced entries to the bottom of their file with a deprecation marker (an entry is "unused" if not found in any source or JSON file).

## Code generation

Triggered by the `rslib:i18n` build action (`build/configure/src/rust.rs`), which runs the `anki_i18n` build script. `extract.rs` turns each Fluent message into a `Translation { key, text, variables }`, then:

| Target          | Generated content                                                  | Output location                                   |
| --------------- | ------------------------------------------------------------------ | ------------------------------------------------- |
| Rust            | `strings.rs` — module/key index + typed `tr.*()` methods           | `$OUT_DIR/strings.rs` (compiled into `anki_i18n`) |
| Python          | snake_case methods (e.g. `adding_added`) + `LegacyTranslationEnum` | `pylib/anki/_fluent.py`                           |
| TypeScript      | camelCase functions (e.g. `addingAdded`) + `ModuleName` enum       | `ts/lib/generated/ftl.ts`                         |
| JSON (optional) | full module/string metadata                                        | path in `STRINGS_JSON` env var                    |

Variable types are inferred from the variable name (see `Variable::from` in `extract.rs`: e.g. `count`/`cards` → `Int`, `*-per-minute` → `Float`, `val`/`percent` → `Any`, else `String`).

## Find it fast

| Task                                        | Where                                                                         |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| Add a new translatable string (shared)      | `ftl/core/<topic>.ftl`                                                        |
| Add a Qt-desktop-only string                | `ftl/qt/<topic>.ftl`                                                          |
| Find a string's key by its English text     | grep `ftl/core/` and `ftl/qt/`                                                |
| See how keys → typed APIs are extracted     | `rslib/i18n/extract.rs`                                                       |
| Change generated Python accessor format     | `rslib/i18n/python.rs`                                                        |
| Change generated TypeScript accessor format | `rslib/i18n/typescript.rs`                                                    |
| Change generated Rust accessor format       | `rslib/i18n/write_strings.rs`                                                 |
| Set where generated files are written       | `build/configure/src/rust.rs` (`outputs`)                                     |
| Rename/move a key across files              | `ftl` CLI `string copy`/`move` (`ftl/src/string/`)                            |
| Deprecate/garbage-collect unused keys       | `just ftl-deprecate`; `ftl/src/garbage_collection.rs`; `ftl/remove-unused.sh` |
| Exempt a key from deprecation               | `ftl/usage/no-deprecate.json`                                                 |
| Pull latest translations / push sources     | `just ftl-sync`; `ftl/src/sync.rs`                                            |
| Use mobile-client translations instead      | set `EXTRA_FTL_ROOT` (`rslib/i18n/gather.rs`)                                 |

## Cross-references

- [01 — Rust core](./01-rust-core.md): the `I18n` runtime type and how `rslib` consumes generated `tr.*()` methods.
- [03 — Qt GUI](./03-qt-gui.md): Python/Qt layer consuming `pylib/anki/_fluent.py`.
- [04 — Web frontend](./04-web-frontend.md): Svelte/TS consuming `ts/lib/generated/ftl.ts`.
- [07 — Build system](./07-build-system.md): the `rslib:i18n` build action, `just ftl-sync` / `ftl-deprecate` recipes, and output wiring.
