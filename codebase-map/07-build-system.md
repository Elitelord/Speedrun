# 07 — Build System & Tooling

> **Scope:** How the project is built and run: the `justfile` recipes, the custom
> build system in `build/` (`configure`, `ninja_gen`, `runner`), the `tools/`
> scripts, `run`/`run.bat`, ninja wrappers, coverage tooling, and root build
> config (`Cargo.toml` workspace, `pyproject.toml`, package manifests).
> Out of scope: CI workflows in `.github/` (see [08](./08-docs-and-tooling.md)).

## Overview

The build is a three-layer pipeline. **`just`** (the `justfile`) is the canonical
command interface — every build/run/test/lint task is a recipe. Each recipe
shells out to a thin **`runner`** binary (via `./ninja` / `tools\ninja.bat`),
which first runs **`configure`** to regenerate `out/build.ninja`, then invokes
**ninja** to execute the actual build graph. The ninja graph itself is generated
in Rust by **`build/ninja_gen`** + **`build/configure`** rather than hand-written.
Dependencies (uv/Python, node/yarn, protoc, ninja) are auto-downloaded into `out/`.

## Common commands

(Run `just --list` for the full set; the `justfile` is the source of truth.)

| Recipe                                   | What it does                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------------- |
| `just build`                             | Build pylib + qt (`ninja pylib qt`).                                            |
| `just run`                               | Build then launch Anki in dev mode (`run`/`run.bat` → `tools/run.py`).          |
| `just run-optimized`                     | Same, release-optimized build.                                                  |
| `just check`                             | Build + run all lint & tests (ninja resolves deps). Run before finishing.       |
| `just test`                              | All tests (Rust/Py/TS); `test-rust`/`test-py`/`test-ts`/`test-e2e` for subsets. |
| `just lint`                              | clippy, mypy, ruff, eslint, svelte, typescript checks.                          |
| `just fmt` / `just fix-fmt`              | Check / apply formatting (`ninja check:format` / `format`).                     |
| `just fix-lint`                          | Auto-fix ruff + eslint.                                                         |
| `just wheels`                            | Build Python wheels (`ninja wheels`).                                           |
| `just ftl-sync` / `just ftl-deprecate`   | Sync / deprecate Fluent translation strings.                                    |
| `just web-watch` / `just rebuild-web`    | Live-rebuild the web stack (macOS/Linux).                                       |
| `just docs` / `docs-serve` / `docs-rust` | Build Sphinx docs / serve / cargo doc.                                          |
| `just clean`                             | Remove `out/` build outputs (`tools/clean`).                                    |

Release recipes live in `release.just` (`just release ...`), each dispatching a
GitHub Actions workflow.

## Directory layout

- `build/configure/` — Rust binary that builds the ninja graph: `rust.rs`, `python.rs`, `pylib.rs`, `aqt.rs`, `web.rs`, `audio.rs`, `installer.rs`, `platform.rs`, `main.rs` orchestrates and writes `build.ninja`.
- `build/ninja_gen/` — library defining ninja build actions per toolchain: `cargo.rs`, `python.rs`, `node.rs`, `sass.rs`, `protobuf.rs`, `archives.rs` (dep downloads), `configure.rs` (regen generator), `build.rs`, `action.rs`.
- `build/ninja_gen/src/bin/` — `update_uv.rs`, `update_node.rs`, `update_protoc.rs` helpers to bump pinned tool versions.
- `build/runner/` — the binary `./ninja`/`run` invoke: `build.rs` (run ninja), `run.rs` (run commands), `pyenv.rs`, `yarn.rs`, `rsync.rs`, `archive.rs`.
- `tools/build`, `tools/build.bat`, `tools/ninja`, `tools/ninja.bat` — entry wrappers that build the runner then call it.
- `tools/clean`, `tools/web-watch`, `tools/rebuild-web`, `tools/reload_webviews.py`, `tools/profile`, `tools/runopt` — dev/clean/watch helpers.
- `tools/build-installer`(`.bat`), `tools/build-x64-mac`, `tools/build-arm-lin`, `tools/run-qt6.8/6.9/6.10` — platform build/run helpers.
- `tools/coverage/` — `coverage-rust`, `coverage-py`, `coverage-ts` (+`.bat`) and `check-coverage-regression.py`.
- `tools/run.py` — Python entry that adds `pylib`/`qt` to path and calls `aqt.run()`.
- `tools/minilints/` — Rust linter for copyright/contributors/licenses (`check:minilints`).

## Root entry scripts & config files

- `run` / `run.bat` — set dev env vars, `ninja pylib qt`, then launch via `tools/run.py`.
- `ninja` / `tools\ninja.bat` — build the `runner` (release) and exec `runner build`.
- `Cargo.toml` — root **Cargo workspace** (members: `rslib/*`, `pylib/rsbridge`, `build/*`, `tools/minilints`, `ftl`, etc.); add deps here, reference with `dep.workspace = true`.
- `pyproject.toml` — root Python project / uv config (env at `out/pyenv`); per-package manifests in `pylib/`, `qt/`.
- `package.json` + yarn (`out/extracted/node/.../yarn`) — JS/TS deps for the web frontend.
- `.dprint.json` — dprint formatter config (drives `check:format`/`format`).
- `.rustfmt.toml` — Rust formatting config.
- `.version` — current Anki version, read by `configure` and release recipes.

## Find it fast

| Goal                                              | Where to look                                                                              |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Add/modify a build step in the ninja graph        | `build/configure/src/*.rs` (pick the layer: `rust.rs`, `python.rs`, `web.rs`, `aqt.rs`, …) |
| Add a new ninja action type / toolchain rule      | `build/ninja_gen/src/` (`cargo.rs`, `node.rs`, `python.rs`, `sass.rs`, …)                  |
| Add a Rust dependency                             | root `Cargo.toml` `[workspace.dependencies]`, then `dep.workspace = true` in the crate     |
| Add a Python dependency                           | `pyproject.toml` (root or `pylib/`/`qt/`); managed by uv                                   |
| Add a TS/JS dependency                            | `package.json` (yarn)                                                                      |
| Add/modify a `just` recipe                        | `justfile` (or `release.just` for release tasks)                                           |
| Change how Anki launches                          | `run` / `run.bat` and `tools/run.py`                                                       |
| Change a downloaded tool version (uv/node/protoc) | `build/ninja_gen/src/bin/update_*.rs` + `archives.rs`/`protobuf.rs`                        |
| Adjust formatting rules                           | `.dprint.json` (most langs), `.rustfmt.toml` (Rust)                                        |
| Change coverage behavior                          | `tools/coverage/*` and `tools/coverage/check-coverage-regression.py`                       |
| Trigger a release                                 | `release.just` recipes (dispatch GitHub workflows)                                         |
| Clean build outputs                               | `tools/clean` (`just clean`); outputs live in `out/`                                       |

## Cross-references

- [08 — Docs & Tooling](./08-docs-and-tooling.md) — CI workflows in `.github/`, docs site, misc tooling.
- [05 — Protobuf & IPC](./05-protobuf-ipc.md) — protoc setup (`build/ninja_gen/src/protobuf.rs`) and generated APIs.
- [06 — Translations & i18n](./06-translations-i18n.md) — `ftl-sync`/`ftl-deprecate` recipes and Fluent generation.
