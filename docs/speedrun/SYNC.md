# Speedrun — two-way sync (desktop ↔ Android)

The Friday gate requires **two-way sync with no lost or double-counted reviews,
offline review, and sync on reconnect.** We ship this by **reusing Anki's
built-in sync** — no new sync code. Anki bundles a full, self-hostable sync
server, and AnkiDroid speaks the identical protocol, so this is configuration +
a demo.

## Why no new code is needed

- **Self-hostable server, in the same binary.** `--syncserver` (intercepted in
  `qt/aqt/__init__.py` → `pylib/anki/syncserver.py` → the axum `SimpleServer` in
  `rslib/src/sync/http_server/mod.rs`) runs the collection + media sync server.
- **Review double-counting is structurally impossible.** Reviews live in the
  `revlog` table, primary-keyed by their epoch-millisecond `id`, and are merged
  with `INSERT OR IGNORE` (`rslib/src/storage/revlog/add.sql`). The same review
  arriving twice is silently ignored.
- **Offline → reconnect is native.** Offline reviews accumulate rows with USN
  `-1`; on reconnect `SyncMeta::compared_to_remote` picks a normal (incremental)
  sync and the pending rows stream up.
- **Conflict-rule winner (7b).** A genuine schema-level divergence forces a
  full one-way sync where the **user picks the winner** (Upload / Download /
  Cancel), in `qt/aqt/sync.py::full_sync`; incremental merges reconcile by
  object USN/mtime. So the "same card reviewed on both devices offline" case is
  resolved deterministically and is documented to the user at sync time.

## Standing up the server (demo)

From the built desktop app (or the `anki-sync-server` cargo binary):

```bash
# Windows (packaged): set the account, then start the server
set SYNC_USER1=demo:demo
"\Program Files\anki\anki-console" --syncserver

# From this source checkout (dev):
SYNC_USER1=demo:demo SYNC_HOST=0.0.0.0 SYNC_PORT=8080 \
    out/pyenv/Scripts/python.exe -m anki.syncserver
```

Env vars (all read via `envy::prefixed("SYNC_")`):
`SYNC_USER1=user:pass` (required), `SYNC_HOST` (default `0.0.0.0`),
`SYNC_PORT` (default `8080`), `SYNC_BASE` (data dir, must differ from your
normal Anki data dir).

## Pointing the clients at it

- **Desktop:** Preferences → Syncing → _Self-hosted sync server_ =
  `http://<LAN-ip>:8080/`; then Sync and log in as `demo`.
  (Stored via `qt/aqt/profiles.py::set_custom_sync_url`.)
- **Android (AnkiDroid ≥ 2.16):** Settings → Sync → custom sync server =
  the **same** `http://<LAN-ip>:8080/`; log in as `demo`. On the emulator use
  the host's LAN IP (not `127.0.0.1`).

> Fork caveat: client and server sync-protocol versions must match
> (`rslib/src/sync/version.rs`, `SYNC_VERSION_MIN..=MAX`). Desktop and Android
> already run our engine at the same commit, so start the server from the same
> build.

## Demo walkthrough (offline → reconnect → reconcile)

1. Sync desktop → server (uploads the MCAT deck).
2. Sync Android → server (downloads the deck).
3. Put Android in airplane mode; review several cards **offline**.
4. On desktop, review a few different cards.
5. Reconnect Android; Sync. Then Sync desktop.
6. Show both devices now have **identical** review counts / due state — no lost
   and no double-counted reviews (the ms-keyed `revlog` + USN merge guarantee
   this). Interleaving + the three scores are identical on both, since they read
   the same shared Rust engine state.
