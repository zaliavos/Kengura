"""Spelling slips in archive texts found by a frequency scan (2026-10-11):
words seen once and one edit away from a common word, each read in
context; only unambiguous ones are listed. Run after
_apply_clean_solutions.py / _apply_kid_solutions.py (idempotent)."""
import json, os, re, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = [  # (key, field, wrong word, right word)
    ('2001-28', 'solution', 'žvaiždės', 'žvaigždės'),
    ('2004-19', 'solution', 'cketvirtadienį', 'ketvirtadienį'),
    ('2005-30', 'solution', 'salygos', 'sąlygos'),
    ('2008-24', 'solution', 'apseiti', 'apsieiti'),
    ('2011-9', 'solution', 'tetinka', 'netinka'),
    ('2012-26', 'solution', 'kvadratėlų', 'kvadratėlių'),
    ('2013-10', 'solution', 'trečiają', 'trečiąją'),
    ('2015-15', 'solution', 'tračiame', 'trečiame'),
    ('2015-23', 'solution', 'skaidinių', 'skardinių'),
    ('2015-28', 'solution', 'dešinąją', 'dešiniąją'),
    ('2017-12', 'solution', 'atitinką', 'atitinka'),
    ('2020-22', 'solution', 'dailių', 'dalių'),
    ('2020-30', 'solution', 'palies', 'dalies'),
    ('2021-13', 'solution', 'patebėkime', 'pastebėkime'),
    ('2022-12', 'solution', 'peiliui', 'paeiliui'),
    ('2022-28', 'solution', 'paeiti', 'praeiti'),
    ('2024-13', 'solution', 'stačiakamplio', 'stačiakampio'),
    ('2024-21', 'solution', 'galiausiais', 'galiausiai'),
    ('2024-27', 'prompt', 'kievienam', 'kiekvienam'),
    ('2013-24', 'solution', ' SPRENDIMAI', ''),
    # 2026-10-11 data scan (prompts confirmed from the figures)
    ('2002-10', 'prompt', 'skaičiųsu', 'skaičių su'),
    ('2010-10', 'prompt', 'jųsurišta', 'jų surišta'),
    ('2013-23', 'prompt', 'už sukusi', 'užsukusi'),
    ('2014-22', 'prompt', 'iš einant', 'išeinant'),
    ('2023-10', 'prompt', 'už rašytų', 'užrašytų'),
    ('2000-25', 'solution', 'atsakymąD', 'atsakymą D'),
    ('2003-22', 'solution', 'sąlygąir', 'sąlygą ir'),
    ('2005-23', 'solution', 'jąsudaro', 'ją sudaro'),
    ('2005-27', 'solution', 'vienąant', 'vieną ant'),
    ('2010-25', 'solution', 'tąpatį', 'tą patį'),
    ('2011-25', 'solution', 'likusiądalį', 'likusią dalį'),
    ('2013-27', 'solution', 'iš ties', 'išties'),
    ('2017-7', 'solution', 'todėl iš šeštasis', 'todėl ir šeštasis'),
    ('2010-27', 'solution', 'horizontailąją', 'horizontaliąją'),
    ('2018-13', 'solution', 'nedidesnis', 'ne didesnis'),
    ('2025-17', 'solution', 'nemažesnis', 'ne mažesnis'),
]
EXACT = [  # (key, field, old, new) – plain substring, figure debris inside a sentence
    ('2003-27', 'solution', 'kairėn-žemyn- M N 100 cm 100 cm 1 cm 1 cm dešinėn-žemyn', 'kairėn-žemyn-dešinėn-žemyn'),
    ('2023-25', 'solution', 'skai- 3/2 47/50 čius', 'skaičius'),
    ('2010-28', 'solution', ' 103 101..................... ', ' '),
    ('2001-14', 'solution', '8,...................... a n', '8, ..., a n'),
    ('2005-22', 'solution', 'nepavyksta. A B C D E Teisingas', 'nepavyksta. Teisingas'),
    ('2002-8', 'solution', 'sistemą– taisyklę', 'sistemą – taisyklę'),
    ('2005-23', 'solution', 'plotą– ', 'plotą – '),
    ('2001-1', 'prompt', '2×0+0×1', '2 × 0 + 0 × 1'),
]
UNIT_GLUE = {'2000-8', '2000-14', '2009-8', '2009-16', '2012-9', '2012-16'}   # "2m 40cm" → "2 m 40 cm" (as in the figures)
SUP_SKIP = {'2005-13', '2018-9'}   # "2 m 3 m" there is figure debris, not m³
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
Q = {f"{y['year']}-{q['num']}": q for y in data['archive'] for q in y['questions']}
n = 0
for k, f, wrong, right in FIX:
    t = Q[k].get(f) or ''
    pat = re.escape(wrong) if wrong.startswith(' ') else r'(?<![\wąčęėįšųūž])' + re.escape(wrong) + r'(?![\wąčęėįšųūž])'
    new = re.sub(pat, right, t, flags=re.I)
    if new != t: Q[k][f] = new; n += 1
