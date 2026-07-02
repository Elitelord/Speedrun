# Speedrun — Friday-gate handoff & UI-revamp plan

> Point a fresh Claude Code session at this file: **"Read
> docs/speedrun/FRIDAY_HANDOFF.md and continue."** It captures everything done,
> what's pending, the QA feedback, and the UI-overhaul plan.

## 0. Why a new session

This work was done in a **background job** that started before
`.claude/settings.json` had `{"worktree":{"bgIsolation":"none"}}`, so its edits
to the shared checkout were blocked (had to use a worktree, then consolidate to
`main`). That setting now exists (also in `.claude/settings.local.json`), so a
**new session reads it and can edit `main` directly** — no worktree needed.
Confirm on start by making any small edit to `main`; if it's still blocked, the
setting didn't load.

## 1. Current state (all committed to local `main`)

- Local `main` HEAD ≈ `f1fbeefc6` (+ any later commits). Friday gate is DONE and
  `just check` is **fully green** in the main checkout (rust/clippy/rust_test,
  mypy, eslint, svelte, all pytest incl. installer tests).
- Also on origin fork `Elitelord/Speedrun` as branch `worktree-friday-gate` +
  **draft PR #1**. Local `main` was fast-forwarded to it but **NOT pushed to
  origin/main** (pushing the default branch is gated — user's call:
  `git push origin main`).
