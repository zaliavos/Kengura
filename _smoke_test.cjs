/* _smoke_test.cjs — Node smoke test for kengura.html.
 *
 * Loads the inline app script with a stubbed DOM and checks:
 *   1. every generator produces a valid question across many seeds
 *      (unique options, valid correctIndex, no "undefined"/"NaN" leaks)
 *   2. stackProjection answers are the verified minimums (9 / 7 / 6)
 *   3. aiBuildOpts works against real archive questions (options are an
 *      object keyed by letter — this crashed once already)
 *   4. pickPracticeFor never routes a 5-point source to an easier generator
 *   5. generateQuiz fills the requested count even for a narrow
 *      difficulty selection (e.g. 30 questions, 5-point only)
 *   6. kid-facing mechanic hints contain no banned notation
 *      (factorials, mod-N, systems of equations, coordinate flips)
 *
 * Run:  node _smoke_test.cjs
 */
"use strict";
const fs = require("fs");
const path = require("path");

let failures = 0;
function check(name, cond, detail){
  if(cond){ return; }
  failures++;
  console.error(`FAIL  ${name}${detail ? " — " + detail : ""}`);
}
function section(name){ console.log(`\n== ${name} ==`); }

// ---------- minimal DOM stubs ----------
// A 2D context that accepts any property and swallows any call, so the
// canvas games can run their loops headlessly.
const noopCtx = new Proxy({}, { get(){ return ()=>{}; }, set(){ return true; } });
// requestAnimationFrame stub: callbacks queue up and the test drives frames.
const rafQueue = [];
function runFrames(n){ for(let i = 0; i < n; i++){ const cbs = rafQueue.splice(0); if(!cbs.length) return i; for(const cb of cbs) cb(performance.now()); } return n; }
function stubEl(){
  return {
    innerHTML: "", textContent: "", style: {cssText: ""}, dataset: {},
    className: "", disabled: false,
    addEventListener(){}, removeEventListener(){},
    querySelector(){ return null; }, querySelectorAll(){ return []; },
    appendChild(){}, remove(){}, setAttribute(){},
    classList: {add(){}, remove(){}},
    getContext(){ return noopCtx; }, getBoundingClientRect(){ return {left:0, width:0}; },
    scrollIntoView(){},
  };
}
const documentStub = {
  getElementById(){ return stubEl(); },
  createElement(){ return stubEl(); },
  querySelector(){ return null; },
  querySelectorAll(){ return []; },
  addEventListener(){}, removeEventListener(){},
  body: {appendChild(){}},
  hidden: true,
};
const windowStub = { addEventListener(){}, removeEventListener(){} };
const localStorageStub = {
  _m: new Map(),
  getItem(k){ return this._m.has(k) ? this._m.get(k) : null; },
  setItem(k, v){ this._m.set(k, String(v)); },
  removeItem(k){ this._m.delete(k); },
};

// ---------- load archive ----------
const archiveSrc = fs.readFileSync(path.join(__dirname, "kengura-archive.js"), "utf8");
new Function("window", archiveSrc)(windowStub);
check("archive loads", windowStub.KENGURA_ARCHIVE && Array.isArray(windowStub.KENGURA_ARCHIVE.archive));

// ---------- extract + run the app script ----------
const html = fs.readFileSync(path.join(__dirname, "kengura.html"), "utf8");
const m = html.match(/<script>\s*("use strict";[\s\S]*?)<\/script>\s*<\/body>/);
if(!m){ console.error("FAIL  could not extract inline script from kengura.html"); process.exit(1); }

const EXPORTS = `
return {GENERATORS, GENERATOR_KEYS, buildQuestionFromKey, generateQuiz,
        generateKenguraQuiz, getGenDiff, ARCHIVE, aiBuildOpts,
        pickPracticeFor, findSimilarArchive, MECH_BAND_INDEX,
        MECHANIC_HINTS, MECHANIC_METHODOLOGY, MECHANIC_LABEL, GEN_MECHANIC,
        MECHANIC_ORDER, buildRecogPool, nextMechanicToLearn,
        pickPlaylistContent, planStepsForToday, daysToContest,
        SHOP_COLORS, starsAvailable, archiveQsForMech,
        openPlan, openRecogDrill, openMixedSet, openPlaylist, startSprint,
        openRaceChallenge, requestOpenContest, state, store,
        planPhase, isContestDay, pickContestYear, contestEligibleYears,
        starsForAnswer, awardStars, starsThisWeek, markPlanStepDone,
        Sfx, Fx, trackMechanics, trackCardHTML, weeklyRecapHTML,
        rewardsCardHTML, buildRacePool, masteryDecayDays, logActivity,
        reservedYears, isReservedYear, needsDiagnosticContest, findSimilarArchive,
        isContestDay, planTimelineHTML, SHOP_TICKET_COST,
        openJumpGame, openRaceGame, renderGamePick, openFreeRace, planMinutes, PLAN_STEP_MIN,
        askConfidenceNow, STAR_TIME_VIEWS, mechTargetFor, noteMechAttempt, loadStore, LS_KEY, masteredBandOf, mechTopBand, trackCardHTML, planTaperDays, weekStripHTML, openPlaylist, isTrainingDay, creditContestActivity,
        renderContestIntro, newTestSizeLabel, needsDiagnosticContest,
        nextPlanStep, renderRecogResult, $app, playlistMasteryMs};
`;
let app;
try {
  app = new Function(
    "window", "document", "localStorage", "setInterval", "clearInterval",
    "requestAnimationFrame", "cancelAnimationFrame", "confirm", "alert", "fetch",
    m[1] + EXPORTS
  )(
    windowStub, documentStub, localStorageStub,
    () => 0, () => {}, (cb) => { rafQueue.push(cb); return rafQueue.length; }, () => {}, () => false, () => {}, () => Promise.reject(new Error("no net"))
  );
} catch(e){
  console.error("FAIL  app script threw at load time:", e.message);
  process.exit(1);
}
console.log("app script loaded cleanly");

const {GENERATORS, GENERATOR_KEYS, buildQuestionFromKey, generateQuiz,
       getGenDiff, ARCHIVE, aiBuildOpts, pickPracticeFor,
       MECHANIC_HINTS, MECHANIC_METHODOLOGY} = app;

