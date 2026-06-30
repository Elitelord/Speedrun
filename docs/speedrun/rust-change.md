# Speedrun Rust change — Topic-aware interleaving scheduler

> One-page note for the Wednesday gate: what the change is, **why it belongs in
> Rust**, how it stays safe (FSRS + undo), and the upstream files touched with
> merge-difficulty notes.

## What

A new **topic-aware interleaving** order for the study queue. When enabled, the
day's gathered review and new cards are reordered into a **round-robin across
configured MCAT topic tags** (Bio/Biochem, Chem/Phys, Psych/Soc) instead of
being shown one topic at a time. Motivated by the interleaving evidence (Rohrer
et al.) and Brainlift SPOV #1.

Control lives in **collection config** (`BoolKey::InterleaveTopics` + an ordered
`InterleaveTopicTags` list), set/read by a new protobuf RPC pair
(`SetInterleaveConfig` / `GetInterleaveConfig`). Because the config is read by
the shared engine at queue-build time, the behaviour ships to the Android build
with **no Kotlin work**.

## Why Rust (not the Python/Qt layer)

- **Queue building is core engine logic owned by `Collection`.** The day's queue
  is gathered and ordered entirely inside `rslib/src/scheduler/queue/builder/`.
  Reordering anywhere else (Python, Qt, JS) would mean re-implementing or
  second-guessing the engine's gather/limit/bury logic, and would not affect the
  cards the engine actually serves via `get_queued_cards`.
- **One engine, two apps.** Desktop (via PyO3) and Android (AnkiDroid, via the
  JNI backend) both build their queues through the same Rust `Collection`.
  Implementing interleaving in Rust means the desktop and phone behave
  identically and the change ships to Android for free. A JS/Kotlin
  reimplementation would diverge per-platform — explicitly disallowed by the
  brief.
- **FSRS + undo live here.** Intervals, memory state, and the undo log are all
  managed in the Rust core. Doing the reorder in-engine lets us guarantee (and
  unit-test) that interleaving is _purely a reordering_ and never perturbs
  scheduling or undo.

## Safety

- **Reorder only.** `interleave_by_topic()` runs after gathering/sorting and only
  permutes the already-gathered `review`/`new` vectors. It never reads or writes
  a card's `due`, `interval`, or `memory_state`. Proven by
  `interleaving_preserves_fsrs_scheduling` (same card set, identical due/interval
  with the toggle on vs off).
- **Undo intact.** Queue building is read-only with respect to the collection;
  answering a card from an interleaved queue uses the unchanged answer path.
  Proven by `interleaving_keeps_undo_intact` (answer → undo restores reps, due,
  interval, type).
- **No collection corruption.** No schema change; the only persisted state is two
  config keys written through the normal undoable config-set path.

## Tests

- Rust (6): `interleaving::test::matches_exact_and_subtags`,
  `first_configured_topic_wins`,
  `round_robin_preserves_within_topic_order_and_trails_untagged` (pure logic);
  `builder::test::interleaving_round_robins_topics`,
  `interleaving_preserves_fsrs_scheduling`, `interleaving_keeps_undo_intact`
  (engine integration).
- Python (1): `pylib/tests/test_interleave.py` — exercises the
  Set/GetInterleaveConfig RPC end-to-end and asserts the built queue round-robins
  topics, then that disabling restores the full card set.

## Upstream files touched (merge-difficulty notes)

| File                                                | Change                                                                                                                                                                  | Merge risk                                                                                                                |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `rslib/src/scheduler/queue/builder/mod.rs`          | New `topic_map` field; `Context` gains `interleave_topics`/`topic_tags`; `build()` calls `interleave_by_topic()`; `build_queues()` calls `resolve_topics()`; new tests. | **Medium** — edits a hot upstream file; additions are localized (new field + two call sites) so conflicts are mechanical. |
| `rslib/src/scheduler/queue/builder/interleaving.rs` | **New file** — all interleaving logic + unit tests.                                                                                                                     | **Low** — net-new, no upstream counterpart.                                                                               |
| `rslib/src/config/bool.rs`                          | New `BoolKey::InterleaveTopics` enum variant.                                                                                                                           | **Low** — append-only.                                                                                                    |
| `rslib/src/config/mod.rs`                           | New `ConfigKey::InterleaveTopicTags` + get/set accessors.                                                                                                               | **Low** — append-only.                                                                                                    |
| `proto/anki/scheduler.proto`                        | Two new RPCs + `InterleaveConfig` message.                                                                                                                              | **Low** — additive; codegen handles indices.                                                                              |
| `rslib/src/scheduler/service/mod.rs`                | Implement the two new RPC trait methods.                                                                                                                                | **Low** — append-only within the impl block.                                                                              |
| `pylib/anki/scheduler/base.py`                      | `get_/set_interleave_config` wrappers + alias.                                                                                                                          | **Low** — append-only.                                                                                                    |
| `pylib/tests/test_interleave.py`                    | **New file** — Python RPC test.                                                                                                                                         | **Low** — net-new.                                                                                                        |

Generated binding files under `out/` are regenerated by the build and are not
hand-edited.

### Build-tooling fix (Windows)

| File                            | Change                                                                                                                                                                                                                                                                                                                                                             | Merge risk                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `build/ninja_gen/src/render.rs` | Emit the `runner` ninja variable with native (backslash) separators on Windows. n2 spawns each rule's command via `CreateProcess`, which cannot resolve a forward-slash _relative_ executable path; since nearly every rule invokes `$runner`, the whole ninja build failed with `CreateProcessA: The system cannot find the file specified` until this was fixed. | **Low** — additive, Windows-gated. Likely worth upstreaming. |
