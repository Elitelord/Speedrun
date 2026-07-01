# **Speedrun Brainlift — MCAT**

# **Owners**

- Sameer Agarwal

- Claude(obtaining sources)

# **Purpose**

### **Purpose**

_The North Star of your BrainLift — one or two sentences defining the central goal/question._

- _The purpose of this BrainLift is to build the research foundation for Speedrun — a desktop and mobile MCAT study app forked from Anki that separates memory, performance, and readiness into three distinct, honest scores. The goal is to understand the science and engineering deeply enough to make real decisions: which scheduling algorithm changes belong in Rust, what the learning-science evidence says about which study features are worth building, and how to model exam readiness in a way that shows uncertainty rather than hiding it._

### **In Scope**

_Topics, domains, and types of information relevant to your purpose._

- _The MCAT's structure, scoring scale (472–528), and content outline_

- _Spaced repetition theory and Anki's Rust/Python/protobuf architecture_

- _The distinction between memory, performance, and transfer_

- _Evidence-based study techniques (retrieval practice, interleaving, spacing)_

- _Calibration, knowledge tracing, and scoring models_

- _AI card generation, grounding, and hallucination evaluation_

### **Out of Scope**

_Boundaries — what you will not focus on (prevents scope creep)._

- _LSAT, GMAT, or USMLE tests_

- _Gamification, streaks, or engagement-maximization features_

- _Free-roaming chatbot tutors or general-purpose AI assistants_

- _The predictive validity of MCAT scores for medical school performance_

- _Building a new spaced-repetition algorithm from scratch_

# **DOK 4: Spiky Points of View (SPOVs)**

_A Spiky POV is a well-reasoned, actionable, often contrarian assertion forged by combining multiple DOK 3 Insights into a new mental model. Write your own below._

- **Spiky POV 1:** _Weakness-Weighted Interleaving should be the default in any MCAT study tool._

  - **Elaboration:** _The MCAT explicitly tests three major Scientific fields, Biology, Chemistry, and Psychology(1.1). Interleaving has been proven to be more effective than blocked learning(3.3). Rather than just using regular Interleaving, which has been implemented in apps like Memm before, weakness-weighted interleaving can be stronger, as seen with Bjork's desirable difficulties._

- **Spiky POV 2:** _Practice Problems for CARS can and should be integrated into Flashcard apps, especially for tests like the MCAT._

  - **Elaboration:** _Current study tools like Anki or Memm don’t attempt to prepare students for the CARS section(Critical reasoning)(2.5). I believe that with the power of LLM generation, this section can be covered with generated practice problems and passages._

- **Spiky POV 3:** _MCAT Study shouldn't be based off Flipcards that show answers_

  - **Elaboration:** _Rather than Flipcards where the user's action is to just flip the card, the user should actually answer with text input answers, this can be graded with AI as well. Writing in the answer and receiving corrective feedback is proven to be effective for retention(3.6). Additionally, there is research into the capacity of LLMs to properly give feedback(4.6)._

# **Experts**

_Leading thinkers in the domain. Names and links populated; Who / Focus / Why Follow left blank for you._

