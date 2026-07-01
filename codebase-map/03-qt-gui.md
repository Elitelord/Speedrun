# 03 — Qt Desktop GUI

> **Scope:** Everything under `qt/` — the PyQt desktop application (`aqt`),
> `.ui` forms and their generated counterparts, bundled web assets
> (`aqt/data/web`), macOS helpers (`qt/mac`), the Briefcase installer
> (`qt/installer`), and `qt/tools`.
> Out of scope: the Svelte/TS sources in `ts/` (see [04](./04-web-frontend.md)).

## Overview

`aqt` is the PyQt6 desktop client. It wraps the Python library (`anki`, see
[02](./02-python-lib.md)) and drives all collection operations through the Rust
backend via that wrapper. The UI is a hybrid: native Qt widgets (built from
`.ui` forms) host embedded `QWebEngineView` web views whose pages are Svelte/TS
apps built in [`ts/`](./04-web-frontend.md) and served locally by an internal
HTTP server (`mediasrv.py`). Python and JS communicate via `pycmd` bridge
messages, and add-ons extend behaviour through the generated hook system
(`gui_hooks.py`).

## Directory layout

| Path                           | Contents                                                                         |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `qt/aqt/`                      | Main PyQt application package (windows, dialogs, reviewer, editor).              |
| `qt/aqt/browser/`              | Card/note Browser: window, `table/` (model/state), `sidebar/` (tree).            |
| `qt/aqt/operations/`           | Async collection ops (card, note, deck, tag, notetype, scheduling).              |
| `qt/aqt/import_export/`        | Import/export dialogs and logic wrapping the Rust importers.                     |
| `qt/aqt/forms/`                | `.ui` Qt Designer layouts + their generated `*.py` (via `build_ui.py`).          |
| `qt/aqt/data/web/`             | Bundled web assets: `js/` (TS for toolbar/reviewer/webview), `css/` (scss).      |
| `qt/aqt/data/`                 | Other runtime data (icons, qt resources) shipped with the app.                   |
| `qt/mac/`                      | macOS Swift helpers (app-nap, theme, audio record) + Xcode project.              |
| `qt/installer/`                | Briefcase packaging: `app/`, per-platform templates, plugins.                    |
| `qt/installer/linux-template/` | Cookiecutter Linux package template (`.desktop`, install scripts).               |
| `qt/tools/`                    | Build helpers: `build_ui.py`, `genhooks_gui.py`, `build_installer.py`, svg/sass. |
| `qt/pyproject.toml`            | `aqt` package metadata and dependencies.                                         |

## Key modules & entry points

| Path                                               | Role                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------- |
| `qt/aqt/__init__.py`                               | Process startup, arg parsing, profile bootstrap, `run()`.             |
| `qt/aqt/main.py`                                   | `AnkiQt` main window; central state machine, collection lifecycle.    |
| `qt/aqt/profiles.py`                               | `ProfileManager` — profile selection, paths, app meta/prefs.          |
| `qt/aqt/reviewer.py`                               | Review session: card display, answer buttons, shortcuts.              |
| `qt/aqt/editor.py`                                 | Note editor (fields, formatting) hosting the editor web view.         |
| `qt/aqt/browser/browser.py`                        | Browse window tying together table + sidebar.                         |
| `qt/aqt/deckbrowser.py`                            | Deck list landing page; `overview.py` is the pre-study screen.        |
| `qt/aqt/addcards.py`                               | Add Cards dialog; `editcurrent.py` edits the current card.            |
| `qt/aqt/deckoptions.py` / `deckconf.py`            | Deck options (Svelte deckconfig) and legacy config.                   |
| `qt/aqt/webview.py`                                | `AnkiWebView` wrapper around `QWebEngineView` + `pycmd` bridge.       |
| `qt/aqt/mediasrv.py`                               | Local HTTP server serving `_anki/pages/*` web views & POST endpoints. |
| `qt/aqt/gui_hooks.py`                              | Generated add-on hook points (see `qt/tools/genhooks_gui.py`).        |
| `qt/aqt/addons.py`                                 | Add-on manager: install, enable/disable, config UI.                   |
| `qt/aqt/sync.py` / `mediasync.py`                  | Collection and media sync UI flows.                                   |
| `qt/aqt/colors.py` / `theme.py` / `stylesheets.py` | Theme palette, light/dark, Qt stylesheets.                            |
| `qt/aqt/utils.py`                                  | Shared Qt helpers (dialogs, tooltips, shortcuts, askUser).            |
| `qt/aqt/taskman.py` / `progress.py`                | Background task runner and progress dialogs.                          |

## Find it fast

| I want to…                               | Look at                                                           |
| ---------------------------------------- | ----------------------------------------------------------------- |
| Change the main window / app state       | `qt/aqt/main.py`                                                  |
| Modify the reviewer (buttons, shortcuts) | `qt/aqt/reviewer.py`, `qt/aqt/data/web/js/reviewer-bottom.ts`     |
| Edit note editing behaviour              | `qt/aqt/editor.py` (web UI in [`ts/`](./04-web-frontend.md))      |
| Work on the card browser                 | `qt/aqt/browser/browser.py`, `browser/table/`, `browser/sidebar/` |
| Add/adjust a dialog layout               | `qt/aqt/forms/*.ui` (regenerate via `qt/tools/build_ui.py`)       |
| Add an add-on hook                       | `qt/tools/genhooks_gui.py` → regenerates `qt/aqt/gui_hooks.py`    |
| Serve a web page to a web view           | `qt/aqt/mediasrv.py`, `qt/aqt/webview.py`                         |
| Change toolbar / top/bottom bars         | `qt/aqt/toolbar.py`, `qt/aqt/data/web/js/toolbar.ts`              |
| Adjust theme / colors                    | `qt/aqt/colors.py`, `qt/aqt/theme.py`, `qt/aqt/stylesheets.py`    |
| Manage profiles / startup                | `qt/aqt/profiles.py`, `qt/aqt/__init__.py`                        |
| Run an async collection operation        | `qt/aqt/operations/*.py`                                          |
| Import or export decks                   | `qt/aqt/import_export/`                                           |
| Handle deck options                      | `qt/aqt/deckoptions.py`                                           |
| Manage add-ons                           | `qt/aqt/addons.py`                                                |
| Build platform installers                | `qt/tools/build_installer.py`, `qt/installer/`                    |
| macOS-specific native behaviour          | `qt/mac/` (Swift helpers)                                         |

## Cross-references

- [04 — Web Frontend](./04-web-frontend.md): Svelte/TS sources for the web views embedded by `aqt`.
- [02 — Python Library](./02-python-lib.md): the `anki` library `aqt` wraps for all collection logic.
- [07 — Build System](./07-build-system.md): `just` recipes, UI/hook generation, and installer packaging.
