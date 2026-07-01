# 04 — Web Frontend

> **Scope:** Everything under `ts/` — the Svelte/TypeScript frontend: SvelteKit
> `routes/` (deck-options, graphs, card-info, image-occlusion, import pages,
> congrats, etc.), shared `lib/` (components, sveltelib, domlib, tslib), the
> `editor/`, `html-filter/`, icons, and the TS build/test config.
> Out of scope: the Qt host that embeds these views (see [03](./03-qt-gui.md))
> and generated protobuf TS bindings (see [05](./05-protobuf-ipc.md)).

## Overview

The frontend is written in **Svelte + TypeScript** and built with **SvelteKit**
(static adapter) + **Vite**. Each screen under `ts/routes/` compiles to a static
page that the Qt app loads from the embedded media server at
`http://localhost:40000/_anki/pages/<name>.html`. Pages talk to the Rust backend
by POSTing protobuf messages to `/_anki/<method>` endpoints (see
`ts/lib/generated/post.ts`); request/response types come from the generated
`@generated/backend` module. Shared UI lives in `ts/lib/` and is consumed both by
SvelteKit routes and by legacy bundles (editor, reviewer, editable) that Qt
injects directly into webviews.

## Directory layout

- `ts/routes/` — SvelteKit pages, one folder per screen (deck-options, graphs, etc.).
- `ts/lib/` — shared frontend code (components, stores, DOM helpers, generated bindings, Sass).
- `ts/editor/` — note editor UI (fields, toolbar, rich-text/plain-text inputs).
- `ts/editable/` — custom elements/Svelte for editable field content & MathJax frames.
- `ts/reviewer/` — review-screen helpers injected into the Qt reviewer webview.
- `ts/html-filter/` — sanitizes pasted HTML before it enters the editor.
- `ts/mathjax/` — MathJax configuration/entry point.
- `ts/icons/` — SVG icons (most pulled from deps; a couple checked in here).
- `ts/tests/e2e/` — Playwright browser end-to-end tests + fixtures.
- `ts/*.{mjs,ts,json,js}` — build/config: `vite.config.ts`, `svelte.config.js`, `bundle_svelte.mjs`, `bundle_ts.mjs`, `transform_ts.mjs`, `tsconfig*.json`.

### `ts/routes/` (pages)

- `deck-options/` — deck/preset config UI (limits, FSRS, lapses, simulator).
- `graphs/` — statistics graphs (intervals, reviews, retention, calendar, etc.).
- `card-info/` — per-card info panel (revlog, forgetting curve).
- `image-occlusion/` — image-occlusion note editor (mask canvas, shapes, tools).
- `import-csv/`, `import-anki-package/`, `import-page/` — import dialogs & shared import-page UI.
- `change-notetype/` — notetype-change field/template mapper.
- `congrats/` — "congratulations, finished" screen.
- `+layout.svelte`, `base.scss` — shared route shell and base styles.

### `ts/lib/` (shared)

- `components/` — reusable Svelte widgets (buttons, selects, modals, tooltips, floating).
- `sveltelib/` — Svelte stores/actions (theme, position/floating, context, lifecycle).
- `domlib/` — DOM manipulation incl. the `surround/` rich-text formatting engine.
- `tslib/` — framework-agnostic TS utils (shortcuts, time, platform, i18n, bridgecommand).
- `tag-editor/` — tag input/autocomplete widgets.
- `sass/` — global styles, color palette, theming vars, mixins.
- `generated/` — hand-written glue (`post.ts`, `ftl-helpers.ts`) merged with generated output (see [05](./05-protobuf-ipc.md)).

## Key modules & entry points

- `ts/lib/generated/post.ts` — `postProto()`: POSTs protobuf to `/_anki/<method>` and decodes the reply.
- `ts/lib/tslib/bridgecommand.ts` — JS→Qt bridge command channel (`pycmd`-style calls).
- `ts/lib/sveltelib/theme.ts` — light/dark/night-mode theme store.
- `ts/routes/+layout.svelte` — common page wrapper for all SvelteKit routes.
- `ts/routes/deck-options/DeckOptionsPage.svelte` — deck-options page root (+ `lib.ts`, `steps.ts`).
- `ts/routes/graphs/GraphsPage.svelte` + `graph-helpers.ts` — graphs page shell and shared data plumbing.
- `ts/routes/card-info/CardInfo.svelte` — card info panel root.
- `ts/routes/image-occlusion/ImageOcclusionPage.svelte` + `tools/`, `shapes/` — IO editor.
- `ts/editor/NoteEditor.svelte` — main note editor; `BrowserEditor.svelte`/`ReviewerEditor.svelte` are host variants.
- `ts/editor/editor-toolbar/EditorToolbar.svelte` — editor toolbar (formatting/cloze/notetype buttons).
- `ts/editor/rich-text-input/` & `plain-text-input/` — the two field input modes.
- `ts/lib/domlib/surround/` — inline-formatting (bold/italic/etc.) tree engine used by the editor.
- `ts/reviewer/index.ts` — reviewer-side helpers loaded into the Qt review webview.
- `ts/html-filter/index.ts` — paste-sanitization entry point.

## Find it fast

| Task                           | Location                                                                            |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| Edit deck-options UI           | `ts/routes/deck-options/` (root `DeckOptionsPage.svelte`)                           |
| Add / change a graph           | `ts/routes/graphs/` (new `*Graph.svelte` + register in `GraphsPage.svelte`)         |
| Change card-info panel         | `ts/routes/card-info/`                                                              |
| Image-occlusion editor / tools | `ts/routes/image-occlusion/` (`tools/`, `shapes/`)                                  |
| Edit import dialogs            | `ts/routes/import-csv/`, `ts/routes/import-anki-package/`, `ts/routes/import-page/` |
| Change-notetype mapper         | `ts/routes/change-notetype/`                                                        |
| Change editor toolbar          | `ts/editor/editor-toolbar/EditorToolbar.svelte`                                     |
| Editor field input behavior    | `ts/editor/rich-text-input/`, `ts/editor/plain-text-input/`                         |
| Rich-text bold/italic logic    | `ts/lib/domlib/surround/`                                                           |
| Add a reusable UI component    | `ts/lib/components/`                                                                |
| Theming / colors / global CSS  | `ts/lib/sass/` (`_color-palette.scss`, `_vars.scss`)                                |
| Call the Rust backend from JS  | `ts/lib/generated/post.ts` + `@generated/backend` (see [05](./05-protobuf-ipc.md))  |
| JS→Qt bridge command           | `ts/lib/tslib/bridgecommand.ts`                                                     |
| Keyboard shortcuts util        | `ts/lib/tslib/shortcuts.ts`                                                         |
| Sanitize pasted HTML           | `ts/html-filter/`                                                                   |
| Reviewer webview helpers       | `ts/reviewer/`                                                                      |
| Add/adjust build config        | `ts/vite.config.ts`, `ts/svelte.config.js`, `ts/bundle_*.mjs`                       |
| Browser e2e tests              | `ts/tests/e2e/`                                                                     |

## Cross-references

- [03 — Qt GUI](./03-qt-gui.md) — the PyQt host that embeds and serves these webviews.
- [05 — Protobuf & IPC](./05-protobuf-ipc.md) — generated `@generated/backend` TS bindings and the `/_anki/` POST protocol.
- [06 — Translations / i18n](./06-translations-i18n.md) — Fluent strings surfaced via `ts/lib/tslib/i18n` and `ts/lib/generated/ftl-helpers.ts`.
- [07 — Build system](./07-build-system.md) — `just` recipes, Vite/SvelteKit bundling, `web-watch`.
