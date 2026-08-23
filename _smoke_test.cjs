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
function stubEl(){
  return {
    innerHTML: "", textContent: "", style: {cssText: ""}, dataset: {},
    className: "", disabled: false,
    addEventListener(){}, removeEventListener(){},
    querySelector(){ return null; }, querySelectorAll(){ return []; },
    appendChild(){}, remove(){}, setAttribute(){},
    classList: {add(){}, remove(){}},
    getContext(){ return null; }, getBoundingClientRect(){ return {left:0, width:0}; },
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
        openRaceChallenge, requestOpenContest, state, store};
`;
let app;
try {
  app = new Function(
    "window", "document", "localStorage", "setInterval", "clearInterval",
    "requestAnimationFrame", "cancelAnimationFrame", "confirm", "alert", "fetch",
    m[1] + EXPORTS
  )(
    windowStub, documentStub, localStorageStub,
    () => 0, () => {}, () => 0, () => {}, () => false, () => {}, () => Promise.reject(new Error("no net"))
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

  check("plan CTA is ghost", html.includes('class="btn ghost" id="planBtn"'));
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
