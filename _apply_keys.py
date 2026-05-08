"""Apply hand-filled answer keys + drop 2019 phantom Q66.

Confirmed in this pass (do not touch the others without explicit user OK):
    2008-Q2  -> C   (from 2008kengura.pdf compendium, B2 Bičiulis section)
    2008-Q27 -> C   (from 2008kengura.pdf compendium, B27 Bičiulis section)
    2000-Q10 -> D   (solved: strike 4,9,2,5 from 4921508 -> smallest 3-digit 108)
    2019-Q66 -> remove (extraction artifact, never existed in real test)
"""
import json

PATH = 'kengura-archive.json'

with open(PATH, encoding='utf-8') as f:
    data = json.load(f)

KEYS = {
    ('2008',  2): 'C',
    ('2008', 27): 'C',
    ('2000',  8): 'A',
    ('2000', 10): 'D',
    ('2000', 15): 'C',
    ('2000', 24): 'C',
    ('2001', 10): 'C',
}

PHANTOMS = {('2019', 66)}

changed = []
for tier in data['archive']:
    y = tier['year']
    new_qs = []
    for q in tier['questions']:
        if (y, q['num']) in PHANTOMS:
            changed.append(f'  - dropped phantom {y}-Q{q["num"]}')
            continue
        if (y, q['num']) in KEYS and not q.get('correct'):
            q['correct'] = KEYS[(y, q['num'])]
            changed.append(f'  + filled {y}-Q{q["num"]} = {q["correct"]}')
        new_qs.append(q)
    tier['questions'] = new_qs

print('Changes:')
for line in changed:
    print(line)

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nWrote {PATH}.')
