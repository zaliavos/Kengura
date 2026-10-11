"""Apply _clean_solutions.json: official solution texts cleaned by hand-
checked agents (2026-10-11) for the questions whose official text is what
the kid sees (no kid solution): figure labels pasted into sentences
removed, stacked fractions / powers rebuilt (1/4, 3², cm²), split words
joined. The ?/!/!! part markers are unchanged (verified per item).
Pipeline order: _reextract_solutions.py -> _fix_keys_audit.py -> this.
"""
import json, os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
fix = json.load(open(os.path.join(HERE, '_clean_solutions.json'), encoding='utf-8'))
# typos in the official texts themselves (checked against the question)
TYPOS = [
    ('2002-6', 'Pagaliau, vėrinyje D juodų širdelių yra 2/6', 'Pagaliau, vėrinyje E juodų širdelių yra 2/6'),
    ('2007-18', 'teiginys C visada teisingas', 'teiginys D visada teisingas'),
    ('2009-20', 'Jei į m neįeina 45', 'Jei į m neįeina 41'),
    ('2010-30', 'Šešiakojai ir aštunkojai', 'Šešiakojai ir aštuonkojai'),
    ('2010-30', 'vienodų atskymų', 'vienodų atsakymų'),
    ('2016-15', '258 + 1953 + 765 = 2975', '258 + 1953 + 764 = 2975'),
    ('2014-9', 'trečias ratas truko 32 minutes', 'trečias ratas truko 34 minutes'),
]
n = 0
for y in data['archive']:
    for q in y['questions']:
        k = f"{y['year']}-{q['num']}"
        if k in fix and q.get('solution') != fix[k]: q['solution'] = fix[k]; n += 1
Q = {f"{y['year']}-{q['num']}": q for y in data['archive'] for q in y['questions']}
for k, old, new in TYPOS:
    if new not in Q[k]['solution']:
        assert old in Q[k]['solution'], (k, old)
        Q[k]['solution'] = Q[k]['solution'].replace(old, new); n += 1
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
print('cleaned', n)
