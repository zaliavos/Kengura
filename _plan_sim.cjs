/* Plan simulator: runs the daily plan with a mocked clock for N days with
   a synthetic kid of accuracy P and prints the schedule it produced.
     node _plan_sim.cjs [days=84] [accuracy=0.7] [--quiet]
   Use it to check cadence/starvation after changing planStepsForToday,
   the due queue, mastery rules or the track order. */
const fs = require("fs"), path = require("path");
const DIR = __dirname;
function stubEl(){ return { innerHTML:"", textContent:"", style:{cssText:""}, dataset:{}, className:"", disabled:false,
  addEventListener(){}, removeEventListener(){}, querySelector(){return null;}, querySelectorAll(){return [];},
  appendChild(){}, remove(){}, setAttribute(){}, classList:{add(){},remove(){}}, getContext(){return null;},
  getBoundingClientRect(){return {left:0,width:0};}, scrollIntoView(){} }; }
const documentStub = { getElementById(){return stubEl();}, createElement(){return stubEl();}, querySelector(){return null;},
  querySelectorAll(){return [];}, addEventListener(){}, removeEventListener(){}, body:{appendChild(){}}, hidden:true };
const windowStub = { addEventListener(){}, removeEventListener(){} };
const ls = { _m:new Map(), getItem(k){return this._m.has(k)?this._m.get(k):null;}, setItem(k,v){this._m.set(k,String(v));}, removeItem(k){this._m.delete(k);} };
new Function("window", fs.readFileSync(path.join(DIR,"kengura-archive.js"),"utf8"))(windowStub);
const html = fs.readFileSync(path.join(DIR,"kengura.html"),"utf8");
const m = html.match(/<script>\s*("use strict";[\s\S]*?)<\/script>\s*<\/body>/);
// ---- fake clock ----
const RealDate = Date;
let NOW = new RealDate(2026, 9, 12, 18, 0, 0).getTime();   // Monday 2026-10-12 18:00
class FakeDate extends RealDate {
  constructor(...a){ if(a.length === 0) super(NOW); else super(...a); }
  static now(){ return NOW; }
}
global.Date = FakeDate;
const EXPORTS = `return {store, state, planStepsForToday, planPhase, daysToContest, isContestDay, needsDiagnosticContest,
  nextMechanicToLearn, dueNow, markPlanStepDone, archiveQsForMech, MECHANIC_ORDER, MECHANIC_LABEL, recordArchiveAnswer,
  noteMechAttempt, masteredBandOf, mechTopBand, creditContestActivity,
  ARCHIVE, pickContestYear, reservedYears, contestEligibleYears, logActivity, pickPlaylistContent, trackMechanics, queueContestWrongs};`;
const app = new Function("window","document","localStorage","setInterval","clearInterval","requestAnimationFrame","cancelAnimationFrame","confirm","alert","fetch", m[1]+EXPORTS)(
  windowStub, documentStub, ls, ()=>0, ()=>{}, ()=>0, ()=>{}, ()=>false, ()=>{}, ()=>Promise.reject(new Error("x")));