// ---------- 1. generator sanity across seeds ----------
section("generators");
const SEEDS = 80;
for(const key of GENERATOR_KEYS){
  for(let seed = 1; seed <= SEEDS; seed++){
    let q;
    try { q = buildQuestionFromKey(key, seed); }
    catch(e){ check(`${key} seed ${seed}`, false, "threw: " + e.message); continue; }
    const opts = q.options || [];
    check(`${key}#${seed} has ≥3 options`, opts.length >= 3, `got ${opts.length}`);
    check(`${key}#${seed} correctIndex valid`,
      Number.isInteger(q.correctIndex) && q.correctIndex >= 0 && q.correctIndex < opts.length,
      `correctIndex=${q.correctIndex}, options=${opts.length}`);
    const uniq = new Set(opts.map(String));
    check(`${key}#${seed} options unique`, uniq.size === opts.length,
      `${opts.length} options, ${uniq.size} unique: ${JSON.stringify(opts).slice(0,120)}`);
    for(const field of ["prompt", "explain"]){
      const s = String(q[field] || "");
      check(`${key}#${seed} ${field} clean`, s.length > 0 && !/undefined|NaN/.test(s),
        s.slice(0, 100));
    }
    if(!q.imageOptions){
      check(`${key}#${seed} options clean`, !opts.some(o => /undefined|NaN/.test(String(o))),
        JSON.stringify(opts).slice(0, 120));
    }
  }
}
console.log(`checked ${GENERATOR_KEYS.length} generators × ${SEEDS} seeds`);

// ---------- 2. stackProjection verified answers ----------
section("stackProjection answers");
const allowed = new Set(["9", "7", "6"]);
for(let seed = 1; seed <= 200; seed++){
  const q = buildQuestionFromKey("stackProjection", seed);
  const ans = String(q.options[q.correctIndex]);
  check(`stackProjection#${seed} answer ∈ {9,7,6}`, allowed.has(ans), `got ${ans}`);
}

// ---------- 3. archive shape + aiBuildOpts ----------
section("archive + aiBuildOpts");
let archiveQs = 0;
for(const t of ARCHIVE){
  for(const q of t.questions){
    archiveQs++;
    check(`${t.year}-q${q.num} options is object`,
      q.options && typeof q.options === "object" && !Array.isArray(q.options));
    check(`${t.year}-q${q.num} correct valid`,
      q.correct == null || "ABCDE".includes(q.correct), String(q.correct));
    try {
      const o = aiBuildOpts(t.year, q, "hint", {tier: 1});
      check(`${t.year}-q${q.num} aiBuildOpts options`,
        Array.isArray(o.options) && o.options.length === 5 && o.options.every(x => typeof x === "string"));
    } catch(e){
      check(`${t.year}-q${q.num} aiBuildOpts`, false, "threw: " + e.message);
    }
  }
}
console.log(`checked ${archiveQs} archive questions`);

// ---------- 4. practice routing never downgrades a 5-pt source ----------
section("pickPracticeFor band routing");
let routed = 0;
for(const t of ARCHIVE){
  for(const q of t.questions){
    let p;
    try { p = pickPracticeFor(q, t.year); }
    catch(e){ check(`route ${t.year}-q${q.num}`, false, "threw: " + e.message); continue; }
    routed++;
    const band = q.points || 3;
    if(p.kind === "generator" || p.kind === "fallback"){
      const genDiff = getGenDiff(p.gen);
      if(band === 5){
        check(`route ${t.year}-q${q.num} (5pt) not downgraded`, genDiff === 5,
          `${p.kind} → ${p.gen} (diff ${genDiff})`);
      }
      if(band === 4){
        check(`route ${t.year}-q${q.num} (4pt) not downgraded`, genDiff >= 4,
          `${p.kind} → ${p.gen} (diff ${genDiff})`);
      }
    }
    if(p.kind === "archive"){
      for(const it of p.items){
        check(`route ${t.year}-q${q.num} archive same band`, (it.q.points || 3) === band);
      }
    }
  }
}
console.log(`routed ${routed} questions`);

// ---------- 5. generateQuiz fills narrow difficulty selections ----------
section("generateQuiz counts");
for(const diffs of [[3], [4], [5], [3,4,5], [4,5]]){
  for(const count of [10, 15, 30]){
    const qs = generateQuiz(count, diffs);
    check(`generateQuiz(${count}, [${diffs}]) fills`, qs.length === count,
      `got ${qs.length}`);
    check(`generateQuiz(${count}, [${diffs}]) difficulties`,
      qs.every(q => diffs.includes(q.difficulty)),
      `bands present: ${[...new Set(qs.map(q => q.difficulty))]}`);
  }
}

// ---------- 6. no banned notation in kid-facing copy ----------
section("kid copy (no algebra/factorial/mod)");
const BANNED = [/faktorial/i, /\bmod\b/i, /lygčių sistem/i, /x\s*→\s*[−-]x/i, /\d+00a\s*\+/];
function scanCopy(objName, obj){
  for(const [mech, entry] of Object.entries(obj)){
    for(const [field, text] of Object.entries(entry)){
      if(typeof text !== "string") continue;
      for(const re of BANNED){
        check(`${objName}.${mech}.${field}`, !re.test(text), `matches ${re}: "${text.slice(0,80)}"`);
      }
    }
  }
}
scanCopy("MECHANIC_HINTS", MECHANIC_HINTS);
scanCopy("MECHANIC_METHODOLOGY", MECHANIC_METHODOLOGY);

// ---------- 7. course layer: track, recog drill, plan, adaptive playlist ----------
section("course layer");
{
  const {MECHANIC_ORDER, buildRecogPool, nextMechanicToLearn,
         pickPlaylistContent, planStepsForToday, SHOP_COLORS} = app;
  // The learning track must cover exactly the mechanics that have methodology
  const orderSet = new Set(MECHANIC_ORDER);
  const methoSet = new Set(Object.keys(app.MECHANIC_METHODOLOGY));
  check("MECHANIC_ORDER has no duplicates", orderSet.size === MECHANIC_ORDER.length);
  for(const m of methoSet) check(`track covers ${m}`, orderSet.has(m));
  for(const m of orderSet) check(`track entry ${m} has methodology`, methoSet.has(m));
  for(const m of orderSet) check(`track entry ${m} has label`, !!app.MECHANIC_LABEL[m]);

  const recogPool = buildRecogPool();
  check("recog pool ≥ 10", recogPool.length >= 10, `got ${recogPool.length}`);
  check("recog pool all labeled", recogPool.every(x => app.MECHANIC_LABEL[x.q.mechanic]));

  const next = nextMechanicToLearn();
  check("nextMechanicToLearn returns a track mechanic", next && orderSet.has(next), String(next));

  // Adaptive playlist content: sourceBand honest, forcedBand honored
  for(const m of ["truth-tellers", "invariant", "area-decomp", "cube-color"]){
    const c = pickPlaylistContent(m);
    check(`playlist(${m}) has mastery Qs`, (c.mastery || []).length >= 1);
    check(`playlist(${m}) sourceBand available`, c.bandsAvailable.includes(c.sourceBand),
      `source ${c.sourceBand}, available ${c.bandsAvailable}`);
    for(const b of c.bandsAvailable){
      const f = pickPlaylistContent(m, b);
      check(`playlist(${m}, band ${b}) honors forcedBand`, f.sourceBand === b,
        `got ${f.sourceBand}`);
    }
  }

  const steps = planStepsForToday();
  check("plan has 3 steps", steps.length === 3);
  check("plan step ids", steps.map(s=>s.id).join(",") === "warmup,core,cooldown",
    steps.map(s=>s.id).join(","));

  check("shop classic color free", SHOP_COLORS.classic && SHOP_COLORS.classic.cost === 0);
  check("stars start at 0 available", app.starsAvailable() === 0);

  check("plan CTA toggles primary/ghost", html.includes("'primary' : 'ghost'}\" id=\"planBtn\""));
  check("plan steps wrap", html.includes('cat-row plan-step'));
  check("recog options use A–D letters", html.includes("String.fromCharCode(65 + i)"));

  const savedPaper = {year:"2018", answers:{1:"A"}, current:3, startedAt:Date.now(), endsAt:Date.now()+3600000};
  app.store.contestInProgress = savedPaper;
  app.requestOpenContest("2024");
  check("declining overwrite keeps in-flight contest",
    app.store.contestInProgress === savedPaper || (app.store.contestInProgress && String(app.store.contestInProgress.year)==="2018"),
    JSON.stringify(app.store.contestInProgress && app.store.contestInProgress.year));
  app.store.contestInProgress = null;
}