- Shipped Friday features:
  - **AI subsystem** `qt/aqt/speedrun_ai/` (desktop-only, no Rust): OpenAI client
    (`client.py`, lazy import, shared `grade()`, `AiUnavailable`, `FakeClient`),
    `config.py` (.env parser), `rag.py` (chunk+embed+numpy cosine), `baseline.py`
    (BM25), `generate.py` (grounded gen + grounding gate), `eval.py`
    (Recall@k/MRR RAG-vs-BM25 + 2x2 confusion matrix vs pre-registered
    `docs/speedrun/ai/cutoff.json`), `emit.py`, `pipeline.py` (CLI, `--fake`).
  - **Free-text production loop** (SPOV #3) in `qt/aqt/reviewer.py` +
    `ts/reviewer/index.ts` (`_showProductionFeedback`/`_setProductionGrading`),
    profile flag `speedrun_production_mode`, Tools -> "Free-text grading (MCAT)".
  - **Three scores**: `rslib/src/scheduler/readiness.rs` (Performance + Readiness)
    - proto/service/pylib wrappers + dashboard (`ts/routes/memory-dashboard/`:
      `ScoreGroup.svelte`, `ReadinessPanel.svelte`), dialog/menu "MCAT Readiness".
  - **Sync** = reuse built-in server; `docs/speedrun/SYNC.md`.

## 2. Environment & workflow notes (read before editing)

- **OpenAI key**: `.env` at repo root, var name **`OPENAI_API_KEY`** (standard;
  no underscore between OPEN and AI). Optional `OPENAI_MODEL` (default
  `gpt-4o-mini`), `OPENAI_EMBED_MODEL` (default `text-embedding-3-small`). `.env`
  is git-ignored. `ai_enabled()` re-reads it live per card.
- **AI deps** (`openai numpy rank_bm25`) are installed in `out/pyenv` via
  `uv pip install --python out/pyenv/Scripts/python.exe ...`. NOT via
  `uv sync --extra ai` (that targets a separate `.venv`).
- **Build/check**: `just check` (green; needs
  `git submodule update --init qt/installer/windows-template` for the 2 installer
  tests). Always run `just fix-fmt` before committing (proto/rust/ts/python
  formatting is checked). `just run` to launch.
- **Running tests manually** (Anki closed, to avoid the `_rsbridge.pyd` copy
  lock): `ANKI_TEST_MODE=1 PYTHONPATH=out/pylib PYTHONUTF8=1
  out/pyenv/Scripts/python.exe -m pytest pylib/tests/ -p no:cacheprovider`.
  For qt tests add `qt;out/qt` to PYTHONPATH. Run the WHOLE dir (single-file
  path triggers a NotetypeDict circular import). `test_schedv3` interval tests
  flake without `ANKI_TEST_MODE=1`.
- **Offline AI pipeline smoke test** (no key/network):
  `PYTHONPATH="qt;out/qt;out/pylib" out/pyenv/Scripts/python.exe -m
  aqt.speedrun_ai.pipeline build-index --fake` then `... eval --fake` -> writes
  `docs/speedrun/ai/eval-report.md` (git-ignored). Verified PASS.
- **Commit conventions**: end messages with
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`. Don't
  push origin/main or force-push. Don't stage `.claude/settings*.json`.

## 3. Pending Friday tasks

### 3a. Readiness = sum of sections (DECIDED — implement)

Current `readiness.rs` maps overall science mastery onto the full 472-528 scale
(assumes 4 sections) and gates the total behind >=200 graded reviews — so with 3
studied sections it shows per-section but hides the total, and silently conflates
CARS. **Change to: total = sum of the 4 MCAT sections.**

In `rslib/src/scheduler/readiness.rs`:

- Constants: drop `READINESS_MIN_REVIEWS` and `TOTAL_MIN`/`TOTAL_SPAN` + the
  `scale_total()` fn. Add `const MCAT_SECTIONS: usize = 4;`,
  `const SECTION_MAX: f32 = 132.0;`, `const SECTION_MID: f32 = 125.0;`. Keep
  `READINESS_MIN_COVERAGE = 0.5`.
- `compute_readiness_score`: build per-topic `ReadinessScore`s (as now). Count a
  section as **covered** when `mastery.shown && mastery.cards_with_state > 0`
  (cap at `MCAT_SECTIONS`). Sum covered sections' `scale_section(estimate/low/
  high)`. For `uncovered = MCAT_SECTIONS - covered` sections (incl. CARS), add
  `uncovered * SECTION_MID` to the estimate, `* SECTION_MIN` to low, `*
  SECTION_MAX` to high (neutral prior, full section range = honest uncertainty).
  `coverage = covered / MCAT_SECTIONS`. `shown = coverage >=
  READINESS_MIN_COVERAGE`. Keep `overall` MemoryScore (mastery 0..1) for the
  graded-review count in the UI. Drop the 200-review gate entirely.
- Update the Rust test `performance_discounts_difficulty_and_readiness_...`: with
  2 topics covered of 4, `coverage == 0.5`, `shown == true`, `scaled_estimate`
  in [472,528]. (Old test asserted `!shown`; flip it.)

In `ts/routes/memory-dashboard/ReadinessPanel.svelte`: update the give-up copy
(no longer "≥200 graded reviews AND ≥50%"; now "needs ≥50% of the 4 sections
studied"), show coverage as `covered/4`, and add a **CARS placeholder row**
("not yet available — coming with the CARS module") since CARS isn't in
`topic_tags`. Note that the total includes a wide-uncertainty estimate for
unstudied sections.

Proto is unchanged (fields already exist). Run `just check` + commit.

### 3b. Type-in notetype by default (fixes the QA pain, see section 4)

`docs/speedrun/seed-deck/build_apkg.py` currently uses `col.models.by_name(
"Basic")` — no `{{type:}}` field, so the free-text loop can't trigger and users
must manually Change Notetype (unintuitive). Change the seed build to use the
built-in **"Basic (type in the answer)"** notetype (has `{{type:Back}}`), add the
`source::<slug>` tag support for AI-emitted cards, and **regenerate
`docs/speedrun/seed-deck/MCAT.apkg`** (run build_apkg.py with the built pylib).
Verify `pylib/tests/test_interleave.py` still passes (round-robin by tag is
unaffected by notetype).

### 3c. Accept `OPEN_AI_API_KEY` alias in `config.py`

Users mistype the var (see section 4). In
`qt/aqt/speedrun_ai/config.py::get_config`, read `OPENAI_API_KEY` OR
`OPEN_AI_API_KEY` (first non-empty). Trivial, prevents recurring confusion.

### 3d. Real AI pipeline run (needs the key) — proof artifact

`... pipeline build-index` / `generate --topic ...` / `eval` / `emit` with the
real key -> produces `docs/speedrun/ai/eval-report.md` (the beat-a-baseline +
confusion-matrix proof) and grounded cards; regenerate MCAT.apkg from passing
cards. This is a user/demo step (costs API calls). Add real MCAT source text to
`docs/speedrun/ai/source/` (CC-BY OpenStax) for a stronger retrieval comparison.

### 3e. Sync demo (documented) — user proof step

Follow `docs/speedrun/SYNC.md`: `--syncserver` + `SYNC_USER1`, point desktop +
AnkiDroid custom URL, show offline->reconnect->reconcile.

## 4. QA feedback from the user (address in the revamp)

- **Change-notetype to enable free-text was "way too hard and unintuitive."**
  Type-in production mode should be **default/auto for all decks** and toggled
  in **Settings**, not via Browse -> Change Notetype. (Ties to 3b + the settings
  page below. Consider: apply the loop to any card that has a back field, or
  auto-add a `{{type:Back}}`-style template, rather than requiring the notetype.)
- **Free-text still self-graded with the key set** — root cause was the `.env`
  var was named `OPEN_AI_API_KEY` (wrong); renamed to `OPENAI_API_KEY` and it
  works. 3c makes the code tolerant of the alias.
- Verify end-to-end after the rename: type answer -> LLM verdict + hint ->
  re-attempt -> reveal -> auto-ease; toggle AI off -> native type-answer
  self-grade (writing preserved).
- After 3a, verify the dashboard shows Memory + Performance + a **Readiness total
  on 472-528** (sum of sections) with coverage, not "not enough data".

## 5. UI overhaul plan (DECIDED: all 4 pieces; build after this plan is reviewed)

Surface facts (from exploration):

- Main window `qt/aqt/main.py`: central area is a vertical `QVBoxLayout`
  (`mainLayout`) stacking `tweb` (top toolbar) / `self.web` (`MainWebView`) /
  `sweb` (bottom toolbar). **deckBrowser, overview, review all render into the
  one `mw.web`** via `stdHtml`. State machine = `moveToState()`.
- Deck browser landing `qt/aqt/deckbrowser.py` is **legacy Python-generated
  HTML** (`stdHtml` + `js/deckbrowser.js`), NOT Svelte. Data from `_renderPage`
  `QueryOp`: `col.sched.deck_due_tree()`, `col.studied_today()`. pycmd bridge.
- Full-page Svelte routes: add a folder under `ts/routes/` (+ `+page.ts` loader
  using `@generated/backend`), embed via a Qt `QDialog` calling
  `web.load_sveltekit_page("<route>")` + a new `AnkiWebViewKind` + allow-list
  backend methods in `mediasrv.py`. Template: `ts/routes/deck-options/` +
  `qt/aqt/deckoptions.py`; scores template: `ts/routes/memory-dashboard/`.
- Preferences today = Qt `.ui` form (`qt/aqt/preferences.py` +
  `qt/aqt/forms/preferences.ui`). Speedrun toggles are Tools-menu actions in
  `main.py` (`on_toggle_interleave`, `_weakness`, `on_toggle_production_mode`).
- **No "recent decks" API** — needs a custom revlog->cards `did` query (mirror
  `pylib/anki/stats.py` revlog SQL), likely a new pylib helper / RPC.
- Existing sidebar (Browser `qt/aqt/browser/sidebar/`) is a Qt `QTreeView` in a
  `QDockWidget`+`QSplitter` — reuse the **layout mechanics**, not the tree.

### Recommended phasing (lowest-risk first; the deck browser is the most-used, riskiest screen)

**Phase A — Sidebar navigation (Qt-native, low risk).**
In `main.py setupMainWindow()`, wrap `self.web` in a horizontal `QSplitter`:
`[ nav sidebar | self.web ]`, keeping `tweb`/`sweb`. Sidebar = a small custom
`QListWidget`/button rail (Decks / Readiness / Stats / Settings) driving existing
handlers (`moveToState`, `on_memory_dashboard`, `onStats`, new settings dialog).
Save/restore splitter state like the Browser. **Watch:** `toolbar.py`
`update_background_image` assumes `mw.web` spans full width — a left sidebar
affects it; test the auto-hide top/bottom bars.

**Phase B — Consolidated Svelte settings page (clean, self-contained).**
New route `ts/routes/settings/` (`+page.ts` + `+page.svelte`) mirroring
`deck-options/` components (`SpinBoxRow`, `SaveButton`, switches). Sections:
Study (interleaving on/off, weakness-weighting, topic tags), Review (**free-text
production mode default toggle** — the QA ask), AI (enable + read-only key-status
"detected/not detected", model). Qt shell copied from `deckoptions.py` /
`memory_dashboard.py`; new `AnkiWebViewKind.SETTINGS`; expose bridge methods:
`get/set_interleave_config` (get already exposed — add `set_interleave_config`
to `exposed_backend_list`), and production-mode get/set (Python
`post_handler_list` handlers reading `mw.pm`, since it's a profile flag not a
Rust RPC). Migrate the Tools-menu toggles to point here (keep them as shortcuts).

**Phase C — Three scores + recent decks on the landing.**
Lowest-risk: keep the legacy deck browser, inject a scores strip + recent-decks
list by extending `deckbrowser.py` `_renderStats()`/`_body`, pulling the three
scores via the same `QueryOp` (call the score backend methods) and a new
recent-decks helper (needs the revlog query). Reuse the dashboard's visual
language. Defer a full Svelte deck-browser rewrite.

**Phase D — Better deck organization (higher risk, optional/last).**
Improve deck-list hierarchy/visuals. If pursued, reimplement the landing as a
SvelteKit route (reusing `ScoreGroup.svelte`), porting deck-tree render,
drag/drop reparent, collapse, and the per-deck options menu. Biggest risk item —
do only after A-C are solid.

**Cross-cutting:** the `type-in-by-default` behaviour (3b + QA) should be wired so
the free-text loop "just works" on the seed deck and any imported deck with a
back field, controlled from the Phase-B settings page rather than notetype
surgery.

## 6. Definition of done per change

Run `just fix-fmt` -> `just check` green (Anki closed) -> verify in `just run` ->
commit with the co-author trailer. For UI, drive the real app (the `verify`/`run`
skills) — screenshots of the landing scores, sidebar nav, settings page.
