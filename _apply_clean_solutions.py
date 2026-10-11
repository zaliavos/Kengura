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
n = 0
for y in data['archive']:
    for q in y['questions']:
        k = f"{y['year']}-{q['num']}"
        if k in fix and q.get('solution') != fix[k]: q['solution'] = fix[k]; n += 1
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
print('cleaned', n)
