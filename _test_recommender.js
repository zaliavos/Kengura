// Standalone runtime test for the new mechanic-aware recommender.
// Loads kengura-archive.js, copies the pieces we need from kengura.html,
// then prints the routing decision for every 5-point archive question.
const fs = require('fs');
const html = fs.readFileSync('kengura.html', 'utf8');
const archive = fs.readFileSync('kengura-archive.js', 'utf8');

global.window = {};
eval(archive);
const ARCHIVE = window.KENGURA_ARCHIVE.archive;

// Slice out the GENERATORS block (we skip running generators themselves;
// we only need their declared difficulty values, which we infer by parsing
// the source for `difficulty:N` literals inside each function body).
function gensWithDiff() {
  const block = html.slice(html.indexOf('const GENERATORS = {'),
                            html.indexOf('const GENERATOR_KEYS'));
  // Walk the block, find each "  funcName(seed){" then look for the FIRST
  // "difficulty:N" occurrence inside that function.
  const out = {};
  const lines = block.split('\n');
  let cur = null;
  for (const line of lines) {
    const m = line.match(/^  ([a-zA-Z]\w*)\(seed\)\s*\{/);
    if (m) cur = m[1];
    if (cur) {
      const dm = line.match(/difficulty:\s*(\d+)/);
      if (dm) {
        if (!out[cur]) out[cur] = parseInt(dm[1], 10);
      }
    }
  }
  return out;
}
const gens = gensWithDiff();

// Pull GEN_MECHANIC and MECHANIC_LABEL from the source verbatim.
function evalConst(name) {
  const re = new RegExp(`const ${name} = (\\{[\\s\\S]*?\\});`);
  const m = html.match(re);
  return m ? eval('(' + m[1] + ')') : null;
}
const GEN_MECHANIC = evalConst('GEN_MECHANIC');

// Build MECH_BAND_INDEX exactly like the page does.
const MECH_BAND_INDEX = {};
for (const key of Object.keys(gens)) {
  const mech = GEN_MECHANIC[key];
  if (!mech) continue;
  if (!MECH_BAND_INDEX[mech]) MECH_BAND_INDEX[mech] = { 3: [], 4: [], 5: [] };
  MECH_BAND_INDEX[mech][gens[key]].push(key);
}

function pickGenForMechBand(mechanic, band) {
  const idx = MECH_BAND_INDEX[mechanic];
  if (!idx) return null;
  const sb = idx[band];
  return sb && sb.length ? sb[0] : null;
}
function findSimilarArchive(q, sourceYear, limit) {
  if (!q.mechanic) return [];
  limit = limit || 4;
  const out = [];
  const wantBand = q.points || 3;
  for (let i = ARCHIVE.length - 1; i >= 0; i--) {
    const t = ARCHIVE[i];
    for (const cand of t.questions) {
      if (t.year === sourceYear && cand.num === q.num) continue;
      if (cand.mechanic !== q.mechanic) continue;
      if ((cand.points || 3) !== wantBand) continue;
      out.push({ year: t.year, q: cand });
      if (out.length >= limit) return out;
    }
  }
  return out;
}
function pickPracticeFor(q, sourceYear) {
  if (q && q.mechanic) {
    const band = q.points || 3;
    const gen = pickGenForMechBand(q.mechanic, band);
    if (gen) return { kind: 'generator', gen };
    const items = findSimilarArchive(q, sourceYear, 4);
    if (items.length) return { kind: 'archive', items };
  }
  return { kind: 'fallback', gen: 'random' };
}

// Report routing per band.
function reportBand(band) {
  const summary = { generator: 0, archive: 0, fallback: 0, total: 0 };
  for (const t of ARCHIVE) {
    for (const q of t.questions) {
      if (q.points !== band) continue;
      summary.total++;
      const r = pickPracticeFor(q, t.year);
      summary[r.kind]++;
    }
  }
  return summary;
}
for (const b of [3, 4, 5]) {
  const s = reportBand(b);
  console.log(
    `${b}-point: ${s.total} questions → gen ${s.generator}, archive ${s.archive}, fallback ${s.fallback}`
  );
}
