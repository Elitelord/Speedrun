# PRD — Learn-by-Doing: The Demographic Transition Model

> A Brilliant-style, learn-by-doing web app. **Subject (course): The Demographic Transition Model (DTM)** — a unit of AP Human Geography (Unit 2: Population). See `Brilliant.md` for the pedagogy this is modeled on, and the project brief PDF for phase gates.

## What is MVP

The MVP is a **deployed, public, mobile-friendly web app** that teaches the Demographic Transition Model through hands-on interaction. It must teach the core idea _without any AI doing the work_.

It contains a single **course** (the DTM) made of **3 solid, interactive lessons that build on each other**, forming a course path with mastery tracking and a next-step recommendation. Learners sign in, manipulate real interactive visuals, get instant hand-written feedback (right _and_ wrong), and their progress + streak persist across sessions and devices.

**The 3 MVP lessons (depth over breadth):**

1. **The DTM Engine** — birth rate, death rate, and the gap between them (natural increase) that drives population across the 5 stages.
2. **Reading Population Pyramids** — how a country's age structure reveals its DTM stage.
3. **From Farms to Factories to Offices** — how a country's workforce shifts from agriculture to industry to services as it moves through the DTM stages.

Success bar: hand the app to someone who's never studied this and they come out understanding how and why populations grow and stabilize as countries develop.

### Features

**Content & lessons**

- A **content model** that describes each lesson as an ordered sequence of typed interactive steps (concept → problem → feedback) stored as data (JSON/TS), not hardcoded HTML — so new lessons can be added without rewriting components, and so AI can generate them later (Phase 2).
- **3 interactive lessons** (see "Course & Lessons" below), each ~2–5 min.
- Each lesson has **at least one rich, directly-manipulated problem** beyond multiple choice (drag rate curves, reshape a pyramid, classify countries on a map) and **a visual element that responds in real time**.

**Feedback**

- **Instant** feedback on every answer (target <100ms), **specific** to what the learner did.
- Wrong answers get a **hint or short explanation** tied to the likely misconception, then allow retry — never just a red X.
- Correct answers get a short "why it works" reinforcement.
- All feedback is **hand-written** (no generation).

**Progress, mastery & path**

- **Course path UI** showing the 3 lessons, what's locked/unlocked, mastery state, and a **recommended next step** after finishing a lesson.
- **Mastery tracking** per concept (based on attempts/correctness); repeated wrong answers surface a review/easier step before moving on.
- **Resume mid-lesson** — return to the exact step where you left off.

**Habit loop**

- **Daily streak** (extended by completing a lesson or N problems in a day), visible streak count, and a **daily-progress** indicator.
- **Milestone / lesson-completion celebration** to make finishing satisfying.

**Accounts & platform**

- **Auth with names** (Firebase Auth: email/password + Google), display name shown in the app.
- **Persistence** of progress, mastery, streaks, and history across sessions and devices (Cloud Firestore).
- **Mobile-first, responsive, touch-friendly**; smooth (60fps) interactive visuals; first interaction <2s.
- **Deployed and public** (Firebase Hosting), supports multiple concurrent learners.

### Out of MVP scope

- **All AI features (Phase 2):** problem generation, AI hints, AI wrong-answer explanations, AI-driven adaptive path. _The app must teach with AI off — so none is built in Phase 1._
- **Learning-science layer (Phase 3):** spaced repetition, interleaving engine, formal scaffolding/fading. (Basic mastery gating ships in MVP; full SRS does not.)
- **Additional lessons** beyond the 3: sector-employment shift (farms→factories→offices), "predict a country's future," migration, etc. → early/final submission.
- **Leagues, leaderboards, XP competition.** (Streaks + progress only for MVP.)
- Social/sharing features, push notifications, email reminders.
- Multiple courses / other subjects; premium tiers / payments; offline mode.
- A content-authoring CMS — lessons are authored as JSON/TS in the repo for now.

