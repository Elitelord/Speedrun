# Speedrun MVP — Manual QA & Your To-Do List

> Running list of things **you** should do/verify manually (I can't, or shouldn't
> do them for you). I keep this updated as work lands. Check items off as you go.
> Grouped by type. ⭐ = needed for the Wednesday MVP submission.

## A. Proof recordings (Wednesday deliverables) ⭐

- [ ] **Desktop clean-build recording**: fresh `just check` (or `just run`) succeeding, with the commit hash visible. (Build works today except 2 environmental installer tests.)
- [ ] **Android review-session screen recording** on the emulator/device: open the MCAT deck → answer a few cards. (App already runs on our engine; needs the real MCAT deck loaded — see D/Phase 5.)
- [ ] **Clean-machine desktop installer recording**: the Windows installer is built at `out/installer/dist/anki-26.05-win-x64.msi` (193 MB). Install it on a fresh Windows VM/machine and record it launching. (macOS installer would need `git submodule update --init qt/installer/mac-template` + a Mac/CI build.)

## B. Git / publishing ⭐

- [ ] **Commit + push our `anki` fork change** (currently local commit `e6a435d7a` on branch `speedrun-mvp`) to your `Elitelord/Speedrun` remote.
- [ ] **Commit + push the two Android repos**: `Speedrun-Android-Backend` (submodule/version wiring) and `Speedrun-Android` (`local_backend`, `BackendDependencies.kt`, `Deck.kt`, `build.gradle`). Decide how the backend submodule should reference our anki fork for a _reproducible_ build (currently a local clone; for a public build, point `.gitmodules` at `Elitelord/Speedrun` + our pushed commit).
- [ ] **README**: state **Exam: MCAT** up top, AGPL-3.0-or-later + credit to Anki, and build instructions for BOTH apps + architecture overview + the Rust-change note (`docs/speedrun/rust-change.md`).

## C. Content QA — medical accuracy (great fit for you as pre-med)

- [ ] **Review the seeded MCAT cards** for factual accuracy once drafted (Phase 5). Draft is auto-generated from CC BY 4.0 OpenStax + CC BY-SA Wikipedia — verify the science is right and the phrasing is exam-appropriate before shipping.
- [ ] Confirm the per-section tagging (`mcat::biobiochem` / `mcat::chemphys` / `mcat::psychsoc`) matches the cards' actual content.

## D. Feature QA — behavior verification

- [ ] **Import the seed deck**: `just run` → File → Import → `docs/speedrun/seed-deck/MCAT.apkg` (72 cards, "MCAT" deck; ships with a high new-cards/day limit so all 3 topics gather).
- [ ] **Interleaving on desktop**: **Tools → "Interleave MCAT topics"** (new checkable toggle) → on → study the MCAT deck → confirm topics visibly alternate (Bio→Chem→Psych→…). Toggle off → cards group by topic. (If it still looks single-topic, confirm the toggle shows a checkmark.)
- [ ] **Memory dashboard route fix**: re-test **Tools → "MCAT Memory"** — the earlier "Invalid path: memory-dashboard" is fixed; it should now open.
- [ ] **Interleaving on Android**: boot emulator → install `Speedrun-Android/AnkiDroid/build/outputs/apk/play/debug/AnkiDroid-play-x86_64-debug.apk` (rebuilt with the toggle) → import `MCAT.apkg` in the app → **overflow menu → "Interleave MCAT topics"** → study → confirm topics alternate on the phone too. (Emulator install cmd: `adb install -r <apk>`.)
- [ ] **Memory score (Phase 4 dashboard)**: `just run` → **Tools → "MCAT Memory"**. With no MCAT deck/reviews yet, every topic should show the **"Not enough data yet"** give-up state (this is correct honest behavior). After importing + reviewing the seed deck, confirm the estimate + range + "updated" render sensibly.
- [ ] **FSRS/undo sanity**: eyeball that enabling interleaving doesn't change due dates/intervals and that undo works mid-session (automated tests cover this, but a manual look is good).

## E. Environment / packaging

- [ ] **(Optional) arm64 Android build** if you want to run on a physical phone (I built x86_64 for the emulator; needs an `ALL_ARCHS` backend build).
- [ ] **Briefcase installer template** (Phase 6): the desktop installer test fails because Briefcase can't clone `qt/installer/windows-template` at branch `v0.4.2` — may need a network/git-config fix on your machine; I'll investigate too.

## F. Decisions for you (when convenient)

- [ ] Confirm the **seed-deck approach**: self-author ~90–120 original cards from CC BY 4.0 sources (recommended, license-clean) vs. any deck you'd prefer.
- [ ] Confirm the **give-up thresholds** (draft: 20 graded reviews/topic, 100/deck) once you see real review volumes.

---

_Done items move to the bottom / get checked. Ping me to add anything._