// ---------- 7b. macro-cycle plan, star economy, effects ----------
section("macro-cycle + stars");
{
  const {planPhase, isContestDay, pickContestYear, contestEligibleYears,
         starsForAnswer, awardStars, starsThisWeek, markPlanStepDone,
         planStepsForToday, Sfx, Fx, trackMechanics,
         trackCardHTML, weeklyRecapHTML, rewardsCardHTML, buildRacePool,
         masteryDecayDays, store, state} = app;
  const pad = n => String(n).padStart(2, "0");
  const keyOf = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const inDays = n => { const d = new Date(); d.setDate(d.getDate() + n); return keyOf(d); };

  // Phases keyed to the contest date
  store.plan.contestDate = null;
  check("no date → build", planPhase() === "build");
  check("no date → 60-day decay", masteryDecayDays() === 60);
  store.plan.contestDate = inDays(90);
  check("90 d out → foundation", planPhase() === "foundation", planPhase());
  check("date set → 28-day decay", masteryDecayDays() === 28);
  store.plan.contestDate = inDays(30);
  check("30 d out → build", planPhase() === "build", planPhase());
  store.plan.startDate = inDays(-80);        // an 85-day run → taper = 10 days
  store.plan.contestDate = inDays(5);
  check("5 d out → taper", planPhase() === "taper", planPhase());
  store.plan.startDate = inDays(-20);        // a 25-day run → taper = 4 days
  check("short run: 5 d out is still build", planPhase() === "build", planPhase());
  store.plan.contestDate = inDays(3);
  check("short run: 3 d out is taper", planPhase() === "taper", planPhase());
  store.plan.startDate = inDays(-80);
  store.plan.contestDate = inDays(5);
  // Taper never introduces a new mechanic
  store.plan.contestWeekday = (new Date().getDay() + 1) % 7;   // not today
  {
    const steps = planStepsForToday();
    check("taper plan has 3 steps", steps.length === 3, steps.map(s=>s.act).join(","));
    check("taper core is not a new playlist", steps[1].act !== "playlist", steps[1].act);
  }
  // Contest eve = rest, contest day = none
  store.plan.contestDate = inDays(1);
  check("eve: strategy step", planStepsForToday().some(s => s.act === "strategy"));
  store.plan.contestDate = inDays(0);
  check("contest day: single none step", planStepsForToday().length === 1 && planStepsForToday()[0].act === "none");
  // Weekly contest day → contest core with a pickable year
  store.plan.contestDate = inDays(40);
  store.plan.contestWeekday = new Date().getDay();
  check("today is contest day", isContestDay(new Date()));
  {
    const steps = planStepsForToday();
    check("contest day core = contest", steps[1].act === "contest", steps[1].act);
    check("contest year chosen", contestEligibleYears().includes(steps[1].arg), String(steps[1].arg));
  }
  check("pickContestYear eligible", contestEligibleYears().includes(pickContestYear()));
  store.plan.contestWeekday = (new Date().getDay() + 1) % 7;
  check("tomorrow-weekday is not contest day today", !isContestDay(new Date()));
  // 3 days before the contest is a rehearsal regardless of weekday
  store.plan.contestDate = inDays(3);
  check("T-3 is a contest day", isContestDay(new Date()));
  store.plan.contestDate = null;
  store.plan.contestWeekday = 6;

  // Star economy
  check("stars: wrong = 1", starsForAnswer(false, 5) === 1);
  check("stars: correct 3 = 1", starsForAnswer(true, 3) === 1);
  check("stars: correct 4 = 2", starsForAnswer(true, 4) === 2);
  check("stars: correct 5 = 3", starsForAnswer(true, 5) === 3);
  const before = store.stars.total, weekBefore = starsThisWeek();
  awardStars("fromBonus", 7);
  check("awardStars sums fromBonus", store.stars.total === before + 7, `${store.stars.total} vs ${before + 7}`);
  check("awardStars logs to the week", starsThisWeek() === weekBefore + 7);
  check("activity day has stars", (store.activity[keyOf(new Date())] || {}).stars >= 7);

  // Daily-plan completion pays once: +10 stars, one free race
  const tk = keyOf(new Date());
  store.planDone[tk] = {};
  const fr = store.games.freeRaces || 0, st = store.stars.total;
  for(const id of ["warmup","core","cooldown"]){ state._planStep = id; markPlanStepDone(); }
  check("plan day bonus +10", store.stars.total === st + 10, `${store.stars.total - st}`);
  check("plan day grants a free race", store.games.freeRaces === fr + 1);
  state._planStep = "core"; markPlanStepDone();
  check("plan day bonus pays once", store.stars.total === st + 10 && store.games.freeRaces === fr + 1);
  delete store.planDone[tk];

  // Effects are no-ops without a browser
  let threw = false;
  try { Sfx.play("correct"); Sfx.play("nope"); Fx.floatStars(3); Fx.confetti(5); Fx.celebrate("plan"); } catch(e){ threw = e.message; }
  check("Sfx/Fx no-op without AudioContext/DOM", !threw, String(threw));
  check("sound setting defaults on", store.settings.sound !== false);

  // Track + recap + rewards render
  const tm = trackMechanics();
  check("track has ≥ 20 mechanics", tm.length >= 20, String(tm.length));
  check("track order follows MECHANIC_ORDER", tm.every((m, i) => i === 0 || app.MECHANIC_ORDER.indexOf(m) > app.MECHANIC_ORDER.indexOf(tm[i-1])));
  const th = trackCardHTML();
  check("track card renders nodes", (th.match(/track-node/g) || []).length === tm.length, String((th.match(/track-node/g) || []).length));
  check("track card has a finish flag", th.includes("track-flag"));
  app.logActivity(true, 5);   // one answered 5-pointer → recap has something to show
  check("recap renders (activity exists)", weeklyRecapHTML().includes("apžvalga"));
  check("recap counts the answer", weeklyRecapHTML().includes("1</b><span>uždavinys"));
  const rh = rewardsCardHTML();
  check("rewards shows weekly goal", rh.includes("Savaitės tikslas"));
  check("rewards shows free race button", rh.includes('id="freeRaceBtn"'));
  // Foundation gate admits 3-pointers; build gate does not
  store.plan.contestDate = inDays(90);
  check("foundation gate has 3-pt", buildRacePool().some(q => q.points === 3));
  store.plan.contestDate = inDays(30);
  check("build gate is 4/5-pt only", buildRacePool().every(q => q.points >= 4));
  store.plan.contestDate = null;
  // The contest sim must not play answer sounds (only the 5-min warn)
  const contestSrc = html.slice(html.indexOf("function startContestTicker("), html.indexOf("function renderContestResults("));
  check("contest sim silent except warn", !/Sfx\.play\("(correct|wrong)"\)/.test(contestSrc) && contestSrc.includes('Sfx.play("warn")'));
}

