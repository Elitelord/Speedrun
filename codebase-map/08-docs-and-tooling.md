# 08 — Docs, CI & Repo Config

> **Scope:** Documentation and repo-level config: `docs/` (developer/sphinx docs,
> syncserver), `docs-site/` (the user manual, FAQs, release notes, addons —
> mdx content), `.github/` (CI workflows + scripts), and root meta files
> (`CLAUDE.md`, `AGENTS.md`, `README`, license/contributor files, editorconfig,
> formatter configs).
> Out of scope: the `justfile`/`build/` build mechanics (see [07](./07-build-system.md)).

## Overview

This area covers two distinct documentation sets plus repo plumbing. `docs/` holds
**developer-facing** documentation (build/architecture/contributing/API references)
authored as Markdown and built with Sphinx (`docs/conf.py`). `docs-site/` is the
**user-facing** manual published with Mintlify (`docs-site/docs.json`), written as
`.mdx` and translated into many languages via per-language subdirectories. `.github/`
holds the CI/CD workflows, composite actions, and helper scripts, while root meta
files configure the repo, agents, formatters, and contribution policy.

## Directory layout

### `docs/` — developer documentation (Sphinx)

- `docs/index.md` — Sphinx landing page + toctree.
- `docs/conf.py`, `docs/_static/` — Sphinx config, CSS/favicon.
- `docs/development.md`, `docs/build.md`, `docs/ninja.md` — dev setup & build notes.
- `docs/architecture.md`, `docs/protobuf.md`, `docs/language_bridge.md` — internals/IPC.
- `docs/contributing.md`, `docs/releasing.md` — contribution & release process.
- `docs/editing.md`, `docs/testing-coverage.md`, `docs/e2e-testing.md` — editing/testing guides.
- `docs/api-python.md`, `docs/api-rust.md`, `docs/api-*-modules.md` — API references.
- `docs/windows.md`, `docs/mac.md`, `docs/linux.md` — per-platform dev notes.
- `docs/docker/` — Docker build image (`Dockerfile`, `README.md`).
- `docs/syncserver/` — self-hosted sync server image (`Dockerfile`, `Dockerfile.distroless`, `entrypoint.sh`, `README.md`).

### `docs-site/` — user manual (Mintlify, `.mdx`)

- `docs-site/docs.json` — Mintlify site config: navigation, tabs, language switcher.
- `docs-site/README.md`, `docs-site/index.mdx` — site overview / home.
- `docs-site/manual/` — the main user manual (studying, deck-options, editing, importing/, templates/, platform/, etc.).
- `docs-site/faqs/` — individual FAQ pages, one `.mdx` per topic.
- `docs-site/releases/` — `changes/` (per-version changelogs) and `betas/` (beta release notes).
- `docs-site/addons/` — add-on development guide (hooks-reference, the-anki-module, qt, debugging, …).
- `docs-site/ankimobile/` — AnkiMobile (iOS) user docs.
- `docs-site/developers/` — `.mdx` mirror of dev topics for the site.
- `docs-site/translators/` — translator guides (anki/, ankidroid, ankimobile).
- `docs-site/<lang>/` — translated trees (e.g. `ru/`, `de/`, `fr/`, `ja/`, `zh-Hans/`, `ar/`, …).
- `docs-site/rtl.js`, `docs-site/media/` — RTL helper script and shared assets.

### `.github/` — CI/CD & repo automation

- `.github/workflows/` — GitHub Actions workflows (see [CI](#ci)).
- `.github/actions/setup-anki/action.yml` — composite action that provisions the build toolchain.
- `.github/scripts/` — helper scripts: `validate_version.py` (+ test), `sync_translations.py`, `setup_apple_signing.sh`.
- `.github/ISSUE_TEMPLATE/` — bug-report template + `config.yml`.
- `.github/pull_request_template.md`, `.github/dependabot.yml` — PR template & dependency bot.

## Root meta & config files

- `CLAUDE.md` — primary agent/dev guide: just recipes, architecture summary, conventions (also surfaced as `AGENTS.md`).
- `AGENTS.md` — agent instructions; references/aliases `CLAUDE.md`.
- `CODEBASE_MAP.md` — root pointer that directs readers to `codebase-map/README.md`.
- `codebase-map/README.md` — the per-area table of contents for this index set.
- `README.md` — top-level project overview and links.
- `LICENSE` — project license (AGPL).
- `CONTRIBUTORS` — list of contributors (CI checks contributor emails).
- `SECURITY.md` — security/vulnerability reporting policy.
- `.editorconfig` — _(none at root)_; formatting handled by tool configs below.
- `.gitignore`, `.gitattributes` — git ignore/attributes (plus nested `.gitignore` per crate/package).
- `.pre-commit-config.yaml` — pre-commit hooks.
- `.eslintrc.cjs`, `.rustfmt.toml`, `.prettier*` — JS/TS, Rust, formatter configs.
- `cargo/licenses.json`, `ts/licenses.json` — third-party license manifests.

## CI

GitHub Actions workflows live in `.github/workflows/`:

- `ci.yml` — main CI on push/PR: jobs `minilints`, `format`, and `check-linux` / `check-macos` / `check-windows` (build + lint + test across platforms).
- `docs-site.yml` — builds/deploys the Mintlify user docs site.
- `release.yml`, `prepare-release.yml` — release builds and release preparation.
- `publish-audio-package.yml` — publishes `anki-audio` to PyPI.
- `check-linked-issue.yml`, `auto-close-missing-issue.yml` — PR policy automation (require/auto-close PRs without a linked issue).

Workflows share the `.github/actions/setup-anki` composite action and `.github/scripts/` helpers. (Build steps wrap the `just`/`build/` system — see [07](./07-build-system.md).)

## Find it fast

| I want to…                              | Go to                                                         |
| --------------------------------------- | ------------------------------------------------------------- |
| Edit the user manual                    | `docs-site/manual/` (e.g. `docs-site/manual/studying.mdx`)    |
| Add / edit an FAQ                       | `docs-site/faqs/<topic>.mdx`                                  |
| Configure manual navigation / languages | `docs-site/docs.json`                                         |
| Translate a user-facing page            | `docs-site/<lang>/manual/…` (mirror the English tree)         |
| Find release notes / changelogs         | `docs-site/releases/changes/` and `docs-site/releases/betas/` |
| Read add-on dev docs                    | `docs-site/addons/`                                           |
| Edit developer docs (Sphinx)            | `docs/*.md` (config in `docs/conf.py`)                        |
| Self-host the sync server               | `docs/syncserver/`                                            |
| Edit a CI workflow                      | `.github/workflows/*.yml`                                     |
| Change the shared CI toolchain setup    | `.github/actions/setup-anki/action.yml`                       |
| Tweak CI helper scripts                 | `.github/scripts/`                                            |
| Update agent instructions               | `CLAUDE.md` / `AGENTS.md`                                     |
| Edit issue / PR templates               | `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md` |

## Cross-references

- [07 — Build System](./07-build-system.md) — `justfile`/`build/` mechanics invoked by CI.
- [../CODEBASE_MAP.md](../CODEBASE_MAP.md) — root pointer into this index.
- [./README.md](./README.md) — codebase-map table of contents.
