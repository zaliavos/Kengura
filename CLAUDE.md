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
- 2010, 2011, 2012, 2016 have 29 questions instead of 30.
- Contest-sim eligibility (kengura.html ~line 3115): year passes only if
  every Q has a `correct` letter AND year is not 2006. Reason 2006 is
  excluded: the 2006 source PDF is **Mažylis (3-4 grade), not Bičiulis**
  — every Q is 3-point, so a kid scoring 30/30 on it would walk away
  with a false sense of contest readiness. With these gates: **23 of 26
  years surface** (excluded: 2000, 2001, 2006).
- Four 2000/2001 answer keys (2000-Q8/15/24, 2001-Q10) are intentionally
  `correct: null`. These were hand-guessed at ~60-70 % confidence on
  2026-05-08; until a Mažylis-section solution PDF for 2000/2001 is
  located (or a math teacher verifies), the keys stay null. With one or
  more unkeyed Qs, those years can't be graded fairly in contest mode.
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
`_solutions_5pt_kid.py`, applied via `_apply_kid_solutions.py`.

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

**D. Kid-Lithuanian solutions for all 99 5-pointers.** `q.solutionKid` is
shown in place of the auto-extracted official `q.solution` when present.
Style: 3 short paragraphs (pastebėjimas → veiksmas → patvirtinimas) in
2nd person voice. Data in `_solutions_5pt_kid.py`.

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
- `*.pdf` — source materials. `200xLT.pdf` and `TMK0x_lietuviu.pdf` are
  test booklets; `200xspB.pdf` and `200xkengura.pdf` are solution
  compendiums; `benjamin_lt (*).pdf` are the modern (2013+) test booklets.