- **Robert A. Bjork**

  - **Who:** _Distinguished Research Professor of Psychology at UCLA; directs the Bjork Learning & Forgetting Lab with Elizabeth Ligon Bjork._

  - **Focus:** _"Desirable difficulties"; the distinction between storage strength and retrieval strength; why current performance is a poor proxy for durable learning._

  - **Why Follow:** _Talks about major learning science principle of ignoring short term performance, important for app optimization._

  - **Where:**

    - **UCLA Bjork Learning & Forgetting Lab:** [https://bjorklab.psych.ucla.edu](https://bjorklab.psych.ucla.edu)

- **Henry L. (Roddy) Roediger III**

  - **Who:** _James S. McDonnell Distinguished University Professor (Emeritus) at Washington University in St. Louis; one of the most cited memory researchers alive._

  - **Focus:** _Retrieval practice and the testing effect; applying cognitive psychology to real educational settings._

  - **Why Follow:** _His 2006 paper with Karpicke is largely cited for flashcard learning. Understanding why retrieval works is essential for building the Performance score on top of Anki's memory engine._

  - **Where:**

    - **Washington University in St. Louis:** _[https://psychweb.wustl.edu/people/henry-l-roediger-iii](https://psychweb.wustl.edu/people/henry-l-roediger-iii)_

- **Jeffrey D. Karpicke**

  - **Who:** _Professor of Psychological Sciences at Purdue; directs the Cognition and Learning Laboratory._

  - **Focus:** _Retrieval-based learning; how elaborative studying (e.g., concept mapping) compares to practice testing; metacognitive illusions about what "counts" as learning._

  - **Why Follow:** _Shows importance of integrating active recall in the app._

  - **Where:**

    - **Purdue Cognition & Learning Lab:** _[https://www.purdue.edu/hhs/psy/directory/faculty/Karpicke\_Jeffrey.html](https://www.purdue.edu/hhs/psy/directory/faculty/Karpicke_Jeffrey.html)_

- **John Dunlosky**

  - **Who:** _Professor of Psychology at Kent State; co-authored the landmark 2013 review of study techniques in Psychological Science in the Public Interest._

  - **Focus:** _Comparative effectiveness of 10 common study techniques; metacognition and students' ability to judge what actually helps them learn._

  - **Why Follow:** _His papers talk about which features are better to build like practice testing and distributed practice._

  - **Where:**

    - **Kent State University:** _[https://www.kent.edu/psychology/profile/john-dunlosky](https://www.kent.edu/psychology/profile/john-dunlosky)_

- **Doug Rohrer**

  - **Who:** _Professor of Psychology at the University of South Florida; leading researcher on interleaving and mixed practice._

  - **Focus:** _Interleaved practice (shuffling problem types) vs. blocked practice; how mixing topics during study improves both discriminative ability and long-term retention._

  - **Why Follow:** _Interleaving is an important feature to add in, his paper is useful in studying implementation and effectiveness._

  - **Where:**

    - **University of South Florida:** [http://uweb.cas.usf.edu/\~drohrer/](http://uweb.cas.usf.edu/~drohrer/)

- **Harold Pashler**

  - **Who:** _Distinguished Professor of Psychology at UC San Diego; directs the Laboratory for Attention and Perception._

  - **Focus:** _Distributed practice; spacing effects; the gap between laboratory memory findings and real-world educational application._

  - **Why Follow:** _Quantified best inter-study intervals, important for integrating in this app._

  - **Where:**

    - **UC San Diego (LaPlab):** [https://laplab.ucsd.edu/](https://laplab.ucsd.edu/)

- **Piotr Woźniak**

  - **Who:** _Polish researcher and software developer; creator of SuperMemo, the first commercial spaced-repetition system._

  - **Focus:** _Computational models of memory (the DSR model: Difficulty, Stability, Retrievability); the SM-2 algorithm and its successors; incremental reading._

  - **Why Follow:** _SM-2 is the foundation for the Anki scheduler and DSR is theory behind it._

  - **Where:**

    - **SuperMemo (super-memory.com):** [https://super-memory.com](https://super-memory.com)

    - **SuperMemo Guru (theory):** [https://supermemo.guru](https://supermemo.guru)

- **Jarrett Ye (L.M.Sherlock)**

  - **Who:** _Researcher and open-source developer; lead author of the FSRS algorithm and the open-spaced-repetition GitHub organization._

  - **Focus:** _Stochastic shortest-path optimization of spaced repetition; FSRS parameter fitting from real Anki review logs; the SRS benchmark for comparing schedulers._

  - **Why Follow:** _Anki runs FSRS for it’s primarily scheduler._

  - **Where:**

    - **Open Spaced Repetition (FSRS):** [https://github.com/open-spaced-repetition](https://github.com/open-spaced-repetition)

    - **GitHub profile:** [https://github.com/L-M-Sherlock](https://github.com/L-M-Sherlock)

- **Damien Elmes**

  - **Who:** _Australian software developer; creator and primary maintainer of Anki since 2006\._

  - **Focus:** _Anki's architecture — the Rust backend (rslib), Python application layer, protobuf interface, cross-platform sync, and the AnkiWeb ecosystem._

  - **Why Follow:** _Developed large portions of the codebase, architectural decisions are important to understand._

  - **Where:**

    - **Anki source (ankitects):** [https://github.com/ankitects/anki](https://github.com/ankitects/anki)

    - **Anki project site:** [https://apps.ankiweb.net](https://apps.ankiweb.net)

- **Albert T. Corbett**

  - **Who:** _Research Professor (Emeritus) at Carnegie Mellon's Human-Computer Interaction Institute; co-creator of the ACT-R cognitive architecture's tutoring applications._

  - **Focus:** _Bayesian Knowledge Tracing (BKT); intelligent tutoring systems; modeling the probability that a student has mastered a knowledge component from their response history._

  - **Why Follow:** _His research acts as a baseline to compare app to._

  - **Where:**

    - **Carnegie Mellon (ACT-R):** [http://act-r.psy.cmu.edu/](http://act-r.psy.cmu.edu/)

# **DOK 3: Insights**

_Your original conclusions/connections drawn from the sources, grouped by theme (mirroring the Knowledge Tree). Leave blank for now._

#### _**From the MCAT Exam**_

- **Insight 1:** _The MCAT primarily aims to test student’s medical knowledge and understanding of the Biological, Chemical, and Psychological aspects of Living Beings. This is specifically through the lens of Scientific Inquiry because the examiners want to ensure students are able to conduct effective research. These topics have the potential to be interleaved._

- **Insight 2:** _Beyond the Medical aspect, the critical reasoning section tests comprehension in subject areas that can have little to do with medicine. This ensures students are able to analyze foreign situations and apply reasoning properly, something that relates heavily to a doctor’s duties. This is a fourth of the test score and an incredibly important point to cover, although the study tactics would be largely different._

#### _**From Spaced Repetition & the Anki Engine**_

- **Insight 1:** _The idea that interstudy gap should increase with retention interval is what motivates the need for FSRS over SM-2._

- **Insight 2:** _Anki already proves to be an effective tool for students, medical and other, with significant gains in scores and a strong predictor for future exam performance. Anki’s gap is a lack of a score using their effective predictive metrics and sessions._

#### _**From The Science of Effective Learning**_

- **Insight 1:** _Some study methods are significantly more efficient than others yet often aren’t put into place because these more effective methods are harder to practice. The better apps would use these harder techniques, knowing it can cause difficulty for students but ultimately better outcomes._

- **Insight 2:** _Since students are unable to recognize their own gaps in most cases (3.1, 4.1), every existing ‘readiness’ percentage from MCAT tools would feel accurate. Showing the value accurately and explicitly is a big design requirement because of this._

- **Insight 3:** _The strongest form of retrieval is production, not recognition. Flip-card apps reveal the answer, which the generation effect (3.6) and the learning-vs-performance gap (3.1) both predict will inflate fluency while under-building durable memory. Forcing a free-text answer converts review from recognition into production — much closer to how the MCAT actually tests (1.2), and the bridge from a memory score toward a performance score._

- **Insight 4:** _A wrong free-text attempt is a learning opportunity, not a failure: corrective feedback after errors drives retention (Pashler 2005, 3.6) and confident errors are corrected especially well (hypercorrection, Metcalfe 2017, 3.6). The right design is therefore scaffolded hint → re-attempt → reveal the correct answer, and the card's reappearance should depend on how it was answered — not a binary self-graded flip._

- **Insight 5:** _Self-directed study misallocates time — learners drop items they merely feel they know (region of proximal learning, 3.7) yet can't judge accurately (3.1, 4.1) — while mastery learning shows the largest gains come from concentrating effort on not-yet-mastered material (Bloom, 3.7). Combined with FSRS's measured retrievability as a weakness signal (2.2), this argues the scheduler should weight interleaving toward measured-weak, high-value topics rather than interleave uniformly or leave the choice to the student._

#### _**From Model Readiness and AI Generation**_

- **Insight 1:** _Student’s and models alike can be incredibly overconfident about their abilities while being wrong, this can be seen in test results and hallucinations. Putting uncalibrated LLM’s in front of these overconfident students doubles the potential for misconceptions._

- **Insight 2:** _LLM’s have strong potential for question generation, yet proper testing hasn’t been done against human generated questions. The study in 4.4 that found 89% retention with ai problems vs 73% without any studying forgot to include human generated problems as a control baseline. Proper evaluation needs to be done when measuring these tool’s performance before integration._

- **Insight 3:** _LLM grading of free-text answers is now accurate enough (near-human agreement, 4.6) to power a production-based review loop — but LLM feedback is prone to ungrounded, fabricated critique, so the same grounding, held-out evaluation, and abstention safeguards any AI feature needs (4.5) are precisely what make AI free-text grading trustworthy enough to sit at the center of the study loop._

# **DOK 2: Knowledge Tree**

_The structured foundation of the BrainLift, organized from broad category to subcategory to source. Under each source, fill in DOK 1 (raw facts) and DOK 2 (your own-words summary), and confirm the link._

- **Category 1: The MCAT Exam — Structure & What It Actually Measures**

  - **Subcategory 1.1: Test Structure, Scoring & Content Outline**

    - "What’s on the MCAT Exam?" Content Outline — AAMC

      - **DOK 1 \- Facts:**

        - _4 sections with the first 3 around foundation concepts_
        - _first is biological/biochemical foundation of living things._
        - _Second is Chemical and Physical Foundations of Living System_
        - _Third is Psychological, Social, and Biological Foundations of Behavior_
        - _Fourth is Critical Analysis and Reasoning Skills_
        - _Required to use these skills:_
          - _Knowledge of scientific concepts and principles._
          - _Scientific reasoning and problem-solving._
          - _Reasoning about the design and execution of research._
          - _Data-based and statistical reasoning._
      - **DOK 2 \- Summary:**

        - _Covers major biological, chemical, and psychological processes, along with general scientific skills like reasoning, data analysis, problem solving, and research execution._

      - **Link to source:** [https://students-residents.aamc.org/whats-mcat-exam/publication-chapters/whats-mcat-exam](https://students-residents.aamc.org/whats-mcat-exam/publication-chapters/whats-mcat-exam)

    - "MCAT Exam Scoring" (raw → scaled, equating, percentiles) — AAMC

      - **DOK 1 \- Facts:**

        - Your raw score on each of the four multiple-choice sections is based on the numbers of questions you answer correctly in each section. ​There is no penalty for guessing.​
        - The raw score for each section is then converted to a scaled score ranging from 118 (lowest) to 132 (highest).
        - Your total scaled score is the sum of the four individual section scores and will range from 472 to 528\.
        - Every test form of the MCAT exam measures the same basic concepts and skills. However, each form is different in the specific questions it uses. ​While care is taken to make sure that the forms are equivalent in difficulty, one form may be slightly more or less difficult than another. The conversion of raw scores to scaled scores, through a process called equating, compensates for small variations in difficulty between sets of questions​ and ensures that sco​​r​​es have the same meaning, no matter when you test or who tests at the same time you did​.
      - **DOK 2 \- Summary:**

        - _Each Section is scored separately, with the raw score determined by amount of questions correct._

        - _These are then scaled from 118 to 132 and combined for the final scoring, the scaling accounts for variations in the difficulty._

      - **Link to source:** [https://students-residents.aamc.org/register-mcat-exam/publication-chapters/mcat-exam-scoring](https://students-residents.aamc.org/register-mcat-exam/publication-chapters/mcat-exam-scoring)

  - **Subcategory 1.2: Scientific Inquiry & Reasoning Skills (passage reasoning, not just recall)**

    - "Scientific Inquiry & Reasoning Skills: Overview" — AAMC

      - **DOK 1 \- Facts:**

        - _Demonstrating understanding of scientific concepts and principles_

        - _Identifying the relationships between closely-related concepts_

        - _Reasoning about scientific principles, theories, and models_

        - _Analyzing and evaluating scientific explanations and predictions_

        - _Demonstrating understanding of important components of scientific research_

        - _Reasoning about ethical issues in research_

        -

      - **DOK 2 \- Summary:**

        - _Scientific inquiry and reasoning skills involve understanding concepts, identifying relationships, and reasoning about principles._

        - _Students should also understand important components of scientific research and ethical dilemmas._

      - **Link to source:** [https://students-residents.aamc.org/whats-mcat-exam/scientific-inquiry-reasoning-skills-overview](https://students-residents.aamc.org/whats-mcat-exam/scientific-inquiry-reasoning-skills-overview)

    - "Critical Analysis and Reasoning Skills Section: Overview" — AAMC

      - **DOK 1 \- Facts:**

        - _The Critical Analysis and Reasoning Skills section achieves this goal by asking you to read and think about passages from a wide range of disciplines in the social sciences and humanities, followed by a series of questions that lead you through the process of comprehending, analyzing, and reasoning about the material you have read._

        - _Critical Analysis and Reasoning Skills passages are relatively short, typically between 500 and 600 words, but they are complex, often thought-provoking pieces of writing with sophisticated vocabulary and, at times, intricate writing styles. Everything you need to know to answer test questions is in the passages and the questions themselves._

      - **DOK 2 \- Summary:**

        - _Tests knowledge that isn’t from explicit mcat material, with passages in a variety of fields._

        - _Analyzes comprehension, thinking, and reasoning skills on non medical items._

      - **Link to source:** [https://students-residents.aamc.org/whats-mcat-exam/critical-analysis-and-reasoning-skills-section-overview](https://students-residents.aamc.org/whats-mcat-exam/critical-analysis-and-reasoning-skills-section-overview)

- **Category 2: Spaced Repetition & the Anki Engine (the platform you’re modifying)**

  - **Subcategory 2.1: The Forgetting Curve & the Spacing Effect (foundations)**

    - "Distributed practice in verbal recall tasks: A review and quantitative synthesis" — Cepeda et al. (2006), Psychological Bulletin

      - **DOK 1 \- Facts:**

        - _The authors performed a meta-analysis of the distributed practice effect to illuminate the effects of temporal variables that have been neglected in previous reviews. This review found 839 assessments of distributed practice in 317 experiments located in 184 articles. Effects of spacing (consecutive massed presentations vs. spaced learning episodes) and lag (less spaced vs. more spaced learning episodes) were examined, as were expanding interstudy interval (ISI) effects. Analyses suggest that ISI and retention interval operate jointly to affect final-test retention; specifically, the ISI producing maximal retention increased as retention interval increased. Areas needing future research and theoretical implications are discussed._

      - **DOK 2 \- Summary:**

        - _Studied spacing and variables that haven’t been considered in many studies._

        - _Found that interstudy interval and retention interval both impacted final retention, with ISI increasing with retention interval_

      - **Link to source:** [https://pubmed.ncbi.nlm.nih.gov/16719566/](https://pubmed.ncbi.nlm.nih.gov/16719566/)

    - "Spacing effects in learning: A temporal ridgeline of optimal retention" — Cepeda et al. (2008), Psychological Science

      - **DOK 1 \- Facts:**

        - _To achieve enduring retention, people must usually study information on multiple occasions. How does the timing of study events affect retention? Prior research has examined this issue only in a spotty fashion, usually with very short time intervals. In a study aimed at characterizing spacing effects over significant durations, more than 1,350 individuals were taught a set of facts and—after a gap of up to 3.5 months—given a review. A final test was administered at a further delay of up to 1 year. At any given test delay, an increase in the interstudy gap at first increased, and then gradually reduced, final test performance. The optimal gap increased as test delay increased. However, when measured as a proportion of test delay, the optimal gap declined from about 20 to 40% of a 1-week test delay to about 5 to 10% of a 1-year test delay. The interaction of gap and test delay implies that many educational practices are highly inefficient._

      - **DOK 2 \- Summary:**

        - _Studied test delay with fact teaching and then review, 1 week test delay was significantly better than 1 year test delay._

        - _Optimal interstudy interval also scales with Test delay._

      - **Link to source:** [https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.2008.02209.x](https://journals.sagepub.com/doi/abs/10.1111/j.1467-9280.2008.02209.x)

  - **Subcategory 2.2: Spaced-Repetition Scheduling Algorithms (SM-2 → FSRS)**

    - "SuperMemo algorithm SM-2" — Woźniak (1990s), super-memory.com

      - **DOK 1 \- Facts:**

        - _Split the knowledge into smallest possible items._

        - _With all items associate an E-Factor equal to 2.5._

        - _Repeat items using the following intervals:_

        - _I(1):=1_

        - _I(2):=6_

        - _for n\>2: I(n):=I(n-1)\*EF_

        - _where:_

        - _I(n) \- inter-repetition interval after the n-th repetition (in days),_

        - _EF \- E-Factor of a given item_

        - _If interval is a fraction, round it up to the nearest integer._

        - _After each repetition assess the quality of repetition response in 0-5 grade scale:_

        - _5 \- perfect response_

        - _4 \- correct response after a hesitation_

        - _3 \- correct response recalled with serious difficulty_

        - _2 \- incorrect response; where the correct one seemed easy to recall_

        - _1 \- incorrect response; the correct one remembered_

        - _0 \- complete blackout._

        - _After each repetition modify the E-Factor of the recently repeated item according to the formula:_

        - _EF':=EF+(0.1-(5-q)\*(0.08+(5-q)\*0.02))_

        - _where:_

        - _EF' \- new value of the E-Factor,_

        - _EF \- old value of the E-Factor,_

        - _q \- quality of the response in the 0-5 grade scale._

        - _If EF is less than 1.3 then let EF be 1.3._

        - _If the quality response was lower than 3 then start repetitions for the item from the beginning without changing the E-Factor (i.e. use intervals I(1), I(2) etc. as if the item was memorized anew)._

        - _After each repetition session of a given day repeat again all items that scored below four in the quality assessment. Continue the repetitions until all of these items score at least four._

      - **DOK 2 \- Summary:**

        - _Spacing formula, devised as an algorithm with a learning loop based on how much was remembered and all._

      - **Link to source:** [https://super-memory.com/english/ol/sm2.htm](https://super-memory.com/english/ol/sm2.htm) _(verify)_

    - "A Stochastic Shortest Path Algorithm for Optimizing Spaced Repetition Scheduling" — Ye et al., ACM SIGKDD 2022 (the FSRS paper; free-access link in repo)

      - **DOK 1 \- Facts:**

        - _Spaced repetition is a mnemonic technique where long-term memory can be efficiently formed by following review schedules. For greater memorization efficiency, spaced repetition schedulers need to model students' long-term memory and optimize the review cost. We have collected 220 million students' memory behavior logs with time-series features and built a memory model with Markov property. Based on the model, we design a spaced repetition scheduler guaranteed to minimize the review cost by a stochastic shortest path algorithm. Experimental results have shown a 12.6% performance improvement over the state-of-the-art methods. The scheduler has been successfully deployed in the online language-learning app MaiMemo to help millions of students._

      - **DOK 2 \- Summary:**

        - _Study made a model \+ algorithm to minimize cost of review._

        - _Improved results by 12% over other methods and used in app, MaiMemo, where students directly benefit._

      - **Link to source:** [https://github.com/open-spaced-repetition/fsrs4anki](https://github.com/open-spaced-repetition/fsrs4anki)

    - "DSR model (Difficulty, Stability, Retrievability)" — Woźniak, via free-spaced-repetition-scheduler

      - **DOK 1 \- Facts:**

        - _What is the principle of FSRS?_

        - _FSRS springs from MaiMemo's DHP model (中文介绍), which is a variant of the DSR model proposed by Piotr Wozniak._

        -

        - _The model considers three variables that affect memory: difficulty, stability, and retrievability._

        -

        - _Stability refers to the storage strength of memory; the higher it is, the slower it is forgotten. Retrievability refers to memory's retrieval strength; the lower it is, the higher the probability that the memory will be forgotten._

        -

        - _In the present model, the following memory laws are considered:_

        -

        - _The more complex the memorized material, the lower the stability increase._

        - _The higher the stability, the lower the stability increase (also known as stabilization decay)_

        - _The lower the retrievability, the higher the stability increase (also known as stabilization curve)_

      - **DOK 2 \- Summary:**

        - _Stability is how strong the memory is and how long it lasts, retrievability is the chance the memory will be forgotten(lower better). With more complex(difficult) material, the stability increases slower._

      - **Link to source:** [https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler)

  - **Subcategory 2.3: Anki’s Architecture — Rust Backend & Scheduler (what you’ll change)**

    - Anki source code (ankitects/anki) — Rust backend, scheduler, protobuf interface

      - **DOK 1 \- Facts:**

        - _Backend is in rslib, with pylib having a bridge so it can be called from python_

        - _Uses Qt with Typescript/html/css_

        - _Protocol buggers define backend methods and formats_

      - **DOK 2 \- Summary:**

        - _Three tier architecture, Ui \- qt, logic \- python, Backend \- rust,_

        - _Multiple paths between languages with proto buffers and library bridges._

      - **Link to source:** [https://github.com/ankitects/anki](https://github.com/ankitects/anki)

    - Anki Manual — scheduling, FSRS, deck options

      - **DOK 1 \- Facts:**

        - _Scheduling in Rust layer, deck metadata in python and settings in proto_

        - _Deck options are presets that can be shared with overrides_

        - _Daily limits, learning teps, modifiers, ordering, burying, and other scheduling settings._

      - **DOK 2 \- Summary:**

        - _Lots of customization built into app with clear iteration shown._

        - _Modular components for easy addition._

      - **Link to source:** [https://docs.ankiweb.net](https://docs.ankiweb.net)

    - AnkiDroid (open-source Android client, AGPL)

      - **DOK 1 \- Facts:**

        - _Open source android client in kotlin._

        - _Separate repo, android backend, that exposes rust backend so desktop links to mobile._

        - _Protocol buffers from rust to kotlin_

      - **DOK 2 \- Summary:**

        - _Android client built to connect to desktop app with integrations to rust and desktop backend data._

        - _\[summary point\]_

      - **Link to source:** [https://github.com/ankidroid/Anki-Android](https://github.com/ankidroid/Anki-Android)

  - **Subcategory 2.4: Spaced Repetition in Medical Education (Anki in the wild)**

    - "Student-directed retrieval practice is a predictor of medical licensing examination performance" — Deng, Gluckstein & Larsen (2015), Perspect Med Educ \[tracks Anki use \+ MCAT scores vs. Step 1\]

      - **DOK 1 \- Facts:**

        - _Seventy-two medical students at one institution completed a survey concerning their use of user-generated (Anki) or commercially-available (Firecracker) flashcards intended for spaced repetition and of boards-style multiple-choice questions (MCQs). Other information collected included Step 1 score, past academic performance (Medical College Admission Test \[MCAT\] score, preclinical grades), and psychological factors that may have affected exam preparation or performance (feelings of depression, burnout, and test anxiety)._

        - _Results_

        - _All students reported using practice MCQs (mean 3870, SD 1472). Anki and Firecracker users comprised 31 and 49 % of respondents, respectively. In a multivariate regression model, significant independent predictors of Step 1 score included MCQs completed (unstandardized beta coefficient \[B\] \= 2.2 × 10− 3, p \< 0.001), unique Anki flashcards seen (B \= 5.9 × 10− 4, p = 0.024), second-year honours (B \= 1.198, p = 0.002), and MCAT score (B \= 1.078, p = 0.003). Test anxiety was a significant negative predictor (B= − 1.986, p \< 0.001). Unique Firecracker flashcards seen did not predict Step 1 score. Each additional 445 boards-style practice questions or 1700 unique Anki flashcards was associated with an additional point on Step 1 when controlling for other academic and psychological factors_

      - **DOK 2 \- Summary:**

        - Studied use of anki vs firecracker flashcards vs mcqs, showing that mcqs, different anki flashcards, and mcat score were all predictors of Step 1 score.

      - **Link to source:** [https://pmc.ncbi.nlm.nih.gov/articles/PMC4673073/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4673073/)

    - "How to learn effectively in medical school: test yourself, learn actively, and repeat in intervals" — Augustin (2014), Yale J Biol Med

      - **DOK 1 \- Facts:**

        - _Students in medical school often feel overwhelmed by the excessive amount of factual knowledge they are obliged to learn. Although a large body of research on effective learning methods is published, scientifically based learning strategies are not a standard part of the curriculum in medical school. Students are largely unaware of how to learn successfully and improve memory. This review outlines three fundamental methods that benefit learning: the testing effect, active recall, and spaced repetition. The review summarizes practical learning strategies to learn effectively and optimize long-term retention of factual knowledge._

        - _How do these studies impact learning in medical school? Whenever students learn factual knowledge, they should test themselves while learning, actively recall information, and retest the facts at expanding time intervals to make learning in medical school most effective. These learning strategies help students learn the most in the least amount of time. Studying according to scientific findings on the testing effect, active recall, and expanding repetition intervals assures optimal long-term retention of factual knowledge. It has to be emphasized that despite the obvious positive effects of these learning strategies on students’ performance, learning how to learn is not a standard part of the curriculum in medical school \[14,16\]. This lack is questionable._

      - **DOK 2 \- Summary:**

        - _Medical school preparation is usually done incorrectly by students. Review covers best methods with testing effect, active recall and spaced repetition._

      - **Link to source:** [https://pmc.ncbi.nlm.nih.gov/articles/PMC4031794/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4031794/)

    - "A Cohort Study Assessing the Impact of Anki as a Spaced Repetition Tool on Academic Performance in Medical School" (2023), Med Sci Educ

      - **DOK 1 \- Facts:**

        - _Seventy-eight students reported using Anki for at least one of the exams, and 52 students did not use Anki for any exam. Anki users scored significantly higher across all four exams: Course I (6.4%; p \< 0.001); Course II (6.2%; p = 0.002); Course III (7.0%; p = 0.002); and CBSE (12.9%; p = 0.003). Students who reported higher dependency on Anki for studying performed significantly better on the Course I, II, and CBSE exams._

      - **DOK 2 \- Summary:**

        - _Anki usage is relatively high among medical students(60%), with extremely positive effects, at least 6% higher on each exam they took._

      - **Link to source:** [https://link.springer.com/article/10.1007/s40670-023-01826-8](https://link.springer.com/article/10.1007/s40670-023-01826-8)

  - **Subcategory 2.5: Existing MCAT & Flashcard Study Tools**

    - Memm — MCAT-specific SRS web app built by two 99.9th-percentile scorers

      - **DOK 1 \- Facts:**

        - _We focused on the following four principles when designing Memm to ensure the most effective experience:_

        -

        - _1\. Spacing effect \- Newly introduced and more difficult pieces of information are shown more frequently, while older and less difficult pieces of information are shown less frequently._

        -

        - _2\. Testing effect \- Information retrieval through active recall is far more effective for memory consolidation than passive review._

        -

        - _3\. Interleaving \- Strategic ordering and mixing of subjects and topics while reviewing improves intersectional learning and overall recall._

        -

        - _4\. Desirable difficulties \- Introducing the right kinds of difficulties into the learning process greatly improves long-term retention._

        - _Memm was designed to address the pitfalls of Anki and unlock the full effectiveness of spaced repetition studying for the MCAT. We've heard stories from many students who were frustrated with Anki and its limitations, including a steep learning curve leading to inefficient studying, premade decks with poor flashcard quality and errors, and lack of informational organization leading to fragmented learning._

        -

        - _Memm solves these issues with a platform offering an easy-to-use interface, expert-created cards that undergo continuous updates, and integration between Cards and Sheets, plus additional contextual content._

        -

        - _The majority of our users have previously tried Anki but found Memm to be a more effective way for them to approach spaced repetition and achieve higher MCAT scores. You can read some of their stories on our blog or on Memm vs. Anki page._

        -

        - _Memm will help you with all the science sections of the MCAT, including Biological and Biochemical Foundations (Bio/Biochem), Chemical and Physical Foundations (Chem/Phys), and Psychological, Social, and Biological Foundations (Psych/Soc). Memm does not cover Critical Analysis and Reasoning Skills (CARS), as CARS is not content-based or memorization driven._

      - **DOK 2 \- Summary:**

        - Memm models itself on Anki, but integrates learning science principles and fixes many of Anki’s issues.

      - **Link to source:**

      - [https://memm.io/about/](https://memm.io/about/)

- **Category 3: The Science of Effective Learning**

  - **Subcategory 3.1: Learning vs. Performance (why fluency ≠ knowing)**

    - "Learning versus performance: An integrative review" — Soderstrom & Bjork (2015), Perspectives on Psychological Science

      - **DOK 1 \- Facts:**

        - _The primary goal of instruction should be to facilitate long-term learning—that is, to create relatively permanent changes in comprehension, understanding, and skills of the types that will support long-term retention and transfer. During the instruction or training process, however, what we can observe and measure is performance, which is often an unreliable index of whether the relatively long-term changes that constitute learning have taken place. The time-honored distinction between learning and performance dates back decades, spurred by early animal and motor-skills research that revealed that learning can occur even when no discernible changes in performance are observed. More recently, the converse has also been shown—specifically, that improvements in performance can fail to yield significant learning—and, in fact, that certain manipulations can have opposite effects on learning and performance. We review the extant literature in the motor- and verbal-learning domains that necessitates the distinction between learning and performance. In addition, we examine research in metacognition that suggests that people often mistakenly interpret their performance during acquisition as a reliable guide to long-term learning. These and other considerations suggest that the learning–performance distinction is critical and has vast practical and theoretical implications._

      - **DOK 2 \- Summary:**

        - _Learning should make permanent changes in comprehension/undesrstanding but performance is what’s measured. This gap is often misunderstood but very important_

      - **Link to source:** [https://journals.sagepub.com/doi/abs/10.1177/1745691615569000](https://journals.sagepub.com/doi/abs/10.1177/1745691615569000)

  - **Subcategory 3.2: Retrieval Practice / the Testing Effect**

    - "Test-enhanced learning: Taking memory tests improves long-term retention" — Roediger & Karpicke (2006), Psychological Science

      - **DOK 1 \- Facts:**

        - _Taking a memory test not only assesses what one knows, but also enhances later retention, a phenomenon known as the testing effect. We studied this effect with educationally relevant materials and investigated whether testing facilitates learning only because tests offer an opportunity to restudy material. In two experiments, students studied prose passages and took one or three immediate free-recall tests, without feedback, or restudied the material the same number of times as the students who received tests. Students then took a final retention test 5 min, 2 days, or 1 week later. When the final test was given after 5 min, repeated studying improved recall relative to repeated testing. However, on the delayed tests, prior testing produced substantially greater retention than studying, even though repeated studying increased students' confidence in their ability to remember the material. Testing is a powerful means of improving learning, not just assessing it._

      - **DOK 2 \- Summary:**

        - _Testing effect suggests that memory tests enhance retention, this was studied against the idea that this would just help restudy materials._

        - _Repeated studying improved confidence but repeated testing improved retention._

      - **Link to source:** [https://journals.sagepub.com/doi/10.1111/j.1467-9280.2006.01693.x](https://journals.sagepub.com/doi/10.1111/j.1467-9280.2006.01693.x)

    - "Retrieval practice produces more learning than elaborative studying with concept mapping" — Karpicke & Blunt (2011), Science

      - **DOK 1 \- Facts:**

        - _Educators rely heavily on learning activities that encourage elaborative studying, whereas activities that require students to practice retrieving and reconstructing knowledge are used less frequently. Here, we show that practicing retrieval produces greater gains in meaningful learning than elaborative studying with concept mapping. The advantage of retrieval practice generalized across texts identical to those commonly found in science education. The advantage of retrieval practice was observed with test questions that assessed comprehension and required students to make inferences. The advantage of retrieval practice occurred even when the criterial test involved creating concept maps. Our findings support the theory that retrieval practice enhances learning by retrieval-specific mechanisms rather than by elaborative study processes. Retrieval practice is an effective tool to promote conceptual learning about science._

      - **DOK 2 \- Summary:**

        - _Typically, learning activities aren’t the ones that require retrieval practice, the thing that produces greater gains according to the paper._

        - _This was preoven with comprehension based test questions._

      - **Link to source:** [https://www.science.org/doi/10.1126/science.1199327](https://www.science.org/doi/10.1126/science.1199327) _(verify)_

  - **Subcategory 3.3: Spacing and Interleaving (a strong ablation candidate for your study-feature test)**

    - "The shuffling of mathematics problems improves learning" — Rohrer & Taylor (2007), Instructional Science

      - **DOK 1 \- Facts:**

        - _Two key findings were observed. First, despite a twofold different in the amount of massed_

        - _practice assigned to Massers and Light Massers, there was not detectable difference in their_

        - _test scores. Thus, because the Light Massers correctly answered at least one practice_

        - _problem (as all analyses excluded subjects who did not correctly answer any practice_

        - _problems), this finding constitutes a null effect of overlearning (i.e., immediate postcriterion study). Admittedly, overlearning might have significantly boosted test scores if_

        - _the number of massed practice problems had varied by a factor of, say, 10 and not just two._

        - _However, any such effect would need to be extremely large before it would justify the_

        - _tenfold increase in study time. This is because learners have a finite amount of study time,_

        - _and they should invest this time in strategies that provide a good return on their investment._

        - _Thus, while an extremely large amount of overlearning might boost test scores, it would_

        - _probably not be efficient._

      - **DOK 2 \- Summary:**

        - _Light massers who studied twice as less as Massers had similar test scores, proving significant efficiency gains._

      - **Link to source:** [http://uweb.cas.usf.edu/\~drohrer/pdfs/Rohrer\&Taylor2007IS.pdf](http://uweb.cas.usf.edu/~drohrer/pdfs/Rohrer&Taylor2007IS.pdf)

    - "Interleaved practice improves mathematics learning" — Rohrer, Dedrick & Stershic (2015), Journal of Educational Psychology \[RCT-style\]

      - **DOK 1 \- Facts:**

        - _Interleaved practice produced higher test scores than did_

        - _blocked practice (Figure 4). Students tested 1 day after the review_

        - _showed a moderate benefit of interleaving, 80% (SD 33%) vs._

        - _64% (SD 42%), t(62) 2.39, p .02, d 0.42, 95%_

        - _confidence interval (CI) \[0.07, 0.77\]. Students tested 30 days after_

        - _the review showed a large benefit of interleaving, 74% (SD_

        - _39%) vs. 42% (SD 43%), t(62) 4.54, p .001, Cohen’s d_

        - _0.79, 95% CI \[0.43, 1.15\]. A two-way analysis of variance (with_

        - _practice schedule as a within-subject variable and test delay as a_

        - _between-subjects variable) showed that interleaved practice was_

        - _superior to blocked practice, F(1, 124\) 24.43, p .001, p_

        - _2_

        - _.165, and that test scores were greater at the shorter test delay, F(1,_

        - _124\) 7.69, p .01, p_

        - _2 .058. However, the interaction between_

        - _practice schedule and test delay was not statistically significant,_

        - _F(1, 124\) 2.84, p .09_

      - **DOK 2 \- Summary:**

        - _Interleaved practieced is better, especially with longer amounts of time, than blocked practice._

      - **Link to source:** [https://files.eric.ed.gov/fulltext/ED557355.pdf](https://files.eric.ed.gov/fulltext/ED557355.pdf)

  - **Subcategory 3.4: Transfer to Novel Problems**

    - "When and where do we apply what we learn? A taxonomy for far transfer" — Barnett & Ceci (2002), Psychological Bulletin

      - **DOK 1 \- Facts:**

        - _Despite a century's worth of research, arguments surrounding the question of whether far transfer occurs have made little progress toward resolution. The authors argue the reason for this confusion is a failure to specify various dimensions along which transfer can occur, resulting in comparisons of "apples and oranges." They provide a framework that describes 9 relevant dimensions and show that the literature can productively be classified along these dimensions, with each study situated at the intersection of various dimensions. Estimation of a single effect size for far transfer is misguided in view of this complexity. The past 100 years of research shows that evidence for transfer under some conditions is substantial, but critical conditions for many key questions are untested._

      - **DOK 2 \- Summary:**

        - _Far transfer is a largely debated viewpoint with some evidence pointing towards conditional transfer but conditions haven’t been fully pinpointed with many untested cases._

      - **Link to source:** [https://pubmed.ncbi.nlm.nih.gov/12081085/](https://pubmed.ncbi.nlm.nih.gov/12081085/)

  - **Subcategory 3.5: Comparative Efficacy of Techniques (what actually works)**

    - "Improving students’ learning with effective learning techniques …" — Dunlosky, Rawson, Marsh, Nathan & Willingham (2013), Psychological Science in the Public Interest

      - **DOK 1 \- Facts:**

        - _We selected techniques that were expected to be relatively easy to use and hence could be adopted by many students. Also, some techniques (e.g., highlighting and rereading) were selected because students report relying heavily on them, which makes it especially important to examine how well they work. The techniques include elaborative interrogation, self-explanation, summarization, highlighting (or underlining), the keyword mnemonic, imagery use for text learning, rereading, practice testing, distributed practice, and interleaved practice. To offer recommendations about the relative utility of these techniques, we evaluated whether their benefits generalize across four categories of variables: learning conditions, student characteristics, materials, and criterion tasks_

        - _Five techniques received a low utility assessment: summarization, highlighting, the keyword mnemonic, imagery use for text learning, and rereading. These techniques were rated as low utility for numerous reasons. Summarization and imagery use for text learning have been shown to help some students on some criterion tasks, yet the conditions under which these techniques produce benefits are limited, and much research is still needed to fully explore their overall effectiveness. The keyword mnemonic is difficult to implement in some contexts, and it appears to benefit students for a limited number of materials and for short retention intervals. Most students report rereading and highlighting, yet these techniques do not consistently boost students' performance, so other techniques should be used in their place (e.g., practice testing instead of rereading)._

      - **DOK 2 \- Summary:**

        - _Studied techniques for studying, specifically common and easily accessible ones by students. Summarization, highlighting, mnemonics, imagery, and rereading had low utility._

      - **Link to source:** [https://pubmed.ncbi.nlm.nih.gov/26173288/](https://pubmed.ncbi.nlm.nih.gov/26173288/)

  - **Subcategory 3.6: Production, Generation & Corrective Feedback (why free-response beats flip-and-reveal)**

    - "The generation effect: Delineation of a phenomenon" — Slamecka & Graf (1978), J. Experimental Psychology: Human Learning and Memory, 4(6), 592–604

      - **DOK 1 \- Facts:**

        - _Across five experiments, words that subjects generated themselves (from a rule + fragment/cue) were remembered better than the same words simply read._

        - _The generate-over-read advantage held on cued and uncued recognition, free and cued recall, and confidence ratings, and persisted across encoding rules, timed vs. self-paced presentation, and within- vs. between-subject designs._

      - **DOK 2 \- Summary:**

        - _Producing an answer yourself builds stronger memory than reading/recognizing it — the foundational evidence for free-text entry over the show-the-answer flip card._

      - **Link to source:** [https://andymatuschak.org/prompts/Slamecka1978.pdf](https://andymatuschak.org/prompts/Slamecka1978.pdf) _(verify)_

    - "When does feedback facilitate learning of words?" — Pashler, Cepeda, Wixted & Rohrer (2005), J. Experimental Psychology: LMC, 31, 3–8

      - **DOK 1 \- Facts:**

        - _258 subjects learned Luganda–English pairs; after tests with varying feedback conditions, a final test followed one week later._

        - _Supplying the correct answer after an incorrect response dramatically increased final retention (reported ~494%, nearly fivefold), whereas feedback after correct responses made little difference._

      - **DOK 2 \- Summary:**

        - _Corrective feedback after errors is what drives long-term retention._

      - **Link to source:** [https://pubmed.ncbi.nlm.nih.gov/15641900/](https://pubmed.ncbi.nlm.nih.gov/15641900/) _(verify)_

    - "Learning from Errors" (hypercorrection effect) — Metcalfe (2017), Annual Review of Psychology, 68, 465–489

      - **DOK 1 \- Facts:**

        - _Errorful learning followed by corrective feedback benefits retention; errors made with high confidence are corrected more readily than low-confidence errors (the hypercorrection effect)._

        - _Caveat: high-confidence errors can return if the correct answer is later forgotten, so corrective feedback and re-review matter._

      - **DOK 2 \- Summary:**

        - _Getting it wrong and then being corrected is a powerful learning event (especially for confident errors)._

      - **Link to source:** [https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010416-044022](https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010416-044022) _(verify)_

  - **Subcategory 3.7: Self-Regulated Study & Mastery-Based Allocation (why the system, not the student, should target weakness)**

    - "A Region of Proximal Learning model of study time allocation" — Metcalfe & Kornell (2005), J. Memory and Language; and "The promise and perils of self-regulated study" — Kornell & Bjork (2007), Psychonomic Bulletin & Review

      - **DOK 1 \- Facts:**

        - _Learners allocate study time by metacognitive judgments (judgments of learning): they choose not to study items they believe are already known, and prioritize items that are not-yet-known but seem learnable (the "region of proximal learning")._

        - _Self-regulated study helps when monitoring is accurate, but it hinges on judgments that are frequently miscalibrated — learners drop items they merely feel they know._

      - **DOK 2 \- Summary:**

        - _Left to themselves, students steer study by "I know this" feelings and systematically under-study material they misjudge as learned; allocation based on a measured signal is more reliable than self-directed choice._

      - **Link to source:** [http://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf](http://www.columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%20Kornell%202005.pdf) ; [https://link.springer.com/article/10.3758/BF03194055](https://link.springer.com/article/10.3758/BF03194055) _(verify)_

    - "The 2 Sigma Problem: The Search for Methods of Group Instruction as Effective as One-to-One Tutoring" — Bloom (1984), Educational Researcher, 13(6), 4–16 (+ mastery learning, Bloom 1968)

      - **DOK 1 \- Facts:**

        - _One-to-one tutoring combined with mastery learning produced roughly two standard deviations ("2 sigma") higher performance than conventional classroom instruction; the average tutored student scored above ~98% of conventionally taught students._

        - _Mastery learning requires students to reach a mastery threshold on prerequisites (checked by regular tests) and to receive extra support on not-yet-mastered material before advancing._

      - **DOK 2 \- Summary:**

        - _The largest documented learning gains come from adaptively concentrating effort on what a student has not yet mastered — the core principle behind weighting review toward measured-weak topics._

      - **Link to source:** [https://journals.sagepub.com/doi/10.3102/0013189X013006004](https://journals.sagepub.com/doi/10.3102/0013189X013006004) _(verify)_

- **Category 4: Readiness, Calibration & Metacognition (the honest "what score would I get?" problem)**

  - **Subcategory 4.1: Metacognition & Overconfidence (why students misjudge readiness)**

    - "Unskilled and unaware of it …" — Kruger & Dunning (1999), Journal of Personality and Social Psychology

      - **DOK 1 \- Facts:**

        - _People tend to hold overly favorable views of their abilities in many social and intellectual domains. The authors suggest that this overestimation occurs, in part, because people who are unskilled in these domains suffer a dual burden: Not only do these people reach erroneous conclusions and make unfortunate choices, but their incompetence robs them of the metacognitive ability to realize it. Across 4 studies, the authors found that participants scoring in the bottom quartile on tests of humor, grammar, and logic grossly overestimated their test performance and ability. Although their test scores put them in the 12th percentile, they estimated themselves to be in the 62nd. Several analyses linked this miscalibration to deficits in metacognitive skill, or the capacity to distinguish accuracy from error. Paradoxically, improving the skills of the participants, and thus increasing their metacognitive competence, helped them recognize the limitations of their abilities. (PsycInfo Database Record (c) 2025 APA, all rights reserved)_

      - **DOK 2 \- Summary:**

        - _Student’s are often overconfident about their abilities because they can reach the wrong conclusions and not realize that they did._

        - _Improving student’s performance helped them realize the limits of their performance, ironically._

      - **Link to source:** [https://doi.org/10.1037/0022-3514.77.6.1121](https://doi.org/10.1037/0022-3514.77.6.1121)

  - **Subcategory 4.2: Calibration & Proper Scoring Rules (Brier, reliability)**

    - "On calibration of modern neural networks" — Guo, Pleiss, Sun & Weinberger (2017), ICML

      - **DOK 1 \- Facts:**

        - _Confidence calibration \-- the problem of predicting probability estimates representative of the true correctness likelihood \-- is important for classification models in many applications. We discover that modern neural networks, unlike those from a decade ago, are poorly calibrated. Through extensive experiments, we observe that depth, width, weight decay, and Batch Normalization are important factors influencing calibration. We evaluate the performance of various post-processing calibration methods on state-of-the-art architectures with image and document classification datasets. Our analysis and experiments not only offer insights into neural network learning, but also provide a simple and straightforward recipe for practical settings: on most datasets, temperature scaling \-- a single-parameter variant of Platt Scaling \-- is surprisingly effective at calibrating predictions._

      - **DOK 2 \- Summary:**

        - _Calibration is predicting probabilities that represent true likelihood, most models are poorly calibrated, temperature scaling is effective._

      - **Link to source:** [https://arxiv.org/abs/1706.04599](https://arxiv.org/abs/1706.04599) _(verify)_

  - **Subcategory 4.3: Knowledge Tracing & Performance Prediction (modeling readiness)**

    - "Knowledge tracing: Modeling the acquisition of procedural knowledge" — Corbett & Anderson (1995), UMUAI (Bayesian Knowledge Tracing)

      - **DOK 1 \- Facts:**

        - _This paper describes an effort to model students' changing knowledge state during skill acquisition. Students in this research are learning to write short programs with the ACT Programming Tutor (APT). APT is constructed around a production rule cognitive model of programming knowledge, called theideal student model. This model allows the tutor to solve exercises along with the student and provide assistance as necessary. As the student works, the tutor also maintains an estimate of the probability that the student has learned each of the rules in the ideal model, in a process calledknowledge tracing. The tutor presents an individualized sequence of exercises to the student based on these probability estimates until the student has ‘mastered’ each rule. The programming tutor, cognitive model and learning and performance assumptions are described. A series of studies is reviewed that examine the empirical validity of knowledge tracing and has led to modifications in the process. Currently the model is quite successful in predicting test performance. Further modifications in the modeling process are discussed that may improve performance levels._

      - **DOK 2 \- Summary:**

        - _Tried to model knowledge growth, program is a tutor that estimates whether student learned rules as they work. This changes the exercises they provide until student mastered everything. Model proves to be effective with potential for improvements._

      - **Link to source:** [https://doi.org/10.1007/BF01099821](https://doi.org/10.1007/BF01099821)

  - **Subcategory 4.4: Automatic Question / Card Generation**

    - "Enhancing Student Learning with LLM-Generated Retrieval Practice Questions: An Empirical Study" (2025), arXiv \[LLM-generated cards, evaluated\]

      - **DOK 1 \- Facts:**

        - _Retrieval practice is a well-established pedagogical technique known to significantly enhance student learning and knowledge retention. However, generating high-quality retrieval practice questions is often time-consuming and labor intensive for instructors, especially in rapidly evolving technical subjects. Large Language Models (LLMs) offer the potential to automate this process by generating questions in response to prompts, yet the effectiveness of LLM-generated retrieval practice on student learning remains to be established. In this study, we conducted an empirical study involving two college-level data science courses, with approximately 60 students. We compared learning outcomes during one week in which students received LLM-generated multiple-choice retrieval practice questions to those from a week in which no such questions were provided. Results indicate that students exposed to LLM-generated retrieval practice achieved significantly higher knowledge retention, with an average accuracy of 89%, compared to 73% in the week without such practice. These findings suggest that LLM-generated retrieval questions can effectively support student learning and may provide a scalable solution for integrating retrieval practice into real-time teaching. However, despite these encouraging outcomes and the potential time-saving benefits, cautions must be taken, as the quality of LLM-generated questions can vary. Instructors must still manually verify and revise the generated questions before releasing them to students._

      - **DOK 2 \- Summary:**

        - _Uses LLM’s to make retrieval practice problems, verifies against not giving students questions at all, showing a 89% accuracy vs 73% accuracy. Limit of this experiments include lack of group using human written retrieval practice problems to evaluate effectiveness properly._

        - _\[summary point\]_

      - **Link to source:** [https://arxiv.org/abs/2507.05629](https://arxiv.org/abs/2507.05629)

  - **Subcategory 4.5: Grounding & Evaluating AI Output (hallucination, RAG, factuality)**

    - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" — Lewis et al. (2020), NeurIPS

      - **DOK 1 \- Facts:**

        - _Large pre-trained language models have been shown to store factual knowledge in their parameters, and achieve state-of-the-art results when fine-tuned on downstream NLP tasks. However, their ability to access and precisely manipulate knowledge is still limited, and hence on knowledge-intensive tasks, their performance lags behind task-specific architectures. Additionally, providing provenance for their decisions and updating their world knowledge remain open research problems. Pre-trained models with a differentiable access mechanism to explicit non-parametric memory can overcome this issue, but have so far been only investigated for extractive downstream tasks. We explore a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG) \-- models which combine pre-trained parametric and non-parametric memory for language generation. We introduce RAG models where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever. We compare two RAG formulations, one which conditions on the same retrieved passages across the whole generated sequence, the other can use different passages per token. We fine-tune and evaluate our models on a wide range of knowledge-intensive NLP tasks and set the state-of-the-art on three open domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract architectures. For language generation tasks, we find that RAG models generate more specific, diverse and factual language than a state-of-the-art parametric-only seq2seq baseline._

      - **DOK 2 \- Summary:**

        - _RAG is better at generating factual language than parametric only models._

      - **Link to source:** [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401) _(verify)_

    - "Survey of Hallucination in Natural Language Generation" — Ji et al. (2023), ACM Computing Surveys

      - **DOK 1 \- Facts:**

        - _Natural Language Generation (NLG) has improved exponentially in recent years thanks to the development of sequence-to-sequence deep learning technologies such as Transformer-based language models. This advancement has led to more fluent and coherent NLG, leading to improved development in downstream tasks such as abstractive summarization, dialogue generation and data-to-text generation. However, it is also apparent that deep learning based generation is prone to hallucinate unintended text, which degrades the system performance and fails to meet user expectations in many real-world scenarios. To address this issue, many studies have been presented in measuring and mitigating hallucinated texts, but these have never been reviewed in a comprehensive manner before. In this survey, we thus provide a broad overview of the research progress and challenges in the hallucination problem in NLG. The survey is organized into two parts: (1) a general overview of metrics, mitigation methods, and future directions; (2) an overview of task-specific research progress on hallucinations in the following downstream tasks, namely abstractive summarization, dialogue generation, generative question answering, data-to-text generation, machine translation, and visual-language generation; and (3) hallucinations in large language models (LLMs). This survey serves to facilitate collaborative efforts among researchers in tackling the challenge of hallucinated texts in NLG._

      - **DOK 2 \- Summary:**

        - _Summarizes different hallucination conditions among models and methods to mitigate hallucinations._

      - **Link to source:** [https://arxiv.org/abs/2202.03629](https://arxiv.org/abs/2202.03629) _(verify)_

  - **Subcategory 4.6: Automated Free-Text / Short-Answer Grading (LLMs as the grader)**

    - "Performance of GPT-4 on Automated Short Answer Grading" (2023) and LLM auto-assessment reviews (2024–25)

      - **DOK 1 \- Facts:**

        - _LLM graders (GPT-4 with prompt/rubric engineering) reach substantial agreement with human markers on short-answer grading (e.g., quadratic weighted kappa ≈ 0.68), and real deployments (e.g., a 100+ student course) report scoring and feedback comparable to human TAs._

        - _Key limitation: LLM feedback can be unfaithful — fluent but not grounded in the student's actual answer (fabricated critiques), so grading needs rubrics, grounding, and held-out evaluation before it can be trusted._

      - **DOK 2 \- Summary:**

        - _AI can grade free-text answers at near-human agreement, making a free-response study loop feasible — but only with rubric-grounding and evaluation, the same safeguards any honest AI feature requires._

      - **Link to source:** [https://arxiv.org/pdf/2309.09338](https://arxiv.org/pdf/2309.09338) ; [https://www.mdpi.com/2076-3417/15/10/5683](https://www.mdpi.com/2076-3417/15/10/5683) _(verify)_
