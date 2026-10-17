# Kengūra Treniruoklis — Project Notes

## Scope: Benjamin level only

This entire app — `kengura.html`, `kengura-archive.json/.js`, the figures, the
generators — is designed for **one Kangaroo level only: Benjamin** (called
**Bičiulis** in Lithuania). Everything else is out of scope.

### What "Benjamin" means

Math Kangaroo (Kengūros konkursas) splits competitors into age tiers. In
Lithuania the names go:

| LT name | International | Grade | Age | Status here |
|---|---|---|---|---|
| Nykštukas | Pre-Ecolier | 1–2 | 7–8 | not in scope |
| Mažylis | Ecolier | 3–4 | 9–10 | not in scope |
| **Bičiulis** | **Benjamin** | **5–6** | **11–12** | **the only target** |
| Kadetas | Cadet | 7–8 | 13–14 | not in scope |
| Junioras | Junior | 9–10 | 15–16 | not in scope |
| Senjoras | Student | 11–12 | 17–18 | not in scope |

A Benjamin paper has 30 problems split into three difficulty bands by
points awarded:

- **3-point block** (Q1–Q10): warm-ups. Single-step arithmetic, simple
  pattern-spotting, reading a clock, counting visible shapes. A child who
  knows the curriculum should clear most of these.
- **4-point block** (Q11–Q20): one or two non-obvious steps. Casework with
  small numbers, basic logic, a geometric observation, fractions/percent
  applied to a story, simple invariants.
- **5-point block** (Q21–Q30): the contest's real teeth. Each problem
  hides a *trick* — an invariant, a parity argument, a clever counting bijection,
  a knight's-tour-style search, a truth-tellers/liars web, optimisation under
  constraints. There is almost never a calculation-only path; you have to
  *see* the structure first. These are the problems that separate participants
  who memorised techniques from those who can think.

### Why this matters for the recommender

The "Praktikuotis šio tipo" (Practice this type) feature is supposed to give
the kid a **similar** problem after they finish or fail one. For Benjamin to
work pedagogically:

1. **Difficulty band has to match.** Practising a generated 3-point arithmetic
   sum after solving a 5-point parity puzzle is worse than nothing — it
   reinforces "the next one will be easy" and erodes contest stamina.
2. **Mechanic has to match, not just topic tag.** Two problems can both be
   tagged `aritmetika` and have nothing in common: one is `(20 + 5) · 3`,
   the other is `find the digit X such that 1ABCDE · 3 = ABCDE1`. The pattern
   tag is too coarse — what matters is the *trick category*: digit-puzzle vs.
   bracket-arithmetic vs. mean-of-set, etc.
3. **Generated content has to actually be Benjamin-grade.** A generator that
   only ever produces 3-point computations is fine for Q1–Q10 practice but
   should *never* surface as a "similar" suggestion for a 5-point problem.

### Practical implication for `pickGeneratorFor`

Today the pick is: pattern → list of generators → uniform random. There is
no difficulty awareness. So a 5-point logic-puzzle (e.g. 2025 Q24, the
Tomas-meluoja-antradieniais truth-teller) gets routed to `chocolateBreak`
or `cuts` because they share the `logika` tag, even though those generators
output 4-point fare with a fixed answer formula.

The right routing has three axes:

- **Difficulty band** of the source question (3 / 4 / 5 from `q.points`)
- **Mechanic family** (digit puzzle, parity/invariant, casework, optimisation,
  truth-tellers, geometry-area, sequence/recurrence, balance/weighing,
  spatial/cube, counting bijection, work/rate, age/algebra)
- **Surface topic** (the existing pattern tag — useful, but as a tiebreaker)

Practically: a 5-point source should only route to generators that produce a
5-point–shaped problem. If no generator currently produces work at that
band for that mechanic, the recommendation should say so and propose
another *archive* problem of the same mechanic instead — that's still a
better practice than a wrong-band random.

## Notes on data

- `kengura-archive.json` / `kengura-archive.js`: questions 2000–2025
  (Bičiulis only), with `prompt`, `options`, `correct`, `solution`,
  `points`, `patterns`, `figure`.
- `figures/{year}-q{n}.png`: per-question images cropped from the **test**
  PDFs (or the Bičiulis section of compendiums). For 2000–2005 and 2007–2009
  these were re-extracted on 2026-05-06 because the original build had
  pulled the strips from solution PDFs / wrong-grade sections — see
  `_refigure.py`.
- Figures: all 26 years × all questions have a `q.figure` (re-extraction
  passes on 2026-05-06; details under "Contest simulator + final figure
  pass" further down).
- Every paper has Q1–30 (2010–12 Q30 and 2016 Q3 were added on
  2026-10-11, `_add_missing_questions.py`). Points follow the number:
  Q1–10 = 3, Q11–20 = 4, Q21–30 = 5 (`_fix_points.py`; until 2026-10-11
  2000–2012 were all stored as 3-pointers).
- Contest-sim eligibility (`contestEligibleYears`): every Q keyed AND year
  is not 2006. Reason 2006 is excluded: the 2006 source PDF is **Mažylis
  (3-4 grade), not Bičiulis** — every Q is 3-point, so a kid scoring 30/30
  on it would walk away with a false sense of contest readiness. Since the
  2026-10-11 audit keyed 2000/2001 too: **25 of 26 years surface**.
- **Answer keys: trust the worked solution, not the answer table.** The
  2024 booklet's printed table was wrong 10 times; solution headers ("7. A"
  / "B7." + letter) are the reference, and 6 booklet keys are wrong even
  there (see `_fix_keys_audit.py`). The smoke test fails on unkeyed
  questions and broken point bands.
- Data pipeline: `python _rebuild_data.py` runs it all; order after a re-extraction: `_reextract_solutions.py` →
  `_fix_keys_audit.py` → `_apply_clean_solutions.py` → `_apply_audit_text.py` (prompts/options) →
  `_apply_kid_solutions.py` → `_mechanic_review.py` → `_fix_typos_2026.py`. Figures: `_recrop.py`.
- Note on `q.hasMissingOptionText`: PDF extraction failed on some option
  text in roughly half the years, but the contest UI handles this fine
  (letter-only buttons + the figure shows the real options). Don't filter
  these years out of the contest picker — pedagogical value of variety
  outweighs presentation friction. A separate `q.contestExclude` flag
  could be added later for individual questions whose **prompt** itself
  is garbled (the user has flagged a few of these manually); deferred.

## Methodology / playlist mode (2026-05-06)

Per-mechanic methodology blurbs live in `kengura.html` (`MECHANIC_METHODOLOGY`).
Each blurb is short Lithuanian text with three parts: *trick*, *key step*,
*pitfalls*. Together with the official per-question solution, this is the
two-layer pedagogy:

1. **Methodology blurb** = unified frame ("liars puzzles always need a parity
   anchor"). Hand-written, short, clean.
2. **Per-question solution** = official Kangaroo-team detail. Auto-extracted,
   cleaned by `_clean_solutions.py` (artifacts removed: `?`/`!` decorative
   bullets, redundant tail "Renkamės atsakymą X", broken option-text prefix,
   whitespace).

PDF extraction does occasionally collapse word boundaries (e.g.
"Devyniapatiniairutuliukai" instead of "Devyni apatiniai rutuliukai"). These
artifacts are localised and don't justify rewriting all 99 5-point solutions
by hand — the methodology blurb above carries the conceptual load.

The playlist is a 4-step mastery sequence per mechanic:
- Step 1 (read): methodology blurb shown alone, no question yet.
- Step 2 (worked): one archive question — preferably one band BELOW the
  source band — with its solution visible. The kid sees the move executed.
- Step 3 (try): one archive question at the source band. Hints available.
- Step 4 (mastery): three archive questions at the source band. No hints.
  ≥ 2/3 correct marks the mechanic as `mastered` in `store.masteredMech`.

## Stats schema (after 2026-05-06)

`store.mechStats[mech][band] = { attempts, wrong }` — replaces the legacy
`store.subStats` (kept for backwards compat but no longer surfaced).

`store.dueQueue["YYYY-N"] = { year, num, mech, band, dueAt, streak }` —
spaced-repetition queue. On a wrong answer the question goes in with
streak 0 and dueAt = +1 day. On each correct answer the streak bumps and
dueAt jumps to the next interval `[1, 3, 7, 14, 30]` days. After the
final interval the question graduates and is removed.

`store.masteredMech[mech] = timestamp` — set when the mastery check on a
playlist passes (≥ 2/3 correct).

## Methodological additions (2026-05-06, second pass)

After the playlist mode landed, the methodologist-parent review surfaced
six more upgrades. All six are now shipped:

**A. Misconception annotations.** Every 5-point archive question carries a
`q.misconceptions = { wrongLetter: shortReason }` map. When the kid picks a
wrong option, the explain box names the *specific misstep* ("Pamiršai, kad
Alė valgo 1/4 LIKUSIO, ne pradinio"). Data is hand-written in
`_solutions_kid.py`, applied via `_apply_kid_solutions.py`.

**B. Confidence calibration + negative-scoring mode.** Before submit the kid
picks one of *Tikrai žinau / Spėju iš dviejų / Atsitiktinai*. Stored in
`store.confStats` and surfaced on the results page (and parent dashboard)
as accuracy-by-confidence. A separate setting toggle ("−25 % už klaidą")
turns on the real Kangaroo penalty in test mode — this changes the
displayed score, not the test format.

**C. Tiered hints (notice → ask → suggest → tell).** `MECHANIC_HINTS` in
kengura.html holds 4-tier ladders for every mechanic. The "Užuomina"
button on archive cards now reveals one tier per tap (1/3 → 2/3 → 3/3),
and submission shows the per-question full solution as the 4th tier.

**D. Kid-Lithuanian solutions for all 250 5-pointers** (99 until the 2026-10-11 re-banding; also the 20 lower-band questions without an official solution). `q.solutionKid` is
shown in place of the auto-extracted official `q.solution` when present.
Style: 3 short paragraphs (pastebėjimas → veiksmas → patvirtinimas) in
2nd person voice. Data in `_solutions_kid.py`.

**E. Parent dashboard.** `/parent` view (button "👁 Tėvams" on home).
Shows: mastery (X/30 mechanics), this-week activity count, 14-day
heatmap of practice intensity, worst-3 mechanics with one-click
playlist links, last-session breakdown by category, confidence
calibration with red flag if "Tikrai žinau" accuracy < 80 %.

**F. Per-band pacing feedback.** Results page after each test shows time
spent per points-band (3/4/5) vs. recommended budget (1 / 2,5 / 5 min
per question). Bar turns red on overrun > 25 %.

## Racing reward game + stars + achievements (2026-06-14)

Gamification layer, all in `kengura.html` (no new files, no build step):

- **🏁 Lenktynių iššūkis** (`state.view = "raceChallenge"`). A 5-question
  gate drawn only from **4/5-point** archive questions that have answer
  keys (`buildRacePool`), biased to include some 5-pointers. Each answer
  routes through the existing `recordArchiveAnswer` so it still feeds
  mechStats / dueQueue / stars. Gate logic in `finishRaceChallenge`:
  < 3 correct → retry screen (no game); ≥ 3 → unlock. Score → difficulty:
  3✓ `easy`, 4✓ `medium`, 5✓ `hard`. Lives = correct − 2 (3✓→1 … 5✓→3).
- **🏎 Racing minigame** (`state.view = "race"`, `openRaceGame`). Canvas
  lane-dodger, 3 lanes, ←→ / A-D / on-screen buttons / canvas-half tap.
  Speed scales with difficulty and accelerates with distance; spawns
  always leave a free lane. Collision costs a life (brief invuln blink);
  0 lives → game over. `endGame` is **idempotent** (`if(g.over) return`)
  so a run never double-counts. Loop is `requestAnimationFrame`, guarded
  by `state.view === "race"`; `stopRaceGame` cancels the raf + keydown.
- **Stars** (`store.stars = {total, fromQ, fromTime, _timeSecRem}`).
  +1 per question answered (in `logActivity`); +1 per active minute via
  `startStarTimeHeartbeat` (visibility-gated so it can't be idle-farmed).
- **Achievements** (`store.achievements = {id: ts}`). 19-badge catalogue
  in `ACHIEVEMENTS`; `checkAchievements()` records + toasts newly earned,
  runs retroactively on load. Badge grid + stars + race record live on
  the home `rewardsCardHTML()` card.
- New store keys (`stars`, `games`, `achievements`) all have migration
  defaults in `loadStore`, so old saves load clean.

## Course layer: plan / drills / adaptive mastery (2026-08-23)

Teaching-standpoint build-out turning the toolbox into an adaptable
course. All in `kengura.html`:

- **Treniruočių planas** (`state.view = "plan"`, `openPlan`). Contest
  date in `store.plan.contestDate` (date input, countdown pill), last-3
  contest score trajectory, and a daily ~20-min session: warm-up (2 easy
  gens) → core → cool-down (recognition drill). Core priority in
  `planStepsForToday`: due backlog ≥ 4 > `needsSpeedWork()` sprint >
  next new mechanic > mixed set. Step completion tracked in
  `store.planDone[day]` via `state._planStep` + `markPlanStepDone()`
  (hooked into finishQuiz / finalizePlaylist / renderRecogResult;
  `renderHome` clears `_planStep` so abandoning a step doesn't mark it).
- **Learning track** `MECHANIC_ORDER` — hand-authored prerequisite order
  over the 30 mechanics (counting-ways before arrangement, invariant
  before state-game…). `nextMechanicToLearn()` picks the first
  unmastered one with archive content.
- **Recognition drill** (`state.view = "recog"`, `openRecogDrill`).
  "Kokia gudrybė?" — 10 archive 4/5-pt questions, kid picks the
  *mechanic* (4 options), no solving. Trains the real 5-pt bottleneck.
  Stats in `store.recogStats`; counts as activity (stars/streak) but
  does NOT touch mechStats or seenQ.
- **Mixed sets** (`openMixedSet`, playlistMech `"__mixed__"`).
  Interleaved 6-question set from recently practiced mechanics
  (`store.mechRecent` keys), mechanic pill hidden until submit
  (`hideMech` opt in `renderPlaylistQuestion`). ≤ 2 per mechanic.
- **Adaptive mastery loop.** Mastery now needs ALL correct (3/3; 2/3
  survives 5-option guessing ~10 %). Fail with a lower band available →
  "Pabandyti X t. lygiu" (openPlaylist forcedBand); pass below 5 with a
  5-pt pool → "Kilti į 5 t.". Stale mastery (> 60 d) opens a light
  2-question retest instead of the full playlist — pass refreshes the
  timestamp, fail clears mastery and offers the full playlist.
  `pickPlaylistContent` prefers questions unseen in 14 d
  (`store.seenQ`, marked in recordArchiveAnswer + finishContest).
- **Signals used for routing.** `store.mechRecent[mech]` = last ≤ 10
  attempts; `weakestMechanics` uses the windowed rate when ≥ 4 samples.
  Confident-wrong ("Tikrai žinau" + wrong) flags the dueQueue item
  (`confWrong`), sorts first in `dueNow()`, gets a special callout in
  the archive card and a parent-view stat. `needsSpeedWork()` (3-pt avg
  > 75 s over last 3 sessions) routes to the **sprint** (`startSprint`:
  10 × 3-pt gens, 10-min timer, verdict banner on results).
- **Motivation.** Mission card now offers a primary + "arba:" alternative
  (choice > assignment). Star shop (`SHOP_COLORS`, night track 100⭐,
  extra race life 20⭐) — `store.stars.spent`, `starsAvailable()`,
  `store.shop`; cosmetics apply in `openRaceGame`. Correct answers name
  the skill ("Pastebėjai gudrybę: X"). Contest card gained a strategy
  explainer (3-pt first, skip-vs-guess under −25 %) and a score
  trajectory pill. Two new badges: recog20, plan5.

## 5-pt generator block (2026-08-23, second pass)

13 new parameterized contest-grade generators in `kengura.html`
(GENERATORS section "5 TAŠKŲ BLOKAS"). Design rules, learned from the
stackProjection incident:

- **Every answer is COMPUTED** — BFS (cupsFlip), DP (nimGame, gridPaths,
  blackboardMin subset-sum), maximum bipartite matching (dominoMax,
  Kuhn's algorithm), permutation brute force (raceLogic5 — clues are
  added until exactly 1 of 120 orderings survives), or exhaustive search
  (digitReversal, appendDigit, remainderPuzzle, erasedAverage). Never a
  hard-coded formula.
- **Every question carries `q._check`** (params + answer); the smoke
  test re-derives each answer with a SEPARATE implementation (60 seeds
  per generator). Keep this pattern for any future generator.
- New coverage by mechanic (all difficulty 5 unless noted): liarsCount
  (truth-tellers), cupsFlip + blackboardMin (invariant), digitReversal
  (digit-puzzle), gridPaths (counting-ways), nimGame (state-game — first
  ever), raceLogic5 (logic-clues), equalGroups (partition), appendDigit
  (place-value — first ever), remainderPuzzle (divisibility), cubeNet
  (cube-net — first ever, difficulty 4), erasedAverage (arith-compute),
  dominoMax (tiling — first ever).
- Result: **all 99 5-pt archive questions now route to practice** — 87
  to a band-matched generator, 12 to same-mechanic archive fallback,
  0 dead-ends (was: many "none").

## Option cleanup + word respacing (2026-05-06, fourth pass)

PDF extraction left two stubborn artifacts the user flagged:

**1. Bogus option values (615 across 148 questions).** Many image-option
questions had options stored as `(A)`, `(B)`, `B)`, `C` (placeholder)
or — worse — long fragments from neighbouring questions ("Kam lygi šių
7 atkarpų ilgių suma..."). `_clean_options.py` detects junk via:
- placeholder regex
- length > 80 chars (real Kangaroo answers ≤ 50)
- starts with question-word (Kuris/Koks/Kam/Kiek/Atkarpos/...)
- trailing hyphen (PDF line-wrap break)

For each question it then sets `q.imageOnlyOptions = true` if all 5
empty (61 questions) or `q.hasMissingOptionText = true` for partial
(90 questions). The archive-card UI:
- Image-only → letter-only buttons + help line "Atsakymai – paveikslėlyje."
- Mixed → text for valid options, italic *— atsakymas paveikslėlyje —*
  placeholder for empty ones

**2. Run-together words (~2400 fields).** PDF extraction sometimes drops
spaces between words ("jogAdelėatbėgotrečia"). `_respace_words.py`
applies five conservative heuristics:
- Rule 1: lowercase → UPPERCASE break (safest)
- Rule 2: function-word peel — WHITELIST ONLY (`o, ir, ar, jog, tai,
  kad, bet, tad`). DO NOT add `pas`, `iš`, `į`, `su`, `pa`, `ant`, `po`,
  `nuo`, `tarp`, `be` etc. — they're also Lithuanian verb/noun prefixes
  inside legitimate words and over-split them ("pasakyta" → "pas akyta")
- Rule 3: suffix-then-lowercase split for known endings
- Rule 4: digit → letter break (with units whitelist: cm, m, kg, ...)
- Rule 5: vowel + consonant-cluster break (tr/kr/br/pr/...)
- Rule 6: glue-word peel (curated list of common Lithuanian words)

`_fix_oversplit.py` reverses any over-split that an earlier (less safe)
function-word list introduced — particularly `"pas \w*"` → `"pas\w*"` for
known pas-prefixed words.

**Residual artifact known:** ~5 % of words remain merged in subtle
positions (e.g. `"iš kartpo"` → should be `"iš karto po"`). Fixing
these properly needs either (a) a Lithuanian dictionary library or
(b) re-OCR'ing the PDFs with `pymupdf get_text("dict")` for better
layout-aware spacing. NOT fixable with Whisper (audio-only).

## Contest simulator + final figure pass (2026-05-06, third pass)

**Figures now 100 %.** Years 2006, 2014, 2015, 2016, 2017 (previously
figureless) re-extracted from `2006LT.pdf` and `benjamin_lt (5/6/7/8).pdf`.
All 777 archive questions across 26 years have a `q.figure`. The same
`_refigure.py` handles portrait compendiums (2000–2009) and landscape
booklets (2013–2025) — see SOURCES and LANDSCAPE_OVERRIDES dicts.

**Contest simulator (`state.view = "contest"`).** Strict Kangaroo
conditions: 75 min hard timer, 30 questions from a real past paper,
−25 % penalty per wrong answer, **no hints, no playlists, no confidence
picker, no "practice similar"**. Questions can be skipped (skipped =
0 points, no penalty — exactly like the real contest). The strip at
top shows all 30 numbers; filled = answered, current = highlighted.
Results page shows: score with/without penalty, per-band breakdown
(green ≥70 %, red <40 %), wrongs with misconception annotation if 5pt,
skipped with the kid solution, and a 10-contest history trend.

Eligible years (have answer keys for every question): 17 of 26 — enough
for weekly contests for ~4 months without repeating. Stored separately
in `store.contests` (last 30 retained).

## File map

- `kengura.html` — the entire treniruoklis app (UI + generators + archive
  rendering). Single file, no build step.
- `kengura-archive.js` — `window.KENGURA_ARCHIVE = {...}` data bundle
  loaded by `kengura.html`. Mirror of the `.json`.
- `kengura-archive.json` — same data as the `.js`, indented for diffs.
- `_extract.py` — pdfplumber-based question text extractor (CID/diacritic
  cleanup, column-aware page extraction, junk filtering, pattern tagging).
- `_extract_solutions.py` — answer key + solution-paragraph extractor.
- `_build_archive.py` — end-to-end build pipeline.
- `_refigure.py` — figure-only re-extraction (added 2026-05-06).
- `_smoke_test.cjs` — Node smoke test (`node _smoke_test.cjs`): runs the
  inline app script with a stubbed DOM and checks every generator across
  80 seeds (unique options, valid correctIndex, no undefined/NaN leaks),
  archive shape + `aiBuildOpts`, band-honest practice routing, quiz-count
  fill, and bans algebra/factorial/mod notation in kid-facing hint copy.
  **Run it after every change to kengura.html.**
- `figures/` — per-question PNGs.
- Data layer (2026-10-11), run all with `python _rebuild_data.py`:
  `_reextract_solutions.py` (+ `_pagetext.py` for stacked fractions),
  `_fix_keys_audit.py`, `_apply_clean_solutions.py` (+ `_clean_solutions.json`),
  `_apply_audit_text.py` (+ `_audit_text.json`), `_apply_kid_solutions.py`
  (+ `_solutions_kid.py`), `_mechanic_review.py`, `_fix_typos_2026.py`.
  One-off: `_fix_keys_2024.py`, `_fix_points.py`, `_add_missing_questions.py`.
- Figures: `_recrop.py` (layout-based crops), `_trim_figures.py` (blank
  strips); bump `FIGS` in `sw.js` after changing any PNG.
- `_plan_sim.cjs` — plan simulator (seeded, reproducible).
- `Solutions/` — 2006 + the full 2014–2017 solution booklets.
- `*.pdf` — source materials. `200xLT.pdf` and `TMK0x_lietuviu.pdf` are
  test booklets; `200xspB.pdf` and `200xkengura.pdf` are solution
  compendiums; `benjamin_lt (*).pdf` are the modern (2013+) test booklets.

## Macro-cycle, sound/effects, star economy, track, recap (2026-10-10)

Prep-course layer for a 2–3 month run-up. All in `kengura.html`; smoke
test section "macro-cycle + stars" covers it.

- **Phases** (`planPhase()`, `PLAN_PHASE`): from `daysToContest()`:
  `foundation` > 60 d (sprint ↔ new-mechanic alternating by day parity),
  `build` 11–60 d (old behaviour: due ≥ 4 > speed > next mechanic >
  mixed), `taper` ≤ 10 d (NO new mechanics: due ≥ 1 > mixed/sprint
  alternating). No date → `build`. Eve of contest = warm-up + read
  strategy + rest; contest day = single "none" step.
- **Contest day** (`isContestDay`, `store.plan.contestWeekday`, default
  Saturday, selectable in the plan view): core step becomes a 75-min
  contest sim on an unplayed eligible year (`pickContestYear`). Also
  forced at T-3 days (dress rehearsal). `finishContest` ticks the plan
  step even when the contest was launched from the home card.
- **Mastery decay** shrinks from 60 d to 28 d while a contest date is in
  the future (`masteryDecayDays()`).
- **Sound** (`Sfx`): WebAudio synth, no files. `store.settings.sound`
  toggle on the home settings row. Bank: correct / wrong / star / badge /
  mastery / plan / warn / crash / gameover / click / tick. Plays only in
  UI handlers (never inside `recordArchiveAnswer`, which bulk-records).
  Contest sim is silent except one `warn` at 5 min left. Quiz timer
  warns at 60 s.
- **Effects** (`Fx`): `floatStars(n)` on every star award, `confetti()`,
  `celebrate(kind)` = sound + confetti. `showToast(icon, html)` is the
  generic bottom toast (achievements use it too).
- **Stars**: `starsForAnswer(correct, band)` → 1 / 2 (correct 4-pt) /
  3 (correct 5-pt). `logActivity(correct, band)` — callers pass the
  band. Bonuses (`store.stars.fromBonus`): +10 for all plan steps of a
  day (once, `planDone[day].bonus`) + one free race ticket
  (`store.games.freeRaces`, `openFreeRace` = medium, 2 lives, no gate),
  +5 perfect session (≥ 5 Q), +5 first mastery of a mechanic. Daily
  stars are logged in `store.activity[day].stars`; `starsThisWeek()`
  sums Mon–Sun.
- **Weekly goal**: `store.plan.weeklyStarGoal` (default 150) and
  `store.plan.weeklyReward` (free text) set in the parent view; progress
  bar on the rewards card.
- **Race gate** admits 3/4-pt questions in the foundation phase while
  < 5 mechanics are mastered (`buildRacePool`), else 4/5-pt as before.
- **Track card** (`trackCardHTML`): 30-node path in `MECHANIC_ORDER`
  (only mechanics with ≥ 3 archive Qs — `trackMechanics()`), states
  done / stale / current, finish flag with days left; node click opens
  the playlist.
- **Weekly recap** (`weeklyRecapHTML`): collapsible card on home once
  there is activity this week; on Mondays it opens expanded and shows
  LAST week. Active days, questions, accuracy, stars, mechanics
  mastered, contest score vs previous, and a focus mechanic (weakest
  ≥ 40 % errors, else next on the track).

## Held-out papers, diagnostic, foundation tuning (2026-10-10, second pass)

- **Held-out contest papers** (`reservedYears()`, `RESERVED_YEAR_COUNT = 3`):
  the newest 3 eligible years NOT yet played as a contest are skipped by
  every practice picker — `archiveQsForMech` (playlists, track, next
  mechanic), `openMixedSet`, `buildRecogPool`, `buildRacePool`,
  `findSimilarArchive`. Archive browser shows them as 🔒 disabled.
  Playing a year releases it. Waiver: a mechanic with < 3 questions
  outside the reserved years keeps its reserved ones (otherwise
  `arrangement` / `state-game` would fall off the track).
- **`pickContestYear`** now prefers unplayed non-reserved years outside
  the taper (reserved ones are saved for the final rehearsals) and among
  candidates picks the paper with the fewest `seenQ` marks.
- **Diagnostic paper** (`needsDiagnosticContest`): contest date set, no
  contest played, > 1 day left → the day's core is a contest labelled
  "Diagnostinis".
- **Foundation cadence**: contest day only every second week (absolute
  week parity in `isContestDay`); sprints only while
  `needsSpeedWork()` or fewer than 2 sprint sessions exist, else the
  day goes to the next mechanic.
- **Prep defaults**: setting a contest date for the first time switches
  on `askConfidence` and `negativeScore` (toast explains; still
  toggleable on home).
- **Shop sink**: race ticket for `SHOP_TICKET_COST = 30` ⭐ →
  `store.games.freeRaces++` (repeatable).
- **Plan timeline** (`planTimelineHTML`): start → contest bar split into
  the phases with a today marker; start = earlier of first activity day
  and today, capped at 90 days before the contest.
- **Track captions**: a node tap names the mechanic in `#trackCaption`
  with a Mokytis/Pakartoti button (no hover on phones).
- **Recognition freshness**: `store.recogSeen` marks shown questions;
  `openRecogDrill` serves unseen-in-14-days first.

## Plan simulator + starvation fixes (2026-10-10, third pass)

`_plan_sim.cjs` — `node _plan_sim.cjs [days] [accuracy] [--quiet]` runs
the real plan logic day by day with a mocked clock and a synthetic kid,
and prints the schedule, a per-phase tally, mastery and contest spacing.
**Run it after touching planStepsForToday, the due queue, mastery rules
or MECHANIC_ORDER.** Reference numbers after this pass (84 days, track = 25–26 mechanics
with ≥ `TRACK_MIN_QS` = 4 keyed questions outside the reserved years):
accuracy 0.70 → 16 mastered (the 5-pt-heavy ones first), 0.85 → all,
0.95 → all; no two papers within 5 days; taper papers 0/30 practised
beforehand; no mastery set under 2 items.

What the first simulation exposed and what changed:

- **Due queue ate the core.** Every archive answer (correct too) was
  scheduled, and 4 due items replaced the day's core → 28 of 50 build
  days were review even at 95 % accuracy. Now only MISTAKES enter the
  queue (`recordArchiveAnswer`: correct + not queued → nothing); review
  is the warm-up (`dueWarm`, ≤ 3 items via `openDueQueue(3)`); a full
  review core needs ≥ 10 due (≥ 5 in the taper).
- **Track order was easy-first**, so casework / truth-tellers /
  invariant sat at positions 20+. `MECHANIC_ORDER` is now ordered by
  contest value (5-pt mechanics first, prerequisites kept), then 4-pt
  only, then 3-pt only.
- **Per-band mastery.** `store.masteredBand[mech]` = highest band
  passed; `store.masteredMech[mech]` only at `mechTopBand(mech)`. Track
  nodes show a half-green "part" state with the band number. The plan
  returns `{mech, band}` from `nextMechanicTarget()` /
  `mechTargetFor()`: foundation caps the target at band 4 (build/taper
  come back for the 5), bands count only with ≥ 2 questions (mastery
  needs 2 items), two fails at a band (`store.mechAttempts`) step the
  target down, two fails at the lowest band park the mechanic for 7 d.
- **Reserved-year waiver is decided per mechanic, never per band** — a
  per-band waiver made the plan ask for a band the picker then refused,
  serving the same 4-pt set forever.
- **Contest spacing** (`isContestDay`): the weekly slot yields within 2
  days of the T-3 rehearsal and within 5 days of any played paper.

## Five fix/review loops (2026-10-10, fourth pass)

Each loop = simulate (`_plan_sim.cjs`) + read + fix + smoke + commit.

- **Loop 1 — second minigame + honest time.** `openJumpGame` (Kengūros
  šuolis, canvas runner: Space/↑/tap), shared `renderGameOver`,
  `renderGamePick` for unlocks and tickets (`openFreeRace` opens the
  picker), badges `jump1`/`jump500`, `store.games.jumpBest/jumpPlays`.
  `PLAN_STEP_MIN` + `planMinutes()` replace the fixed "~20 min". Smoke
  test drives both game loops headlessly (no-op canvas ctx + queued rAF).
- **Loop 2 — adaptive cadence + proportional taper.** `isContestDay`:
  a paper is due every 7 d (14 in foundation); the preferred weekday
  takes it after ≥ 5 d, a missed weekday hands it to the first day it is
  overdue by one (weekend-off kid: 10 papers instead of 2).
  `planTaperDays()` = 12 % of the run clamped 4–10, anchored by
  `store.plan.startDate` (set when the date is first entered; falls back
  to the earliest activity day). Mission card uses `nextMechanicTarget`
  with the band; parent view counts mastery against `trackMechanics()`.
  Simulator gained `--skip=<weekdays>`.
- **Loop 3 — one "do this now".** With a date set the mission card
  leads with today's next undone plan step (`action: 'planStep'`).
  `askConfidenceNow()` hides the confidence picker in the sprint.
  Per-minute stars only in `STAR_TIME_VIEWS` (quiz, playlist, recog,
  archive, contest, results) — never on home/plan/games.
- **Loop 4 — pacing of hard mechanics.** Park time = 7 × (fails − 1)
  days. Stale retest runs at `masteredBandOf(mech)`; a failed retest
  drops one band (`masteredBand`) instead of wiping. Recap focus needs
  ≥ 4 samples. Home nudges when no contest date is set.
- **Loop 5 — verification.** Browser pass on home/plan/games, final
  simulation table below, notes.

Simulation reference (84 days, daily kid, 3 reserved years):
accuracy 0.60 → 8 full + 3 partial, 0.70 → 13 + 2, 0.85 → all 26,
weekend-off 0.80 → 20 full, 10 papers; 30-day start 0.85 → 15.

## Loops 6–15 (2026-10-10, fifth pass)

- **6 — legacy saves.** Smoke test loads a pre-prep-layer save and
  checks every new default; ancient mastery reads as stale on the
  track. Mastery-pass copy distinguishes a partial band; quotes the live
  decay window. Simulator `--learn` (accuracy +0.06 per exposure).
- **7 — date edges.** Timeline no longer emits NaN widths when the
  contest is today or the dates are inverted; a past contest date
  schedules no papers. Smoke: contest today / past / inverted / eve.
- **8 — audio + cost.** `Sfx` creates its AudioContext only after the
  first user activation (`navigator.userActivation`). Measured on a
  6-week store: `planStepsForToday` 3.5 ms, track 0.4 ms.
- **9 — honesty marker.** `finishContest` stores `practisedBefore`
  (questions of that paper already met in practice); results page and
  parent view show it, flagged at ≥ 6.
- **10 — one band logic.** `openPlaylist` without an explicit band asks
  `mechTargetFor`, so every entry point lands on the plan's band.
  Mechanic list shows partial-band pills. Simulator `--miss=P`.
- **11 — rehearsal slide.** A missed T-3 rehearsal moves to T-2 unless
  a paper was played in the last 4 days.
- **12 — long-arc badges.** plan20, contest5, clean60, track.
- **13 — anti-exploit.** `finishQuiz` credits the plan step only when
  ≥ half the questions were answered.
- **14 — browser pass.** Contest results (marker), parent view (contest
  list), mechanic list pills, badges; no console errors.
- **15 — notes + table.**

Simulation (84 days unless noted; `node _plan_sim.cjs …`):
0.70 flat → 13 full; 0.70 --learn → 18; 0.85 → all 26; weekend-off
0.80 → 20, 10 papers; erratic 0.70 --learn --miss=0.3 → 12, 11 papers;
30-day 0.85 → 15; 45-day 0.80 --learn → see table in git log.

## Loops 16–25 (2026-10-10, sixth pass)

- **16 — calibration in playlists.** Try/mastery steps ask "Kiek esi
  tikras?" (`state.playlistConf`), passed to `recordArchiveAnswer`.
- **17 — training days.** `store.plan.trainingDays` (toggles in the
  plan view, ≥ 2). `isTrainingDay()`: streak counts missed training days
  only; rest days have no plan steps, no bonus, no paper; week strip and
  home card show 🛌. Simulator mirrors `--skip` into it.
- **18 — papers count as activity.** `creditContestActivity` (streak,
  activity, stars) in `finishContest`. Found by the simulator: streak 3
  after 12 weeks for a kid who sat 10 papers.
- **19 — phone width.** Verified via a 360px iframe (the extension's
  window resize does not change the viewport): no horizontal overflow on
  home/plan/parent/picker/jump; canvases now `max-width:100%`.
- **20 — backup/restore.** Parent view exports the store as JSON
  (`exportProgress`) and imports it back (`importProgressFile`,
  shape-checked, confirm, reload).
- **21 — parent view shows the weekly recap.**
- **22 — combo cheers** at 3, 5 and every 10 correct in a row
  (`state._combo` in `logActivity`; contests stay silent).
- **23 — "Dar kartą"** label when returning to a mechanic after fails.
- **24 — rest day no longer shows "plan done"** (`allDone` needs steps).
- **25 — notes + push.**

Simulation after this pass (84 d, --learn): daily 0.80 → 25/26, streak
intact; weekend-off 0.80 → 24/25, 10 papers, streak 58.

## Loops 26–45 (2026-10-10, seventh pass)

- **26** many badges at once → one summary toast. **27** hero shows
  stars (+ weekly goal) and streak freezes left. **28** ladder buttons
  only offer bands with ≥ 2 questions. **30** parent weak list needs
  ≥ 4 samples. **33** race gate prefers unseen questions. **36** quitting
  a mastery check after a miss = failed attempt (`noteMechAttempt` in
  `exitHome`). **38** diagnostic also when the last paper is > 60 d old
  (`DIAGNOSTIC_STALE_DAYS`). **39** recap marks partly-practised papers.
  **44** figure `alt` text.
- **29 — profiles.** `kengura_meta` = {profiles:[{id,name}], active};
  default profile keeps `kengura_v1`, others `kengura_v1_<id>`
  (`storeKeyFor`). Parent view: switch / add (prompt) / delete
  (confirm). Hero shows the active name when > 1 profile.
- **31 — offline.** `sw.js` (network-first shell, cache-first
  `figures/`), `manifest.webmanifest`, `icon.svg`; registration skipped
  on `file:` and in the harness. **43** static checks pass.
- **32 — first-run parent card** (date, days, prize) when no date and no
  answers yet.
- **34 — stale rechecks are scheduled.** `staleMechanicToRecheck()`
  takes the core before the mixed fallback in every phase (120-day sim:
  43 idle mixed days → 43 recheck playlists).
- **37 — long foundation** lifts the band-4 cap once every capped target
  is done (`nextMechanicTarget` walks again as "build").
- **40 — unload-save bug.** `beforeunload` → `saveStore` overwrote an
  imported store and re-saved a deleted profile. `_storeFrozen` silences
  saves across those reloads. Verified live.
- **35** English-leak sweep: nothing. **41** matrix (--learn where noted):
  0.70 → 20/25, 0.85 → all, weekend-off 0.80 → 22, streak 58; erratic
  0.70 miss 30 % → 14; 120 d → all; 45 d → 22; 30 d (flat 0.85) → 18.
- **42/45** notes + push.

## Grammar passes + "surprise 30 questions" UX fix (2026-10-10)

- **Grammar, 4 passes** over all Lithuanian UI/generator/method text:
  (1) spelling and word choice, (2) numeral agreement — every
  "number + noun" template goes through `pluralForm(n, nomSg, nomPl,
  gen)` (verified on 2,376 rendered generator strings), (3) punctuation:
  „…“ quotes, space before %, "pvz.,", "t. y.", em dash → spaced en dash
  everywhere, (4) terminology: "gudrybė" only (no "triukas"/"mechanika"
  in kid-facing text), "tiesuoliai", "dalijasi/dalytis". Kid is addressed
  with "tu" and masculine participles. **Keep new copy to these rules.**
- **Surprise 30 questions.** The results page's only primary button was
  "Naujas testas", which starts a free test at `settings.count` (30 if
  "30 (Kengūra)" was ever tapped) — reached right after a 2-question
  plan warm-up. Now: `state._resultsFromPlan` → primary "Toliau pagal
  planą: <next step>", "Naujas testas (N klausimų · M min)" secondary;
  every free-test button states its size (`newTestSizeLabel()`).
- **Contest intro** (`renderContestIntro`, view "contestIntro") replaces
  the browser confirm: what to expect, diagnostic note on day 1, and
  "Ne dabar" for plan papers → `store.plan.contestPostponedDay` makes
  `isContestDay`/`needsDiagnosticContest` false for that day only.
- **Paper year was random per render** (`pickContestYear` tie-break used
  Math.random) — the plan label, intro and opened paper could differ.
  Tie-break is now a hash of date + year: stable within a day.

## Loops 46–55 (2026-10-10, eighth pass)

- **46/47 — no dead ends after a plan step.** Playlist, recognition and
  contest results lead with "Toliau pagal planą: <next>" (`nextPlanStep`,
  `planNextButtonHTML`, `wirePlanNext`); the screen that finishes the day
  offers "🎟 Žaisti už bilietą" (`planRewardButtonHTML`). Contest-day
  "review mistakes" step ticks on the contest results page.
- **48 — mastery clock = contest pace** (`playlistMasteryMs`: 1 / 2,5 /
  5 min per 3/4/5-pt item). It was a flat 5 min (100 s per 5-pointer).
- **49 — option debris.** `_fix_option_junk.py` cleared "D) E)" & co.
  from 48 questions; smoke test guards debris and the option flags.
- **50/51 — kid solutions were wrong.** The re-spacers had mangled the
  hand-written kid texts ("Pas ir inkai"); worse, 74 of 99 kid solutions
  never reached the key and many argued for a wrong answer (written
  without the figures). All rewritten from figure + official solution
  (`_solutions_kid.py`, applied by `_apply_kid_solutions.py`); every
  one ends "Atsakymas: X) …" with X = key (smoke-checked); misconceptions
  only name a concrete slip. **Never run `_respace_words.py` /
  `_segment_words.py` on solutionKid/misconceptions** (now excluded).
  Playlists now show solutionKid + "Tavo klaida" too (they showed only
  the official text before).
- **Archive errors fixed:** 2021-10 (held Q29's text), 2021-29 options,
  2024-23 key → B, 2024-24 key → A (`_fix_misfiled_2021_2024.py`); wrong
  figures on 2010-8, 2012-13, 2019-11, 2023-9, 2022-25, 2023-23
  (`_refigure_misfits.py`) and 2021-29/30 (split). Smoke test fails on
  byte-identical figures. PyMuPDF is installed for the user: run figure
  scripts with plain `python`, not `python -I`.
- **52 — official solution beats AI text**; AI is asked only when no human
  solution exists; no AI "your mistake" for picture options.
- **53 — contest mistakes auto-queue** (`queueContestWrongs`: ≤ 3 per
  paper, easier bands first, 3/day, `fromContest` → warm-up only, never a
  whole review day outside the taper). 6-seed averages (`--seed=N`):
  0.8 learn 26.0, 0.85 25.3, weekend-off 18.2, erratic 12.0, 0.7 learn
  17.8 (was 20.7 – the price of reviewing 3 paper mistakes a week).
- **55 — service worker:** shell fetched with `cache: "no-cache"`; cache
  names v2. **Bump `FIGS` in sw.js whenever a figure PNG changes** –
  figures are cache-first, so a device keeps the old picture otherwise.

## Loops 56–75 (2026-10-11, ninth pass – full archive audit)

- **56 — 2024 keys.** The booklet's answer table was wrong on Q1, 2, 4,
  5, 6, 7, 8, 11 (+ 23, 24 earlier); keys follow the worked solutions.
- **57/65/70 — official solutions re-extracted** with PyMuPDF
  (`_reextract_solutions.py`): real word spacing, segmentation by the
  booklets' own headers, "Žr. Mažylio N" pointers resolved, figure labels
  dropped from the value line, stacked fractions as a/b (`_pagetext.py`,
  2000–05 and 2018–25 only). 2014–17 solutions come from `Solutions/`.
- **58 — point bands by number** (269 questions moved; 2000–12 were all 3).
- **59 — 10 keys fixed / filled** after an audit of all 777 questions by
  7 agents + a hand check of each dispute (`_fix_keys_audit.py`).
- **60 — 601 prompts, 174 option sets** transcribed from the figures
  (`_audit_text.json`, `_apply_audit_text.py`).
- **61/62 — `_recrop.py`**: layout-based crops (a drawing belongs to the
  question whose band holds its centre); 58 flagged figures re-cut and
  checked by eye; 4 missing questions added. sw.js FIGS v4.
- **63 — labelled official solutions** (`parseOfficialSolution`,
  `solutionBlockHTML`): "Atsakymas", "Greitas būdas", "Sprendimas",
  "Kitas sprendimas" instead of raw ?/!/!! markers.
- **66 — 271 kid solutions** (152 new 5-pointers + 20 unsolved 3/4-pt),
  357 misconception notes, 67 trick tags corrected (`_mechanic_review.py`).
- **67 — simulator seeds the app's Math.random** too: runs reproduce.
- **69 — `RELATED_MECHANIC`** so a trick with a single 5-pointer still
  routes to band-matched practice (0 dead ends of 250).
- **71/72 — `reconcileMasteryWithArchive`** on load: full mastery earned
  below the new top band becomes partial; due items take the new band.
- **64/73** smoke guards (Q1–30, bands, keys, split words, routes,
  solution parsing) and a style pass over the agent texts.

Simulation after this pass (84 d, 6 seeds, mastered of 26 track tricks):
0.8 learn 22.8 · 0.85 flat 23.8 · 0.7 learn 16.0 · weekend-off 0.8 learn
17.8 · erratic 0.7 learn miss 30 % 9.2. Same seeds on the pre-audit
archive: 25.7 / 25.2 / – / 20.5 – the drop is the real 5-point checks
that many tricks gained, not a regression.

## Loops 76–95 (2026-10-11, tenth pass)

- **76/80 — figures.** Edge sweep (dark pixels on the top/bottom row): 38
  re-cut by `_recrop.py`, which now snaps to whole text lines and its own
  drawings. `_trim_figures.py` removed blank strips from 380 figures
  (2000-30 was 811 of 890 px white). Smoke test checks every figure's
  file and size. sw.js FIGS v6.
- **77/82/83/86 — official texts.** Agents repaired 154 official
  solutions that the kid actually sees (label runs, fractions, powers,
  split words; part markers kept) → `_clean_solutions.json`; booklet
  typos patched; a frequency scan fixed 19 spelling slips
  (`_fix_typos_2026.py`).
- **81 — parser:** a ?/! inside a sentence ("kaip radome ! dalyje") is a
  reference, not a new part.
- **84 — the official solution stays one tap away** under a kid solution
  ("yra greitas būdas" when it has one).
- **87 — `_rebuild_data.py`** reruns the whole text layer from the PDFs;
  verified to reproduce the committed archive.
- **78 — practice papers newest first** among the least-practised ones
  (2022, 2018, 2015 … rather than 2000, 2001 …).
- **79 — recognition drill** leaves out catch-all tags.
- **88/89 — hints:** the last tier is the question's own "Gudrybė:"
  sentence (withheld when it names the answer); playlist hints no longer
  start from the official computation.
- **91 — 2006 (Mažylis) is not served** (`OUT_OF_SCOPE_YEARS`).
- **92 — related-trick practice is labelled as such.**
- **93 — the archive card hides the trick name** on 4/5-pointers until an
  answer or a hint.
- **85/90/94 — browser passes** at 360 px: no overflow, no errors.

Simulation (84 d, 6 seeds, mastered of 26): 0.8 learn 25.2 · 0.85 flat
23.7 · 0.7 learn 15.2 · weekend-off 0.8 learn 17.8 · erratic 9.3.

## Loops 96–145 (2026-10-11, eleventh pass)

- **Kid solutions for every question (105/123):** agents wrote the 242
  four-pointers and 237 three-pointers from the figures; with the earlier
  ones `_solutions_kid.py` (renamed from `_solutions_5pt_kid.py`) holds
  750 solutions + 854 misconception notes; `_mechanic_review.py` holds 256
  trick-tag corrections. One more booklet key error: **2002-10 → B** (0
  may be a middle digit: 987 − 102 = 885).
- **Contest simulator:** flag a doubtful question (🚩), withdraw an answer
  (tap again), keyboard A–E / 1–5 / ←→, figures prefetched before the
  clock starts; parent view can cache all figures for offline use.
- **Paper practice (111/112/126):** `openPrintPaper` prints a paper (key on
  a print-only page), `openPaperEntry` grades the answer sheet; 📄 in the
  history; offered from the contest card and the contest intro.
- **Mistakes notebook (104/106/107/108/115):** `store.mistakes` via
  `noteMistake` (practice + papers); "📒 Klaidos" view, badges 🩹/🛠,
  parent card, contest-results link, weekly recap line.
- **Hints & drill:** recognition drill shows the problem's own Gudrybė;
  parent view breaks papers down by band.
- **Plan:** review cores at most every other day before the taper (100).
- **Text style:** decimal comma in scores and generated answers
  (`fmtPts`, `makeMC`), "20 %", "cm²"; answer values never glued to a
  header letter; control characters stripped.
- **Smoke guards added:** kid answer line = option text, text hygiene,
  decimal comma in generators, source files free of control characters
  (a shell-mangled `\b` is a literal backspace!), undefined/NaN leaks in
  every main view, contest flag/finish, paper print/entry, notebook,
  parent view with history.
- **Later in the pass (128–142):** each paper mistake and each 2+-mistake
  trick group links to its playlist; the paper picker marks ✓ done / 🔒
  held back; archive cards show "📒 kartoji ×N"; mistakes worksheet print
  (notebook + parent card); `topUpQueueFromNotebook` feeds ≤ 2 old open
  mistakes a day into the warm-up review; 📄 badge; "Kaip naudotis" for
  parents; long words wrap (`overflow-wrap:anywhere`, `hyphens:auto`).

Final check of this pass: `_rebuild_data.py` reproduces the archive;
simulation (84 d, 6 seeds, of 28 track tricks): 0.8 learn 25.0 · 0.85
22.3 · 0.7 learn 14.0 · weekend-off 17.3 · erratic 10.0.

## Loops 146–195 (2026-10-11, twelfth pass)

- **Time on practice papers (146/149/150/151/159):** `creditContestTime`
  records time per question (saved with progress); results show
  "⏱ Kur dingo laikas" per block against 1 / 2,5 / 3,5 min per question
  and the slowest three; quiet pace checkpoints at 15 min (3 t.) and
  40 min (4 t.); the one pace plan (15 / 40 min) is the same in the
  intro, the strategy card and the checkpoints.
- **Strategy notes (147):** rule-based tips after each paper (skipped
  3-pointers, low-accuracy guessing vs the −¼ penalty, too timid, slow
  first block).
- **Recognition drill (148/152/153):** seconds per answer; the most
  frequent trick mix-up (`store.recogConfusion`) with the trick's
  one-line recognition tip; top mix-ups in the parent view.
- **Real 3-point sprint (155):** `openArchiveSprint` – 10 archive
  3-pointers on the contest clock; the plan alternates it with the
  generated sprint.
- **Self-explanation (156/157/160):** "Kodėl, manai, suklydai?" chips
  (`MISTAKE_REASONS`) after wrong answers in archive cards, playlists and
  paper results; stored on the notebook entry; parent view shows the
  distribution with a tip.
- **Contest-day checklist (158)** in the strategy card.
- **Independent review (162):** five reviewer agents re-checked all 750
  kid solutions against the figures: 39 fixed (wrong picture
  descriptions, example arithmetic, incomplete arguments, hints that gave
  the answer away, notes whose slip doesn't produce the option). A second
  pass with a reshuffled split followed (see the next entry / git log).
- **AI only as a fallback (175/176):** with a reviewed kid solution behind
  every question, no AI "Tavo klaida" note and no AI hint tiers are
  requested; the hand-written ladder + the question's Gudrybė are used.
- **Cards:** the old keyword pills are gone (177); "📒 kartoji ×N" (132);
  archive years show "· N/30" done and "Tęsti nuo N" (163/164).
- **Figures (178):** `_recrop.py` paints out other questions' words and
  stray drawings inside a crop (own labels stay); 51 PNGs regenerated;
  FIGS v7.
- **Home order (171/172):** mission → plan → track → paper → tricks →
  weak spots → archive → generated test.
- **More:** strategy/time sections on paper results, paper-to-paper delta
  (185), flag count in the contest header (180), post-contest "Kaip
  sekėsi?" card with the real score (168), contest-day message (169),
  repeated-mistake toast (181), printable parent report (183), export
  file names per child (184), reduce-motion (179), focus rings (167),
  corrupt saves kept aside (186). Store size after 120 simulated days:
  ~50 KB.
- **Second independent review (192):** reshuffled split, 25 more fixes
  (unproved steps argued, wrong figure facts, an answer-giving hint,
  misconception notes); two official typos (2016-15, 2014-9). Both
  reviews: 64 fixes in 750 solutions, no answer key in doubt.
- **Paper results (185–191):** delta to the previous paper, the first
  paper framed as the starting point, time per wrong answer, a "stuck
  6+ min" strategy note; notebook rows show the kid's reason.
- **Final check (193):** `_rebuild_data.py` reproduces the archive, smoke
  green, no LF-only lines; simulation (84 d, 6 seeds, of 28): 0.8 learn
  25,0 · 0.85 22,3 · 0.7 learn 14,0 · weekend-off 17,3.

## Loops 196–245 (2026-10-11, thirteenth pass)

- **Three review agents** (logic bugs, Lithuanian wording, archive text)
  and one **visual audit of all 751 figures** drove most of this pass.
- **Bugs fixed (203–210):** a mastery check counted letters that were
  tapped but never sent (a timed-out set could pass); leaving a passed
  check by the top button lost the mastery (`finalizePlaylist` is now
  idempotent and runs from `exitHome`); sprint/mixed sets ticked the plan
  with nothing answered; the worked example (solution on screen) paid
  stars and stats; grading a paper inherited an online run's times and
  deleted an unfinished online contest; "Praleisti" with all answered
  submitted the paper; a repeated mistake never asked "why?" again; game
  tickets were spent on opening the picker; one unlock gave endless
  replays (now `GAME_RUNS_PER_UNLOCK` = 3); minute stars on an idle open
  page (`STAR_IDLE_MS`); reset kept keys without defaults; UTC day parity
  (`localDayNum()`, calendar-day `dateKeyOffset`).
- **Contest simulator:** ✕ crosses an option out (198, saved with the
  run); `contestElimination` → strategy note on informed guesses (201);
  **"🔁 Antras bandymas"** (216) – the paper's wrong + skipped questions
  again without the clock before reading solutions; `contest.retry` =
  points lost to time and haste, shown on results, in the parent view
  (average, 237), and it ticks the contest day's review step (219); a
  slow 3-point block on a recent paper triggers speed work (238); the
  real 3-point sprint is stored as a session (239).
- **Reading:** kid solutions render as 💡 trick line / short paragraphs /
  ✅ answer line (`kidSolutionHTML`, 226); tap a picture to enlarge it
  (`wireFigureZoom`, 222).
- **Plan:** one-tap suggested contest date, the third Thursday of March
  (`suggestedContestDate`, 221).
- **Wording (199/200/217/236):** numeral agreement, "uždavinys" (not
  "užduotis"), "sugaišai" for time (praleisti = skip), "gudrybė" (not
  "tipas"), parent view consistently "jūs".
- **Archive text (211–213):** `_fix_typos_2026.py` now also strips
  booklet page headers, figure-label runs after the answer sentence,
  "◦" → "°", "cm 2" → "cm²", unit spacing, "––"; smoke guard.
- **Figures (196, 214–215, 228–234):** `_recrop.py` gained section-heading
  and copyright-footer stops, never paints over the question's own words,
  paints out foreign text lines (≥ 3 words), `FORCE_MASK`, `EXTRA_MASK`,
  `MANUAL` crops with masks and `FIG_SOURCE` (2007 comes from the
  compendium). ~140 figures re-cut and compared side by side (old | new
  contact sheets) before adoption; 2024-20 shows all 4 rows again, 2003-5
  /2019-12/2003-19 hold one question each. FIGS v17. Smoke: no orphan PNGs.
- **Simulator:** `--start`, `--stop`, `--dump=<file>` (import-shaped store
  for browser checks; `_sim_store.json` is git-ignored).
- **Pitfalls:** in this Git Bash, `sed -i` turns CRLF files into LF and
  heredoc Python halves backslashes ("\1" → chr(1)) – edit via Python with
  newline='' and build backslashes with chr(92).
- **Final check:** `_rebuild_data.py` reproduces the archive; smoke green;
  simulation (84 d, 6 seeds, of 28): 0.8 learn 24,7 · 0.85 22,0 ·
  0.7 learn 14,7 · weekend-off 17,0 · erratic 9,8.

## Home tabs (2026-10-12)

The home page had grown to 14 stacked cards. It is now five tabs with a
bottom tab bar (`HOME_TABS`, `setHomeTab`, `state.homeTab`; every start
opens on "today"): **Šiandien** (mission, plan, recap, post-contest),
**Gudrybės** (track, weak spots, full trick list collapsed),
**Konkursas** (papers, strategy, paper print), **Uždaviniai** (archive
years, generated test, last test), **Prizai** (race/shop/badges,
settings, about/reset). A one-line status strip (streak, stars, 📒, 👁)
sits above every tab. All panes are rendered and only `[hidden]` is
toggled, so wiring and smoke checks see the whole page; a re-render keeps
the tab. Dots on tabs: undone plan steps, unfinished paper, game tickets.

## UX pass for the child and the parent (2026-10-17, 50 loops)

Started from two complaints: the review intro listed the spaced-repetition
intervals ("1 d. → 3 d. → …") and every archive card printed the prompt
above a figure that already shows the same text.

- **Figure first** (`questionBodyHTML`): every archive figure is the question
  as printed (text + drawing + options), so the typed prompt now sits behind
  an "Aa Rodyti tekstą" `<details>` under the figure. Closed by default on
  wide screens, open on phones (< 600 px) where the print is too small;
  an explicit tap is remembered in `store.settings.showQText` (null = no
  choice yet) and applied to every card on the page (`wireQTextToggle`).
  Browsers fire one `toggle` for a `<details open>` right after parsing –
  `data-auto` marks those so they are not taken for the kid's choice.
  Used by archive cards, playlists, the contest, the recognition drill
  and the race gate. A "🔍 paspausk, kad padidintum" hint shows on phones.
- **Picture-only options** render as five letter circles in playlists too
  (`.opt-letter-only`, `.options.image-options`); the contest shows
  "– atsakymas paveikslėlyje –" instead of empty bars.
- **Kid wording**: "Pakartojimas" instead of "Pakartojimo eilė"; no
  intervals; review cards say why the question is back ("praeitą kartą
  suklydai" / "jau N kartus iš eilės teisingai" / "buvai tikras, bet
  suklydai") and, after the answer, when it returns ("Sugrįš po 7 d." /
  "Pakartosime rytoj"). Card headers are "N uždavinys · YYYY m."
  everywhere (no "Klausimas N", no "2024 · K16"); mastery-step
  instructions became a pill row. Plan steps say "uždaviniai".
  Streak and star counters on the hero are tappable (toast explains them –
  phones have no hover). Archive years have a "Tik neišspręsti (N)" filter.
- **Activity log** gained `activity[day].sec` (active seconds, from the
  star heartbeat – only in `STAR_TIME_VIEWS`, idle cut-off) and
  `activity[day].byBand = {3:{a,ok},…}` (from `logActivity` and
  `creditContestActivity`).
- **Parent view rebuilt** (`renderParent`): this week's tiles (training
  days, questions + accuracy with week-over-week delta, minutes, stars vs
  goal) → "Ką verta daryti" (`parentAdvice`, ≤ 3 rule-based tips with
  buttons) → settings (contest date via shared `applyContestDate`,
  contest weekday, training days, weekly goal + prize, confidence /
  penalty / sound toggles, parent code) → progress (mastery bar, accuracy
  by block over 30 days, 4-week table, 14-day grid, 7-day table,
  per-mechanic table) → papers, weak tricks, notebook, calibration,
  recognition, profiles, how-to, backup. "📋 Santrauka" copies a
  plain-text week summary (`parentSummaryText`) for a message to the
  other parent or a teacher. Settings and buttons are hidden in print.
- **Parent code**: `META.parentPin` (shared by all profiles; 4–6 digits)
  gates the parent view (`renderParentGate`, view "parentGate"); the
  gate still offers export, so recovery = export → clear site data →
  import. The hero button shows 🔒 when a code is set.
- Smoke test covers all of it (section "figure-first question body +
  parent view", "archive filter + parent summary"). Phone check: a 360 px
  iframe harness (`scrollWidth` per view) – no overflow on any view.

## Kids' UX + learning-methods pass (2026-10-17, 50 loops)

Driven by a research sweep (NN/g children's usability, Beast Academy, Duolingo,
Zearn, Khan, Alcumus; Mueller & Dweck on praise, Deci et al. on rewards,
productive failure, worked-example fading, self-explanation, hypercorrection)
mapped onto a code + 375 px numeric audit of every view.

- **Reading & touch.** Text floor 13 px (help lines, pills, labels), options
  ≥ 48 px, `.btn` ≥ 44 px, `.btn.small` ≥ 40 px, track nodes 40 px, contest
  pips 36 px, text toggle 36 px; phones get 15–16 px reading text. The tab
  bar's `font:600 11px/1.1 inherit` was an invalid shorthand (labels fell back
  to 13.3 px) – now longhand.
- **Phone back button** (`hookViewNavigation`): `state.view` is an accessor.
  A view change scrolls to the top; a non-home view holds one history entry,
  and `popstate` closes an open picture or clicks the view's own exit button
  (`.nav-back`, else `NAV_EXIT_IDS`), so cleanup runs as on a tap. A running
  contest just goes home (it stays resumable). Back on home is ignored once.
- **One question at a time** for archive years (default; "☰ Visi sąraše"
  toggles `store.settings.archiveList`). All 30 cards are still rendered,
  29 with `[hidden]` (smoke checks and wiring see every card). Number strip
  coloured by result, sticky prev / N of 30 / next bar, ← → / A–E / 1–5 /
  Enter keys, horizontal swipe, `state.archiveFocus[year]`. Phone page went
  from ~18 000 px to ~1 400 px. On phones the strip is one scrollable row
  (`centerStripPip`, also in the contest). A whole answered paper ends with
  a per-block summary card.
- **Time vs budget**: `shownAt` → `tookSec` on the card ("⏱ Sprendei 2:40 ·
  konkurse 5 t. uždaviniui verta skirti iki ~5 min", + "verta praleisti" when
  > 1,5 × `PACE_SEC`).
- **Verdict first**: in playlists the verdict box now sits right under the
  options (before the slip note, "why?" chips and the solution) and is
  scrolled into view; mastery/mixed/due sets have a progress bar and a
  "Kitas uždavinys ↓" jump.
- **Second try** (archive cards + playlist try step): the first miss is
  recorded as a miss (stats, notebook, queue unchanged) but the solution
  waits – the option is struck out, the misconception note for that letter
  and (if "Tikrai žinau") a confident-wrong line are shown, then "Pabandyk
  dar kartą" or "Rodyti sprendimą". `store.secondTry = {a, ok}` (a reveal
  counts as not self-fixed) → parent card "Kaip vaikas taiso klaidas".
- **Try first** (`TRY_FIRST_SEC` 45 s / 90 s for 4/5-pt, focus mode only): an
  early first hint tap shows three self-questions; the next tap gives the
  hint. Friction, never a lock.
- **Worked-example fading**: `kidSolutionHTML(t, {fade:true})` hides the
  answer line and, with ≥ 2 steps, the last step; the playlist's worked step
  shows it above the options ("Paskutinį žingsnį užbaik pats"). Smoke checks
  that no faded text of the 750 kid solutions contains "Atsakymas:".
- **Self-explanation after a right answer** (`selfExplainFor`): on ~half of
  the right first-try 4/5-pointers (stable per question by `keyHash`) the
  kid picks the idea that solved it – own "Gudrybė:" line vs one from a
  different trick; the solution waits until picked or "Praleisti".
  `store.selfExplain = {a, ok}` in the parent view.
- **Wording**: process praise, no ability praise or "Šaunu!"; "✓ Teisingai."
  / "Ne šis atsakymas." / "✓ Teisingai – iš antro karto."; outdated "Apie"
  text rewritten.
- **Motivation hygiene**: one quiet break nudge after 30 active minutes a day
  (`BREAK_NUDGE_SEC`, never in a contest/quiz); parent prize help text frames
  the prize as a celebration of effort (overjustification) and asks for
  process praise; the today tab has one primary action; first run opens the
  newest practice paper at Q1 in focus mode instead of a generated quiz.
- **Browser testing tip**: `_phone.html` (git-ignored) is a 375 px iframe
  harness on `python -m http.server`. The app saves on unload – set
  `_storeFrozen = true` in the frame before clearing or restoring
  localStorage, or the reload writes the old in-memory store back.

## Second kids' pass: a11y, flows, learning methods (2026-10-17, loops 51–150)

Four reviews (practice flows; home/contest/games; accessibility; research on
methods the app lacked) drove 100 loops, then an independent diff review.

- **Accessibility (51–66).** Tokens darkened for 4.5:1 text (`--accent`
  #b83a12, `--good` #16703f, `--muted` #5f5f66) plus `--line-strong` for the
  borders of things you tap. Selected options: 2 px border, filled letter,
  `aria-pressed` on every option. Verdicts are `role="status"`, focused after
  a check; toasts are a polite live region above the tab bar and never block
  taps; the mastery countdown speaks only at the last minute. JS scrolling
  goes through `smoothScroll()` (reduced motion). Keyboard figure zoom with
  focus in/out, badges are buttons that toast how they are earned, home tabs
  use `aria-current` (no half tab pattern), 40–44 px pips/summaries/checkbox
  rows/inputs, print keeps colours.
- **Practice flows (67–86).** Timed checks (mastery, 3-pt sprint) and mixed
  sets show only the verdict until the set ends (`holdFeedback` – one trick's
  first solution would give the rest away; delayed feedback in mixed sets).
  Sets run one question at a time like the archive (`playlistFocusKey`,
  number strip, `plPrevQ/plNextQ`, `plFocus`); keys in sets and the drill
  (`wirePracticeKeys`). Next items call `toTop()`. `askConfidenceNow` is
  scoped to the sprint's own view. The try step has try-first, a two-rung
  hint ladder (notice → this problem's idea) and one spare try
  (`content.extraTry`) after a miss. Notebook: "Spręsti klaidas" set
  (`openMistakeSet`, `playlistFromBook` → every back returns to the
  notebook) and "Bandyti" lands on the exact card. Mixed sets ask
  "Kokia gudrybė?" (optional, logged like the drill). Quiz results lead with
  the next step; the generated sprint has a skip and no hints.
- **Home/contest/games (87–106).** `liveStreak()` (shared `streakGap`) shows
  0 for a broken run. Game challenge: `GATE_TRIES_PER_DAY` = 3, counted when
  a try starts. One name: "Žaidimų iššūkis/bilietas", "pasiekimas". Contest:
  one forward button (next unanswered), finish primary only when all are
  answered; second attempt above the solutions, which stay folded until it
  is done (`_showContestSolutions`). Plan view: today's steps first,
  settings in a fold, read-only behind the parent code (reset too). Contest
  tab: one recommended paper. Recap counts planned training days. The day
  bonus ticks hand-ticked steps – except a paper day's review step.
- **Learning methods (107–120).** Thinking drill (`openThinkDrill`):
  "Kur suklydo …?" – match a classmate's wrong letter to the slip note that
  produces it (questions with ≥ 2 notes) – and "Sudėliok sprendimą" – tap the
  kid solution's steps (`kidSolutionParts`) in order. Trick cards
  (`openRecallCards`) for recall from memory, rated, streak only. Playlist
  step 0 first shows the try problem ("pusė minutės", `playlistPeeked` = its
  key). "Palygink abu kelius" under official quick ways. Contest intro:
  optional worry note (never saved) + reappraisal line. Kid's week goal as an
  if–then plan (`store.ifThen`, today tab, contest intro, parent view).
  Parent "🍽 Šiandien paklauskite" (`parentAskToday`): an unseen 3/4-pt
  question on a trick met today. A "check it back" line before checking a
  5-pointer. ✏️ pen on every figure (`wireSketch`; pads restore after a
  re-render, cleared when a paper starts).
- **Checks.** Smoke section "second kids' pass"; two 375 px browser passes
  (no overflow, leaks or console errors); simulator (84 d, 6 seeds, of 28):
  0.8 learn 24,0 · 0.85 23,7 · 0.7 learn 14,5 · weekend-off 16,3 ·
  erratic 9,7. Dark mode is still open: ~54 literal colours and 322 inline
  styles need tokens first.
- **Editing tip.** In this Git Bash, heredoc Python mangles non-ASCII and
  backslashes; write edit scripts with the Write tool and apply them
  (old/new pairs, each must match exactly once).