// ---------- 7c. held-out papers, diagnostic, foundation cadence ----------
section("held-out papers + diagnostic");
{
  const {reservedYears, isReservedYear, needsDiagnosticContest, planStepsForToday,
         pickContestYear, contestEligibleYears, archiveQsForMech, buildRecogPool,
         buildRacePool, findSimilarArchive, isContestDay, planTimelineHTML,
         SHOP_TICKET_COST, rewardsCardHTML, store, state} = app;
  const pad = n => String(n).padStart(2, "0");
  const keyOf = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const inDays = n => { const d = new Date(); d.setDate(d.getDate() + n); return keyOf(d); };
  const savedContests = store.contests; store.contests = [];

  // Reserved = newest 3 eligible unplayed years
  const res = reservedYears();
  const eligDesc = contestEligibleYears().slice().sort((a,b)=>String(b).localeCompare(String(a)));
  check("3 reserved years", res.length === 3, res.join(","));
  check("reserved are the newest eligible", res.join(",") === eligDesc.slice(0,3).join(","), `${res} vs ${eligDesc.slice(0,3)}`);
  check("isReservedYear(string)", isReservedYear(String(res[0])));
  // Every practice picker skips them
  const resSet = new Set(res.map(String));
  check("recog pool skips reserved", buildRecogPool().every(x => !resSet.has(String(x.year))));
  check("race pool skips reserved", buildRacePool().every(x => !resSet.has(String(x.year))));
  for(const m of ["casework", "truth-tellers", "counting-ways"]){
    check(`archiveQsForMech(${m}) skips reserved`, archiveQsForMech(m, null).every(x => !resSet.has(String(x.year))));
  }
  // Tiny mechanics keep their held-out questions (waiver)
  const tiny = Object.keys(app.MECHANIC_METHODOLOGY).filter(m => archiveQsForMech(m, null).length >= 3 && archiveQsForMech(m, null).some(x => resSet.has(String(x.year))));
  check("waiver only when < 3 outside reserved", tiny.every(m => archiveQsForMech(m, null).filter(x => !resSet.has(String(x.year))).length < 3), tiny.join(","));
  // "practice similar" never pulls from a reserved paper
  const srcT = app.ARCHIVE.find(t => !resSet.has(String(t.year)) && t.questions.some(q => q.points === 5 && q.mechanic === "casework"));
  const srcQ = srcT.questions.find(q => q.points === 5 && q.mechanic === "casework");
  check("findSimilarArchive skips reserved", findSimilarArchive(srcQ, srcT.year, 8).every(x => !resSet.has(String(x.year))));
  // Playing a reserved year releases it
  store.contests = [{when: Date.now(), year: res[0], points: 0, scoreWithPenalty: 0, maxPoints: 120}];
  check("played reserved year is released", !reservedYears().includes(res[0]) && reservedYears().length === 3);
  store.contests = [];

  // Diagnostic paper opens the course
  store.plan.contestDate = inDays(70);
  store.plan.contestWeekday = (new Date().getDay() + 1) % 7;
  check("needs diagnostic with no contests", needsDiagnosticContest());
  {
    const steps = planStepsForToday();
    check("day-1 core is the diagnostic contest", steps[1].act === "contest" && /Diagnostinis/.test(steps[1].label), steps[1].label);
    check("diagnostic avoids reserved years", !resSet.has(String(steps[1].arg)), String(steps[1].arg));
  }
  store.contests = [{when: Date.now() - 86400000, year: eligDesc[5], points: 0, scoreWithPenalty: 0, maxPoints: 120}];
  check("no diagnostic once a contest exists", !needsDiagnosticContest());
  check("after diagnostic the core is not a contest", planStepsForToday()[1].act !== "contest", planStepsForToday()[1].act);
  // pickContestYear keeps reserved for the taper
  check("pickContestYear avoids reserved outside taper", !resSet.has(String(pickContestYear())), String(pickContestYear()));
  store.plan.contestDate = inDays(6);
  const taperPick = pickContestYear();
  check("pickContestYear may use reserved in taper", contestEligibleYears().includes(taperPick));
  // Foundation: contest day only every other week
  store.plan.contestDate = inDays(80);
  store.plan.contestWeekday = new Date().getDay();
  const nextWeek = new Date(); nextWeek.setDate(nextWeek.getDate() + 7);
  const twoWeeks = new Date(); twoWeeks.setDate(twoWeeks.getDate() + 14);
  store.contests = [{when: Date.now() - 1*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("foundation: biweekly contest day", !isContestDay(new Date()) && !isContestDay(nextWeek) && isContestDay(twoWeeks));
  store.plan.contestDate = inDays(40);
  store.contests = [{when: Date.now() - 7*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("build: weekly contest day", isContestDay(new Date()) && isContestDay(nextWeek));
  // Missed weekday → the first day the paper is overdue takes it
  store.plan.contestWeekday = (new Date().getDay() + 3) % 7;
  store.contests = [{when: Date.now() - 8*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("overdue paper lands on a non-preferred day", isContestDay(new Date()));
  store.contests = [{when: Date.now() - 6*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("not yet overdue → waits for the weekday", !isContestDay(new Date()));
  store.plan.contestWeekday = new Date().getDay();
  store.contests = [];
  store.contests = [{when: Date.now() - 2*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("no paper within 5 days of the last one", !isContestDay(new Date()));
  store.contests = [];
  store.plan.contestDate = inDays(4);
  check("weekly slot yields near the T-3 rehearsal", !isContestDay(new Date()));
  store.plan.contestDate = inDays(2);
  store.contests = [];
  check("missed T-3 rehearsal slides to T-2", isContestDay(new Date()));
  store.contests = [{when: Date.now() - 1*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];
  check("T-2 stays quiet right after a paper", !isContestDay(new Date()));
  store.contests = [];
  // Foundation sprint only while needed: with ≥ 2 sprints and no speed flag → mechanic
  store.plan.contestDate = inDays(80);
  store.plan.contestWeekday = (new Date().getDay() + 1) % 7;
  const savedSessions = store.sessions;
  store.sessions = [{sprint:true, when:1, questions:[], bandTime:{}}, {sprint:true, when:2, questions:[], bandTime:{}}];
  store.contests = [{when: Date.now() - 10*86400000, year: eligDesc[6], points:0, scoreWithPenalty:0, maxPoints:120}];   // diagnostic done
  check("foundation routes to mechanic once speed is fine", ["playlist","mixed","due"].includes(planStepsForToday()[1].act), planStepsForToday()[1].act);
  store.sessions = savedSessions;
  // Timeline + shop ticket
  check("timeline renders three phases", (planTimelineHTML().match(/tl-seg/g) || []).length >= 2);
  check("timeline has a today marker", planTimelineHTML().includes("tl-today"));
  check("ticket costs 30", SHOP_TICKET_COST === 30);
  check("shop lists the ticket", rewardsCardHTML().includes('data-shop-ticket'));
  store.plan.contestDate = null; store.plan.contestWeekday = 6; store.contests = savedContests;
}

// ---------- 7d. canvas games driven headlessly ----------
section("minigames");
{
  const {openJumpGame, openRaceGame, renderGamePick, openFreeRace, planMinutes, planStepsForToday, store, state} = app;
  for(const [name, open, view] of [["jump", openJumpGame, "jump"], ["race", openRaceGame, "race"]]){
    let threw = null;
    try { open("medium", 99); } catch(e){ threw = e.message; }   // many lives: free-run must not end on its own
    check(`${name}: opens`, !threw && state.view === view, threw || state.view);
    const g = state._race;
    const ran = runFrames(240);
    check(`${name}: loop runs`, ran === 240 && g.distance > 0, `frames ${ran}, distance ${g && g.distance}`);
    check(`${name}: still ${view}`, state.view === view);
    // force a collision: one life, obstacle on the player
    g.lives = 1; g.invuln = 0;
    if(name === "jump"){ g.y = 260; g.vy = 0; g.onGround = true; g.obstacles.push({x: 54, w: 30, h: 40}); }
    else { g.obstacles.push({lane: g.lane, y: 540 - 60 - 14}); }
    const before = (name === "jump" ? store.games.jumpPlays : store.games.plays) || 0;
    runFrames(10);
    check(`${name}: collision ends the game`, state.view === "raceOver", state.view);
    check(`${name}: play counted once`, ((name === "jump" ? store.games.jumpPlays : store.games.plays) || 0) === before + 1);
    runFrames(5);   // a late frame must not re-enter the loop
    check(`${name}: endGame idempotent`, ((name === "jump" ? store.games.jumpPlays : store.games.plays) || 0) === before + 1);
  }
  let threw = null;
  try { renderGamePick("easy", 1, "x"); } catch(e){ threw = e.message; }
  check("game picker renders", !threw && state.view === "gamePick", threw || state.view);
  store.games.freeRaces = 1;
  openFreeRace();
  check("free ticket opens the picker and is consumed", state.view === "gamePick" && store.games.freeRaces === 0);
  // Honest time budget
  const steps = planStepsForToday();
  check("plan minutes positive", planMinutes(steps) > 0);
  check("playlist day ≥ 20 min", planMinutes([{act:"warmup"},{act:"playlist"},{act:"recog"}]) >= 20);
  check("no stale 20-min copy", !html.includes("(~20 min)") && !html.includes("~20 min treniruotė"));
  // Loop 3: sprint never asks confidence; time stars only in learning views
  store.settings.askConfidence = true;
  state._sprintMode = false; check("confidence on in a normal quiz", app.askConfidenceNow());
  state._sprintMode = true;  check("confidence off in the sprint", !app.askConfidenceNow());
  state._sprintMode = false; store.settings.askConfidence = false;
  check("home/plan/race earn no time stars", !app.STAR_TIME_VIEWS.has("home") && !app.STAR_TIME_VIEWS.has("plan") && !app.STAR_TIME_VIEWS.has("race"));
  check("quiz/playlist/contest earn time stars", ["quiz","playlist","contest"].every(v => app.STAR_TIME_VIEWS.has(v)));
  check("mission leads with the plan step", html.includes("action: 'planStep'") && html.includes('act === "planStep"'));
  {
    const {openPlaylist, mechTargetFor, store, state} = app;
    const pad = n => String(n).padStart(2, "0");
    const d = new Date(); d.setDate(d.getDate() + 80);
    store.plan.contestDate = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;   // foundation → cap at 4
    store.mechAttempts = {}; store.masteredBand = {}; delete store.masteredMech.casework;
    openPlaylist("casework");
    check("openPlaylist without a band uses the plan target (foundation → 4)", state.playlistContent.sourceBand === 4, String(state.playlistContent.sourceBand));
    openPlaylist("casework", 5);
    check("explicit band still wins", state.playlistContent.sourceBand === 5);
    store.plan.contestDate = null; state.view = "home";
  }
  check("parent view offers export/import", html.includes('id="exportBtn"') && html.includes('id="importFile"') && html.includes("function importProgressFile"));
  check("import validates the file shape", html.includes("!incoming.activity || !incoming.settings"));
  check("playlists ask confidence", html.includes('data-pl-conf="a"') && html.includes("state.playlistConf[k] = b.dataset.plConf"));
  check("empty quiz gives no plan credit", html.includes("if(session.answered >= Math.ceil(total / 2)) markPlanStepDone();"));
  check("contest result records practisedBefore", html.includes("practisedBefore = qs.filter") && html.includes("byTimer: !!byTimer, practisedBefore"));
  // Loop 4: parking grows with fails; retest runs at the mastered band
  {
    const {mechTargetFor, noteMechAttempt, store} = app;
    const m = "casework";
    store.mechAttempts = {}; store.masteredBand = {}; delete store.masteredMech[m];
    store.plan.contestDate = null;
    const t0 = mechTargetFor(m, "build");
    check("casework targets band 5 in build", t0 && t0.band === 5, JSON.stringify(t0));
    noteMechAttempt(m, 5, false); noteMechAttempt(m, 5, false);
    const t1 = mechTargetFor(m, "build");
    check("two fails step down to band 4", t1 && t1.band === 4, JSON.stringify(t1));
    noteMechAttempt(m, 4, false); noteMechAttempt(m, 4, false);
    const t2 = mechTargetFor(m, "build");
    check("two fails at band 4 step down to 3", t2 && t2.band === 3, JSON.stringify(t2));
    noteMechAttempt(m, 3, false); noteMechAttempt(m, 3, false);
    check("two fails at the lowest band park it", mechTargetFor(m, "build") === null);
    store.mechAttempts[m][3].lastAt = Date.now() - 8*86400000;
    check("parked 7 d after 2 fails → back", mechTargetFor(m, "build") !== null);
    noteMechAttempt(m, 3, false);
    store.mechAttempts[m][3].lastAt = Date.now() - 8*86400000;
    check("parked 14 d after 3 fails", mechTargetFor(m, "build") === null);
    store.mechAttempts[m][3].lastAt = Date.now() - 15*86400000;
    check("…and back after 14 d", mechTargetFor(m, "build") !== null);
    store.mechAttempts = {};
  }
  state.view = "home";
}

// ---------- 7e. legacy save migration ----------
section("legacy save");
{
  const {loadStore, LS_KEY, store, state, masteredBandOf, mechTopBand} = app;
  // A save shaped like the app wrote it before the prep layer existed.
  const legacy = {
    sessions:[{when: 1, total: 10, correct: 7, points: 20, questions: []}], catStats:{}, subStats:{},
    mechStats:{casework:{5:{attempts:4, wrong:1}}}, dueQueue:{"2019-24":{year:"2019", num:24, mech:"casework", band:5, dueAt: 1, streak: 0}},
    masteredMech:{casework: 1}, confStats:{a:{attempts:0,wrong:0}}, activity:{"2026-09-01":{answered:5, correct:4}},
    contests:[{when: 1, year:"2018", points: 50, scoreWithPenalty: 45, maxPoints: 120, correct: 14, total: 30, answered: 20, byBand:{}}],
    settings:{count:15, difficulties:[3,4,5], useTimer:true}, streak:{count:3, lastDay:"2026-09-01"},
    stars:{total:40, fromQ:30, fromTime:10}, games:{plays:2, best:300, bestByDiff:{easy:300}},
    achievements:{q10: 1}, plan:{contestDate:null}, planDone:{}, seenQ:{}, mechRecent:{}, recogStats:{attempts:3, correct:2},
    shop:{activeColor:"classic", colors:["classic"]},
  };
  localStorageStub.setItem(LS_KEY, JSON.stringify(legacy));
  let loaded = null, threw = null;
  try { loaded = loadStore(); } catch(e){ threw = e.message; }
  check("legacy store loads", !threw && loaded, threw);
  if(loaded){
    check("legacy: sound default on", loaded.settings.sound !== false);
    check("legacy: plan defaults", loaded.plan.contestWeekday === 6 && loaded.plan.weeklyStarGoal === 150 && loaded.plan.weeklyReward === "");
    check("legacy: stars fromBonus", loaded.stars.fromBonus === 0 && loaded.stars.total === 40);
    check("legacy: games tickets/jump", loaded.games.freeRaces === 0 && loaded.games.jumpBest === 0 && loaded.games.best === 300);
    check("legacy: masteredBand/mechAttempts/recogSeen", loaded.masteredBand && loaded.mechAttempts && loaded.recogSeen);
    check("legacy: old mastery kept", loaded.masteredMech.casework === 1);
  }
  // Old mastery (no masteredBand) reads as full mastery at the top band
  const savedMM = store.masteredMech, savedMB = store.masteredBand;
  store.masteredMech = {casework: 1}; store.masteredBand = {};
  check("old mastery = top band", masteredBandOf("casework") === mechTopBand("casework") && mechTopBand("casework") >= 4);
  check("ancient mastery shows as stale on the track", app.trackCardHTML().includes("track-node stale"));
  store.masteredMech = savedMM; store.masteredBand = savedMB;
  localStorageStub.removeItem(LS_KEY);
}

// ---------- 7f. contest-date edge cases ----------
section("date edges");
{
  const {planStepsForToday, planPhase, isContestDay, needsDiagnosticContest, planTimelineHTML, planTaperDays, weekStripHTML, store} = app;
  const pad = n => String(n).padStart(2, "0");
  const keyOf = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const inDays = n => { const d = new Date(); d.setDate(d.getDate() + n); return keyOf(d); };
  const savedC = store.contests; store.contests = [];
  const savedA = store.activity; store.activity = {};
  // Contest today, nothing ever recorded: timeline must not divide by zero
  store.plan.startDate = inDays(0); store.plan.contestDate = inDays(0);
  const tl = planTimelineHTML();
  check("timeline on contest day has no NaN", !/NaN/.test(tl), tl.slice(0, 120));
  check("contest day plan is a single rest step", planStepsForToday().length === 1);
  check("no diagnostic on contest day", !needsDiagnosticContest());
  // Contest in the past
  store.plan.contestDate = inDays(-3);
  let threw = null, steps = null;
  try { steps = planStepsForToday(); } catch(e){ threw = e.message; }
  check("past date: plan still builds", !threw && steps && steps.length === 3, threw || JSON.stringify(steps));
  check("past date: phase build", planPhase() === "build");
  check("past date: no contest day", !isContestDay(new Date()));
  check("past date: no diagnostic", !needsDiagnosticContest());
  check("past date: timeline hidden", planTimelineHTML() === "");
  let ws = null; try { ws = weekStripHTML(); } catch(e){ threw = e.message; }
  check("past date: week strip renders", !threw && typeof ws === "string");
  // startDate after contestDate (parent edited the date backwards)
  store.plan.startDate = inDays(10); store.plan.contestDate = inDays(5);
  check("inverted start/contest → default taper", planTaperDays() === 10);
  check("inverted start: timeline safe", !/NaN/.test(planTimelineHTML()));
  // Tomorrow
  store.plan.startDate = inDays(-30); store.plan.contestDate = inDays(1);
  check("eve: no diagnostic", !needsDiagnosticContest());
  check("eve: strategy step", planStepsForToday().some(s => s.act === "strategy"));
  store.plan.contestDate = null; store.plan.startDate = null; store.contests = savedC; store.activity = savedA;
}

// ---------- 7g. training days ----------
section("training days");
{
  const {isTrainingDay, planStepsForToday, isContestDay, markPlanStepDone, logActivity, store, state} = app;
  const pad = n => String(n).padStart(2, "0");
  const keyOf = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const inDays = n => { const d = new Date(); d.setDate(d.getDate() + n); return keyOf(d); };
  const todayWd = new Date().getDay();
  check("default: every day trains", store.plan.trainingDays.length === 7 && isTrainingDay(new Date()));
  store.plan.contestDate = inDays(40); store.plan.startDate = inDays(-20); store.contests = [{when: Date.now() - 20*864e5, year: "2010", points:0, scoreWithPenalty:0, maxPoints:120}];
  store.plan.trainingDays = [0,1,2,3,4,5,6].filter(d => d !== todayWd);
  check("rest day: no plan steps", planStepsForToday().length === 0);
  check("rest day: no paper", !isContestDay(new Date()));
  const stars0 = store.stars.total, fr0 = store.games.freeRaces || 0;
  state._planStep = "core"; markPlanStepDone();
  check("rest day: no bonus for nothing", store.stars.total === stars0 && (store.games.freeRaces || 0) === fr0);
  // streak survives rest days: last answer 3 days ago, the two days between are rest days
  const wdM1 = (todayWd + 6) % 7, wdM2 = (todayWd + 5) % 7;
  store.plan.trainingDays = [0,1,2,3,4,5,6].filter(d => d !== wdM1 && d !== wdM2);
  store.streak = {count: 4, lastDay: inDays(-3), freezesUsed: 0, freezeMonth: null};
  logActivity(true, 3);
  check("streak continues across rest days", store.streak.count === 5, String(store.streak.count));
  store.plan.trainingDays = [0,1,2,3,4,5,6];
  store.streak = {count: 4, lastDay: inDays(-3), freezesUsed: 2, freezeMonth: null};
  logActivity(true, 3);
  check("two missed training days, no freezes left -> reset", store.streak.count === 1, String(store.streak.count));
  store.plan.trainingDays = [0,1,2,3,4,5,6]; store.plan.contestDate = null; store.contests = [];
  // A finished paper counts as today's activity: streak + stars
  {
    const {creditContestActivity, ARCHIVE} = app;
    const paper = ARCHIVE.find(x => x.year === "2015").questions.filter(q => q.correct).slice(0, 30);
    const answers = {}; paper.forEach((q, i) => { if(i < 20) answers[q.num] = i % 3 === 0 ? "A" : q.correct; });
    store.streak = {count: 6, lastDay: inDays(-1), freezesUsed: 0, freezeMonth: null};
    const st = store.stars.total, act = (store.activity[keyOf(new Date())] || {answered:0}).answered;
    creditContestActivity(paper, answers);
    check("paper bumps the streak", store.streak.count === 7, String(store.streak.count));
    check("paper counts answered questions", (store.activity[keyOf(new Date())].answered) === act + 20);
    check("paper pays stars", store.stars.total > st);
  }
}

// ---------- 7h. no surprise 30-question sessions ----------
section("no surprises");
{
  const {renderContestIntro, newTestSizeLabel, needsDiagnosticContest, planStepsForToday, isContestDay, store, state} = app;
  const pad = n => String(n).padStart(2, "0");
  const keyOf = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
  const inDays = n => { const d = new Date(); d.setDate(d.getDate() + n); return keyOf(d); };
  store.settings.count = 30; store.settings.useTimer = true;
  check("new-test label states size and time", newTestSizeLabel() === "30 klausimų · 75 min", newTestSizeLabel());
  store.settings.count = 15;
  check("15 → 38 min", newTestSizeLabel() === "15 klausimų · 38 min", newTestSizeLabel());
  check("results footer is plan-aware", html.includes('id="planNextBtn"') && html.includes("Toliau pagal planą"));
  check("contest start goes through the intro, not confirm", /renderContestIntro\(year\);\s*\}/.test(html) && !html.includes("Pradėti kontrolinį testą iš"));
  // diagnostic day: intro renders; "Ne dabar" moves the paper
  store.contests = []; store.plan.contestDate = inDays(70); store.plan.startDate = inDays(0); store.plan.contestPostponedDay = null;
  check("day 1 core is the diagnostic", planStepsForToday()[1].act === "contest");
  check("plan paper year is stable across renders", new Set([1,2,3,4,5,6,7,8].map(() => planStepsForToday()[1].arg)).size === 1);
  state._planStep = "core";
  let threw = null; try { renderContestIntro(planStepsForToday()[1].arg); } catch(e){ threw = e.message; }
  check("contest intro renders", !threw && state.view === "contestIntro", threw || state.view);
  store.plan.contestPostponedDay = keyOf(new Date());
  check("postponed: no diagnostic today", !needsDiagnosticContest());
  check("postponed: core is not a contest", planStepsForToday()[1].act !== "contest", planStepsForToday()[1].act);
  check("postponed: today is not a contest day", !isContestDay(new Date()));
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  store.plan.contestPostponedDay = keyOf(new Date(Date.now() - 864e5));
  check("postpone expires the next day", needsDiagnosticContest());
  store.plan.contestPostponedDay = null;
  // every plan end screen offers the next plan step
  const {nextPlanStep, renderRecogResult, $app} = app;
  const tk = keyOf(new Date());
  store.planDone[tk] = {};
  check("next step skips the current one", nextPlanStep("warmup") && nextPlanStep("warmup").id !== "warmup");
  state.recogQs = new Array(10).fill(0); state.recogCorrect = 7; state._planStep = "cooldown";
  renderRecogResult();
  check("recog result offers the next plan step", $app.innerHTML.includes('id="planNextBtn"'));
  state._planStep = null; renderRecogResult();
  check("recog result outside the plan has no plan button", !$app.innerHTML.includes('id="planNextBtn"'));
  store.planDone[tk] = {warmup:true, core:true}; store.games.freeRaces = 0; state._planStep = "cooldown";
  renderRecogResult();
  check("finishing the day pays a ticket", store.planDone[tk].bonus && store.games.freeRaces === 1);
  check("…and the end screen offers to play it", $app.innerHTML.includes('id="planRewardBtn"'));
  store.games.freeRaces = 0;
  check("playlist end and contest results wire the plan button", (html.match(/wirePlanNext\(/g) || []).length >= 5);
  const pm = app.playlistMasteryMs;
  check("mastery clock: three 5-pt = 15 min", pm([5,5,5].map(p => ({q:{points:p}}))) === 15 * 60000);
  check("mastery clock: three 3-pt = 3 min", pm([3,3,3].map(p => ({q:{points:p}}))) === 3 * 60000);
  store.planDone[tk] = {};
  store.plan.contestDate = null; state.view = "home";
}

// ---------- 7½. 5-pt generators: independent answer verification ----------
// Each new generator attaches q._check with its parameters; here we
// re-derive the answer with a SEPARATE implementation and compare.
section("5-pt generator math verification");
const VERIFIERS = {
  liarsCount(c){
    return c.variant === "exact" ? c.ans === c.n - 1
         : (c.n % 2 === 0 && c.ans === c.n / 2);
  },
  cupsFlip(c){
    // independent BFS over the count of upside-down cups
    const dist = new Array(c.n + 1).fill(-1);
    dist[c.d0] = 0;
    const qq = [c.d0];
    while(qq.length){
      const d = qq.shift();
      for(let j = Math.max(0, c.m - (c.n - d)); j <= Math.min(c.m, d); j++){
        const nd = d - j + (c.m - j);
        if(nd >= 0 && nd <= c.n && dist[nd] === -1){ dist[nd] = dist[d] + 1; qq.push(nd); }
      }
    }
    return dist[0] === c.ans;
  },
  blackboardMin(c){
    // consecutive runs always achieve the parity bound
    return c.ans === c.S % 2;
  },
  digitReversal(c){
    const fits = [];
    for(let x = 10; x <= 99; x++){
      const a = Math.floor(x/10), b = x % 10;
      if(a + b === c.s && x - (10*b + a) === c.d) fits.push(x);
    }
    return fits.length === 1 && fits[0] === c.ans;
  },
  gridPaths(c){
    // independent: binomial C(cols+rows, cols)
    let v = 1;
    for(let i = 1; i <= c.cols; i++) v = v * (c.rows + i) / i;
    return Math.round(v) === c.ans;
  },
  nimGame(c){
    return c.ans === c.N % (c.k + 1) && c.ans >= 1 && c.ans <= c.k;
  },
  raceLogic5(c){
    const nn = 5;
    const holds = (clue, pos) => {
      const [t, i, j, cc] = clue;
      if(t === "after")    return pos[i] === pos[j] + 1;
      if(t === "before")   return pos[i] < pos[j];
      if(t === "notFirst") return pos[i] !== 1;
      if(t === "notLast")  return pos[i] !== nn;
      if(t === "between")  return Math.abs(pos[i] - pos[j]) - 1 === cc;
      return false;
    };
    const perms = [];
    (function build(rest, acc){
      if(!rest.length){ const pos = {}; acc.forEach((p, i) => pos[p] = i + 1); perms.push(pos); return; }
      for(let x = 0; x < rest.length; x++) build(rest.slice(0, x).concat(rest.slice(x+1)), acc.concat([rest[x]]));
    })([0,1,2,3,4], []);
    const alive = perms.filter(pos => c.clues.every(cl => holds(cl, pos)));
    if(alive.length !== 1) return false;
    // the surviving permutation must match the generator's secret order
    return c.order.every((p, i) => alive[0][p] === i + 1);
  },
  equalGroups(c){
    let g = 0;
    for(let x = 2; x <= c.S; x++) if(c.S % x === 0 && c.S / x >= c.n) g = x;
    return g === c.ans;
  },
  appendDigit(c){
    const fits = [];
    if(c.variant === "append"){
      for(let x = 1; x <= c.diff; x++) if(x*10 + c.d - x === c.diff) fits.push(x);
    } else {
      // original ≈ 10/9 of the decrease, so search past c.diff
      const hi = Math.ceil(c.diff * 10 / 9) + 10;
      for(let x = 10; x <= hi; x++) if(x - Math.floor(x/10) === c.diff) fits.push(x);
    }
    return fits.length === 1 && fits[0] === c.ans;
  },
  remainderPuzzle(c){
    for(let x = 1; x <= 2*c.p*c.q; x++){
      if(x % c.p === c.rp && x % c.q === c.rq) return x === c.ans;
    }
    return false;
  },
  cubeNet(c){
    const OPP = [[0,5],[1,3],[2,4]];
    const pair = OPP.find(pp => pp.includes(c.askIdx));
    const oppIdx = pair[0] === c.askIdx ? pair[1] : pair[0];
    return c.nums[oppIdx] === c.ans;
  },
  erasedAverage(c){
    const S = c.n*(c.n+1)/2;
    return S - c.V*(c.n - 1) === c.ans && c.ans >= 1 && c.ans <= c.n;
  },
  dominoMax(c){
    const total = c.rows * c.cols;
    const remColor = ([i,j]) => (i + j) % 2;
    let b = 0, w = 0;
    for(let i = 0; i < c.rows; i++) for(let j = 0; j < c.cols; j++) ((i+j)%2 === 0 ? b++ : w++);
    if(remColor(c.rem1) === 0) b--; else w--;
    if(remColor(c.rem2) === 0) b--; else w--;
    // matching can't exceed the smaller color class, and can't miss it by much
    return c.ans <= Math.min(b, w) && c.ans >= Math.min(b, w) - 2 && c.ans <= (total - 2) / 2;
  },
};
const NEW_GENS = Object.keys(VERIFIERS);
for(const key of NEW_GENS){
  let verified = 0;
  for(let seed = 1; seed <= 60; seed++){
    const q = buildQuestionFromKey(key, seed);
    if(!q._check){ check(`${key}#${seed} has _check`, false); continue; }
    let ok = false;
    try { ok = VERIFIERS[key](q._check); }
    catch(e){ check(`${key}#${seed} verifier`, false, "threw: " + e.message); continue; }
    check(`${key}#${seed} answer verified`, ok, JSON.stringify(q._check).slice(0, 140));
    if(ok) verified++;
  }
  console.log(`${key}: ${verified}/60 independently verified`);
}

// ---------- 8. render smoke: new views execute without throwing ----------
section("render smoke (stubbed DOM)");
for(const [name, fn] of [
  ["openPlan",       () => app.openPlan()],
  ["openRecogDrill", () => app.openRecogDrill()],
  ["openMixedSet",   () => app.openMixedSet(6)],
  ["openPlaylist",   () => app.openPlaylist("truth-tellers")],
  ["openPlaylist forced band", () => app.openPlaylist("area-decomp", 3)],
  ["startSprint",    () => app.startSprint()],
  ["openRaceChallenge", () => app.openRaceChallenge()],
]){
  try { fn(); console.log(`ok    ${name}`); }
  catch(e){ check(name, false, "threw: " + e.message); }
}

// ---------- result ----------
console.log("");
if(failures){
  console.error(`${failures} check(s) FAILED`);
  process.exit(1);
}
console.log("ALL CHECKS PASSED ✓");
