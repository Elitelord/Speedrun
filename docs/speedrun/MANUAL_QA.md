# Speedrun MVP — Manual QA & Your To-Do List

> Running list of things **you** should do/verify manually (I can't, or shouldn't
> do them for you). I keep this updated as work lands. Check items off as you go.
> Grouped by type. ⭐ = needed for the Wednesday MVP submission.

## A. Proof recordings (Wednesday deliverables) ⭐

> **See [`DEMO_VIDEO.md`](./DEMO_VIDEO.md)** for the full combined demo+proof
> recording script (proofs are captured inside the single demo video) and the
> automated-verification results already captured (Rust tests exit 0; pylib 123
> passed; interleaving + seed-deck tests pass).

- [ ] **Clean-build + tests + commit hash**: `just check` succeeding, hash visible. Verified green at `401f76dad` except the `_rsbridge.pyd` copy, which needs Anki **closed** first (OS file lock, not a code error). See DEMO_VIDEO Scene B.
- [ ] **Android review-session recording** on the emulator/device: open the MCAT deck → toggle interleave → answer a few cards. See DEMO_VIDEO Scene F.
- [ ] **Clean-machine desktop installer recording**: install `out/installer/dist/anki-26.05-win-x64.msi` (193 MB) on a fresh Windows VM/machine and record it launching. See DEMO_VIDEO Scene D. (macOS installer would need `git submodule update --init qt/installer/mac-template` + a Mac/CI build.)

## B. Git / publishing ⭐

- [x] **Commit + push our `anki` fork change** — `main` @ `401f76dad` pushed to `Elitelord/Speedrun` (includes Phase 7 weakness-weighting).
- [x] **Commit + push the Android backend repo** — `Speedrun-Android-Backend` `main` @ `7b03d23` pushed; `.gitmodules` → `Elitelord/Speedrun.git`, `anki` submodule pinned at `e6a435d7a` (reproducible). _Note: pin predates Phase 7, so Android runs uniform interleaving; bump the submodule + rebuild the `.aar` if you want weakness-weighting on-device._
- [ ] **Push `Speedrun-Android`** app changes (`local_backend`, `BackendDependencies.kt`, `Deck.kt`, `build.gradle`, DeckPicker toggle) if not already.
- [ ] **README**: state **Exam: MCAT** up top, AGPL-3.0-or-later + credit to Anki, and build instructions for BOTH apps + architecture overview + the Rust-change note (`docs/speedrun/rust-change.md`).

## C. Content QA — medical accuracy (great fit for you as pre-med)

- [ ] **Review the seeded MCAT cards** for factual accuracy once drafted (Phase 5). Draft is auto-generated from CC BY 4.0 OpenStax + CC BY-SA Wikipedia — verify the science is right and the phrasing is exam-appropriate before shipping.
- [ ] Confirm the per-section tagging (`mcat::biobiochem` / `mcat::chemphys` / `mcat::psychsoc`) matches the cards' actual content.

## D. Feature QA — behavior verification

- [ ] **Import the seed deck**: `just run` → File → Import → `docs/speedrun/seed-deck/MCAT.apkg` (72 cards, "MCAT" deck; ships with a high new-cards/day limit so all 3 topics gather).
- [x] **Interleaving on desktop**: confirmed working by user (topics alternate; toggle off groups by topic).
- [ ] **Weakness-weighting toggle (Phase 7)**: **Tools → "Weight interleaving by weakness"** (enabled only while interleaving is on) → after some reviews, confirm the weaker topic (lower dashboard estimate) surfaces more often.
- [x] **Memory dashboard route fix**: **Tools → "MCAT Memory"** opens (the earlier "Invalid path" is fixed).
- [x] **Interleaving on Android**: confirmed working by user on the emulator (topics alternate via the DeckPicker overflow toggle).
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