# house style (grammar pass 3): a space before % – "20 %"
pct = re.compile(r'(\d)%')
for q in Q.values():
    for f in ('prompt', 'solution', 'solutionKid'):
        if q.get(f) and pct.search(q[f]): q[f] = pct.sub(lambda m: m.group(1) + ' %', q[f]); n += 1
    for L, v in list((q.get('options') or {}).items()):
        if v and pct.search(v): q['options'][L] = pct.sub(lambda m: m.group(1) + ' %', v); n += 1
# superscripts lost in extraction: cm2 / m3 → cm² / m³ (units or squared variables)
sup = re.compile(r'\b(c?m|dm|mm|km)([23])\b')
def _sup(t): return sup.sub(lambda m: m.group(1) + ('²' if m.group(2) == '2' else '³'), t)
for q in Q.values():
    for f in ('prompt', 'solution', 'solutionKid'):
        if q.get(f) and sup.search(q[f]): q[f] = _sup(q[f]); n += 1
    for L, v in list((q.get('options') or {}).items()):
        if v and sup.search(v): q['options'][L] = _sup(v); n += 1
for k, fld, old, new in EXACT:
    t = Q[k].get(fld) or ''
    if old in t: Q[k][fld] = t.replace(old, new); n += 1
glue = re.compile(r'(?<![\w.,])(\d+)(cm|m|kg|h|min)\b')
for k in UNIT_GLUE:
    q = Q[k]
    if glue.search(q.get('prompt') or ''): q['prompt'] = glue.sub(r'\1 \2', q['prompt']); n += 1
    for L, v in list((q.get('options') or {}).items()):
        if v and glue.search(v): q['options'][L] = glue.sub(r'\1 \2', v); n += 1
for q in Q.values():
    if q.get('prompt') and '––' in q['prompt']: q['prompt'] = re.sub(r'\s*––\s*', ' – ', q['prompt']); n += 1
# official solutions: page headers, figure labels, flattened symbols
HEADER = re.compile(r'\s*(?:BIČ ?IULIO UŽDUOČIŲ )?SPRENDIMAI(?: (?:BIČ ?IULIS|KADETAS) \([VI]+ ir [VI]+ klasės\))?|\s*KADETAS \(VII ir VIII klasės\)\s*$')
ANSWER = r'(?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą|atsakymas yra) [A-E]\.'
def short_run(t):
    t = re.sub(r'\.{3,}', ' ', t)
    return all(len(x) <= 3 or re.search('[þëðÞ]', x) for x in t.split())
TAIL = re.compile('(' + ANSWER + r')\s+((?:(?!' + ANSWER + r')[^!?])+)$')
MID = re.compile('(' + ANSWER + r')\s+((?:\S{1,3}\s+){1,40})(?=(?:!!?|\?\??)\s)')
SUP = re.compile(r'(?:(?<=\d )|(?<=\())(c?m|dm|mm) ([23])(?=[\s).,;:]|$)')
for k, q in Q.items():
    s = q.get('solution')
    if not s: continue
    t = HEADER.sub(' ', s).strip()
    t = re.sub(r'\s{2,}', ' ', t)
    m = TAIL.search(t)
    if m and short_run(m.group(2)): t = t[:m.start(2)].rstrip()
    t = MID.sub(lambda m: m.group(1) + ' ' if short_run(m.group(2)) else m.group(0), t)
    t = re.sub(r'(\d)\s?◦\s?(?=\w)', r'\1° ', t).replace('◦', '°')
    if k not in SUP_SKIP: t = SUP.sub(lambda m: m.group(1) + ('²' if m.group(2) == '2' else '³'), t)
    if t != s: q['solution'] = t; n += 1
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
print('fixed', n, 'of', len(FIX))