const {store, state} = app;
// ---- scenario ----
const CONTEST_IN = parseInt(process.argv[2] || "84", 10);
const SKILL = parseFloat(process.argv[3] || "0.7");   // p(correct) on a mastery question
// --skip=0,3 → weekdays (0 = Sunday) the kid does NOT train; --start=N → set the contest date only N days in
const skipArg = (process.argv.find(a => a.startsWith("--skip=")) || "--skip=").slice(7);
const SKIP_DAYS = new Set(skipArg ? skipArg.split(",").map(Number) : []);
// --learn → the kid gets better at a mechanic with every playlist on it (+0.06 per exposure, cap 0.95)
const LEARN = process.argv.includes("--learn");
const MISS = parseFloat((process.argv.find(a => a.startsWith("--miss=")) || "--miss=0").slice(7));   // p(random day off)
const exposure = {};
const pMech = mech => Math.min(0.95, SKILL + (LEARN ? 0.06 * (exposure[mech] || 0) : 0));
const c = new RealDate(NOW); c.setDate(c.getDate() + CONTEST_IN);
store.plan.contestDate = `${c.getFullYear()}-${String(c.getMonth()+1).padStart(2,"0")}-${String(c.getDate()).padStart(2,"0")}`;
store.plan.contestWeekday = 6;
if(SKIP_DAYS.size) store.plan.trainingDays = [0,1,2,3,4,5,6].filter(d => !SKIP_DAYS.has(d));
let rng = Number((process.argv.find(a => a.startsWith("--seed=")) || "--seed=42").slice(7));; const rand = () => { rng = (rng * 1103515245 + 12345) & 0x7fffffff; return rng / 0x7fffffff; };
const log = []; const tally = {};
const seenMastery = new Set();
let skipped = 0;
for(let day = 0; day <= CONTEST_IN; day++){
  if(SKIP_DAYS.has(new RealDate(NOW).getDay()) || (MISS > 0 && rand() < MISS)){ skipped++; NOW += 24*60*60*1000; continue; }
  const steps = app.planStepsForToday();
  const core = steps.find(s => s.id === "core") || steps[0];
  const phase = app.planPhase();
  tally[phase] = tally[phase] || {}; tally[phase][core.act] = (tally[phase][core.act] || 0) + 1;
  // simulate doing the core
  if(core.act === "contest" && core.arg){
    const t = app.ARCHIVE.find(x => String(x.year) === String(core.arg));
    const seenBefore = t.questions.filter(q => store.seenQ[`${t.year}-${q.num}`]).length;
    store.contests.push({when: NOW, year: t.year, points: 60, scoreWithPenalty: 60, maxPoints: 120, byBand:{}});
    const answers = Object.fromEntries(t.questions.map(q => [q.num, rand() < 0.6 ? q.correct : "A"]));
    app.creditContestActivity(t.questions, answers);
    app.queueContestWrongs(t.year, t.questions, answers);   // automatic since loop 53
    t.questions.forEach(q => { store.seenQ[`${t.year}-${q.num}`] = NOW; });
    log.push(`${day.toString().padStart(2)} ${phase.padEnd(10)} CONTEST ${t.year}  (practised before: ${seenBefore}/30)`);
  } else if(core.act === "playlist"){
    const content = app.pickPlaylistContent(core.arg, core.band);
    let ok = 0;
    const pm = pMech(core.arg); exposure[core.arg] = (exposure[core.arg] || 0) + 1;
    for(const it of content.mastery){ const r = rand() < pm; if(r) ok++; app.recordArchiveAnswer(it.year, it.q, r, null); seenMastery.add(`${it.year}-${it.q.num}`); }
    if(content.worked) app.recordArchiveAnswer(content.worked.year, content.worked.q, true, null);
    if(content.tryQ) app.recordArchiveAnswer(content.tryQ.year, content.tryQ.q, rand() < pm, null);
    const passed = ok === content.mastery.length && content.mastery.length >= 2;   // same rule as finalizePlaylist
    app.noteMechAttempt(core.arg, content.sourceBand, passed);
    if(passed){ store.masteredBand[core.arg] = Math.max(app.masteredBandOf(core.arg), content.sourceBand); if(content.sourceBand >= app.mechTopBand(core.arg)) store.masteredMech[core.arg] = NOW; }
    log.push(`${day.toString().padStart(2)} ${phase.padEnd(10)} playlist ${core.arg} band${content.sourceBand} ${ok}/${content.mastery.length}${passed?" ✓":""}`);
  } else if(core.act === "due"){
    const due = app.dueNow().slice(0, 10);
    for(const d of due){ const t = app.ARCHIVE.find(x => String(x.year) === String(d.year)); const q = t.questions.find(q => q.num === d.num); app.recordArchiveAnswer(t.year, q, rand() < SKILL + 0.15, null); }
    log.push(`${day.toString().padStart(2)} ${phase.padEnd(10)} due x${due.length}`);
  } else if(core.act === "sprint"){
    store.sessions.push({when: NOW, sprint: true, questions: [], bandTime: {}});
    log.push(`${day.toString().padStart(2)} ${phase.padEnd(10)} sprint`);
  } else {
    log.push(`${day.toString().padStart(2)} ${phase.padEnd(10)} ${core.act}`);
  }
  const warm = steps.find(s => s.id === "warmup");
  if(warm && warm.act === "dueWarm"){
    for(const d of app.dueNow().slice(0, 3)){ const t = app.ARCHIVE.find(x => String(x.year) === String(d.year)); const q = t.questions.find(q => q.num === d.num); app.recordArchiveAnswer(t.year, q, rand() < SKILL + 0.15, null); }
  }
  for(const s of steps){ state._planStep = s.id; app.markPlanStepDone(); }
  NOW += 24*60*60*1000;
}
console.log(log.join("\n"));
console.log("\n--- core-step tally by phase ---"); console.log(JSON.stringify(tally, null, 1));
if(skipped) console.log("days skipped:", skipped, " streak at end:", store.streak.count);
console.log("full mastery:", Object.keys(store.masteredMech).length, " partial:", Object.keys(store.masteredBand).filter(m => !store.masteredMech[m]).length, "/", app.trackMechanics().length, " contests:", store.contests.length, " dueQueue:", Object.keys(store.dueQueue).length, " stars:", store.stars.total);
console.log("unmastered:", app.MECHANIC_ORDER.filter(m => !store.masteredMech[m] && app.trackMechanics().includes(m)).join(","));
