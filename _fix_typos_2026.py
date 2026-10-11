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
]
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
Q = {f"{y['year']}-{q['num']}": q for y in data['archive'] for q in y['questions']}
n = 0
for k, f, wrong, right in FIX:
    t = Q[k].get(f) or ''
    pat = re.escape(wrong) if wrong.startswith(' ') else r'(?<![\wąčęėįšųūž])' + re.escape(wrong) + r'(?![\wąčęėįšųūž])'
    new = re.sub(pat, right, t, flags=re.I)
    if new != t: Q[k][f] = new; n += 1
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
print('fixed', n, 'of', len(FIX))
