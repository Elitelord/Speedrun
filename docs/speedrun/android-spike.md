# Android engine-sharing spike — findings

> Phase 1 of the Speedrun MVP. Goal: determine how to compile our modified
> `rslib` for Android and make the AnkiDroid fork run a real review on **the
> shared Rust engine**, and de-risk it before committing.

## What's on the machine

- **Fork:** `C:\Users\Samee\Documents\GitHub\Speedrun-Android`
  (origin `github.com/Elitelord/Speedrun-Android`), an AnkiDroid fork.
- **Android SDK:** `…\AppData\Local\Android\Sdk` with **NDK 26.1.10909125**,
  cmake, emulator, platform-tools — all present.
- **Rust Android targets:** none installed yet (`rustup target list` shows no
  `*-android`). `cargo-ndk` not installed.

## Blocking finding: the fork is pre-Rust-backend AnkiDroid

The fork does **not** use the shared Rust engine at all:

- Dependencies are ~2019–2020 era: `io.requery:sqlite-android`,
  `com.afollestad.material-dialogs:0.9.6.0`, `appcompat:1.1.0-rc01`; Gradle 6.2.1.
- **No** `rsdroid` / `Anki-Android-Backend` dependency, no `.so`/`jniLibs`, no
  Rust anywhere in the tree.
- It ships its **own Java scheduler**:
  `AnkiDroid/src/main/java/com/ichi2/libanki/Sched.java` and `SchedV2.java`.

AnkiDroid only adopted the shared Rust backend (rsdroid) around 2.15–2.16
(2021–2022); this fork predates that. **Consequence:** our interleaving change in
`rslib` does **not** ship to this app, because this app never calls `rslib`. It
therefore cannot satisfy the brief's hard rule — _"Rewriting the scheduler in
JavaScript or Swift [or Java] instead of sharing the Rust engine does not count"_
— or the Wednesday gate _"runs a real review session on the shared engine."_

## Options

**A. Re-fork from modern AnkiDroid (recommended).** Current AnkiDroid depends on
`Anki-Android-Backend` (rsdroid), which bundles a JNI-compiled `rslib` `.so`.
Path to ship our change:

1. Fork **current** `ankidroid/Anki-Android` (replacing the old `Speedrun-Android`).
2. Build the `Anki-Android-Backend` `.aar` from **our** modified `rslib`:
   rsdroid references anki's `rslib` (as a pinned submodule/commit) and
   cross-compiles it for `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64` via
   `cargo-ndk` + NDK 26. Point that reference at our fork/commit.
3. Publish the `.aar` to a local Maven repo (`mavenLocal()`), or `includeBuild`
   it, and have AnkiDroid resolve our build instead of the released backend.
4. Run on the emulator: import the MCAT deck, study → interleaving (already in
   `rslib`, config-driven) is active with **zero Kotlin changes**.

   Prereqs to install: `rustup target add aarch64-linux-android
   armv7-linux-androideabi i686-linux-android x86_64-linux-android` and
   `cargo install cargo-ndk`; set `ANDROID_NDK_HOME` to the NDK 26 path.

**B. Port interleaving into the old fork's Java `Sched.java`.** Rejected — a Java
scheduler reimplementation is exactly what the brief forbids; it would not count.

**C. Demo the old fork without engine sharing.** Rejected — fails the "shared
engine" gate.

## Recommendation / decision needed

Pursue **Option A**: the Android target must be a **modern AnkiDroid fork wired to
our `rslib` via rsdroid**. This is a repo-level change (re-fork) and the
single longest-lead MVP item. It needs the maintainer's go-ahead to replace the
current `Speedrun-Android` fork.

Once confirmed, the next concrete steps are: stand up `cargo-ndk` + Android Rust
targets, build the rsdroid `.aar` from our `rslib`, wire AnkiDroid to it, and
record a review session on the emulator.

## Risk note

Even on Option A, the desktop `rslib` already cross-compiles cleanly via cargo;
the Android-specific risk is the rsdroid `.aar` build (NDK linking, target setup)
and pinning AnkiDroid to our backend artifact — not the interleaving logic, which
is engine-side and platform-agnostic.