## Course & Lessons

**Course:** The Demographic Transition Model. Core through-line: **population change = birth rate − death rate**, and that gap shifts predictably as a country develops (5 stages).

### Lesson 1 — The DTM Engine _(MVP)_

- **Concept:** Population growth is driven by the _gap_ between the birth-rate and death-rate curves (natural increase), and that gap changes across the 5 stages.
- **Hero interaction:** a graph with birth-rate and death-rate curves over time, plus a draggable **stage handle (1→5)** (and/or draggable rate points). As the learner drags: the gap between the curves shades live (= natural increase) and a **population indicator** (growing/shrinking bar or animated total) responds in real time. ("Slider → live visual" primitive.)
- **Steps:**
  1. _Explore (no wrong answer):_ drag through the stages; watch the gap between births and deaths.
  2. _Predict:_ "In Stage 2, deaths fall but births stay high — what happens to population?" → manipulate to confirm.
  3. _Solve:_ "Drag the rates to make a country with a _stable_ population." (Two valid answers — Stage 1 high/high and Stage 4 low/low — surfaced in feedback.)
  4. _Apply:_ "Births fall _below_ deaths — which stage, and what's population doing?" → introduces Stage 5 / decline.
- **Feedback examples:**
  - ✅ "Right — births and deaths are both high, so the gap is tiny and population barely grows. That's Stage 1."
  - ❌ "Not quite — you lowered the death rate but kept births high, which _widens_ the gap, so population grows _faster_. Try shrinking the gap instead."

### Lesson 2 — Reading Population Pyramids _(MVP)_

- **Concept:** A population pyramid (age/sex structure) reveals a country's DTM stage: a **wide base** = high birth rate (Stage 2), a **rectangular** shape = low birth & death (Stage 4), a **narrowing base / top-heavy** shape = decline (Stage 5). Connects shape back to the rates from Lesson 1.
- **Hero interaction:** an interactive population pyramid (horizontal age-cohort bars, male/female split). The learner **drags the base width (birth rate) and the top (longevity/death rate)** and the pyramid reshapes live; the app shows the implied stage and ties it to Lesson 1's curves.
- **Steps:**
  1. _Explore:_ widen/narrow the base; see what high vs low birth rates look like as a shape.
  2. _Predict:_ "A wide base means lots of young people — is the birth rate high or low? Which stage?"
  3. _Solve:_ "Reshape this pyramid to match a Stage 4 developed country."
  4. _Classify:_ match 3 real pyramids (e.g., Niger, United States, Japan) to their stages.
- **Feedback examples:**
  - ✅ "Exactly — a tall, rectangular pyramid means births and deaths are both low and steady: Stage 4."
  - ❌ "That pyramid has a wide base, which means _high_ births — that's Stage 2, not Stage 4. Stage 4 looks more like a column."

### Lesson 3 — From Farms to Factories to Offices _(MVP)_

- **Concept:** As a country develops through the DTM stages, its workforce shifts from the **primary** sector (agriculture/farming) → **secondary** (industry/manufacturing) → **tertiary** (services). Early stages are agrarian; later stages are service economies. A third lens on the same development story from Lessons 1 & 2 (economic structure, not just rates or age).
- **Hero interaction:** a **stacked bar / three-bar chart** of the primary/secondary/tertiary employment split (summing to 100%), with a draggable **development handle (or draggable sector splits)**. As the learner drags, employment flows live between farms → factories → offices, and the implied DTM stage updates. (Same custom SVG + `d3-scale` + drag primitive as Lessons 1 & 2 — no new dependency, no geo/mobile risk.)
- **Steps:**
  1. _Explore (no wrong answer):_ drag the development handle; watch jobs move from farms to factories to offices.
  2. _Predict:_ "In an early-stage (Stage 2) country, which sector employs the most people?"
  3. _Solve:_ "Drag the sector mix to match a highly developed (Stage 4) economy." (services dominate)
  4. _Connect:_ "This country's jobs are mostly services, and its births and deaths are both low — which DTM stage is it in?" → ties economic structure back to the engine from Lesson 1.
