"""Apply KID_SOLUTIONS and MISCONCEPTIONS from _solutions_5pt_kid.py
to kengura-archive.json (and its .js mirror).

Adds two fields per 5-point archive question:
  q.solutionKid    — kid-Lithuanian rewrite of the official solution
  q.misconceptions — { wrongLetter: short reason }
"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _solutions_5pt_kid as data

ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

with open(ARCHIVE_JSON, encoding='utf-8') as f:
    archive = json.load(f)

n_sol = 0
n_misc = 0
for y in archive['archive']:
    for q in y['questions']:
        if q.get('points') != 5:
            continue
        key = (y['year'], q['num'])
        if key in data.KID_SOLUTIONS:
            q['solutionKid'] = data.KID_SOLUTIONS[key]
            n_sol += 1
        if key in data.MISCONCEPTIONS:
            # Filter to only WRONG letters (skip the correct one if mistakenly listed)
            misc = {k: v for k, v in data.MISCONCEPTIONS[key].items() if k != q.get('correct')}
            q['misconceptions'] = misc
            n_misc += 1

with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
    json.dump(archive, f, ensure_ascii=False, indent=1)
with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
    f.write('window.KENGURA_ARCHIVE = ')
    json.dump(archive, f, ensure_ascii=False)
    f.write(';\n')

print(f"Applied {n_sol} kid solutions and {n_misc} misconception sets.")