- **Feedback examples:**
  - ✅ "Right — early-stage economies are mostly farming (primary sector), since most labor goes to producing food."
  - ❌ "Not quite — heavy _industry_ (secondary) peaks in the middle of development, not at the start. Early on, farming dominates."

### Post-MVP lessons (early/final submission)

- **Place the Country** — classify real countries into DTM stages from their data on an interactive world map (synthesizes Lessons 1–3; deferred for mobile-map polish).
- **The Epidemiological Transition** — why death rates change by stage (Omran's model; CED IMP-2.B.2), paired with the DTM.
- **Limits of the Model** — where the DTM breaks down (Eurocentric, assumes one path, ignores migration/policy); a standard AP exam target.
- Predict a country's future trajectory from current data.
- Migration & its effect on population structure.

## User Persona

The User Persona is a 14-15 year old kid who is interested in studying AP Human Geography concepts for exam preparation and general curiosity.

## User Stories

- **Identity:** As a learner, I can create an account and sign in with my name, so my progress is saved to me across sessions and devices.
- **Learn by doing:** As a learner, I can work through a lesson by directly manipulating an interactive visual (dragging rates, reshaping a pyramid, classifying countries) rather than watching a video or reading walls of text, so the concept actually clicks.
- **Instant feedback & recovery:** As a learner, when I answer, I get instant, specific feedback — and when I'm wrong, I get a hint/explanation so I can recover and try again, not just a red X.
- **Resume freely:** As a learner, I can leave mid-lesson and come back later (even on a different device) and pick up exactly where I left off.
- **Progress & mastery:** As a learner, I can see how I'm doing — my progress through the course, which concepts I've mastered, and my score on each lesson.
- **A path that guides me:** As a learner, when I finish a lesson I'm shown a sensible next step, so I always know what to learn next.
- **Daily habit:** As a learner, I can build and see a daily streak and sense of daily progress, so I'm motivated to come back tomorrow.
- **On my phone:** As a learner, I can do all of this comfortably on a mobile screen with touch.

## Tech Stack

**Required core:** React + TypeScript + Vite + Firebase.

- **Framework / build:** React + TypeScript, bundled with **Vite**.
- **Styling:** **Tailwind CSS** (mobile-first, responsive utilities).
- **Routing:** React Router.
- **State:** lightweight store (Zustand) or React Context for lesson + progress/session state.
- **Backend / auth / persistence (Firebase):**
  - **Firebase Auth** — email/password + Google sign-in, with display name.
  - **Cloud Firestore** — progress, mastery, streaks, attempt history (syncs across devices, supports concurrent learners).
  - **Firebase Hosting** — public deploy.
- **Interactive visuals (the heart of the app):**
  - **Custom SVG + `d3-scale` + pointer events** for all three MVP lessons — the draggable rate graph (L1), the population pyramid (L2), and the sector-employment bars (L3). One shared primitive: full control, easy 60fps, touch-friendly. (`visx` is an option if a React-wrapped d3 helps.)
  - **Framer Motion** for animations, transitions, and milestone/completion celebrations.
  - _(Post-MVP)_ **`react-simple-maps`** (d3-geo + TopoJSON) for the deferred "Place the Country" world-map lesson.
- **Content:** lessons authored as typed JSON/TS objects validated against a shared `Lesson`/`Step` schema (data-driven; AI-generatable in Phase 2).
- **Tooling:** ESLint + Prettier; Vitest + React Testing Library for content-model/feedback logic.
- **Phase 2 (later, out of MVP scope):** OpenAI/Anthropic for generation & hints, with a ground-truth check (rates/stage logic is simple arithmetic, so a small custom validator suffices over a full math engine).
