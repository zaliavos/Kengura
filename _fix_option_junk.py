"""Clear option-letter debris left by PDF extraction (2026-10-10).

The extractor sometimes stored the tail of the answer row as an option
value: "D) E)" under C (45 questions), "1D) E)", "C) ♥♥". The UI then
showed a button "C  D) E)". This script

  1. empties every option value that is only letter-paren debris,
  2. applies hand fixes read off the figure PNGs (EXPECT must match),
  3. recomputes imageOnlyOptions / hasMissingOptionText,
  4. rewrites kengura-archive.json and kengura-archive.js.

Re-running is a no-op.
"""
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

DEBRIS_RE = re.compile(r'^\s*\d*\s*(\(?[A-E]\)\s*)+$')

# (year, num): {field: new_value} – checked against figures/{year}-q{num}.png
HAND = {
    ('2022', 28): {'options.C': 'Tarp B ir C'},
    ('2008', 24): {'options': {'A': '5 km', 'B': '8 km', 'C': '9 km', 'D': '12 km', 'E': '15 km'}},
    ('2023', 12): {
        'prompt': 'Pranciškus simboliais užrašė tris iš eilės einančius dviženklius skaičius: □◊, ♡△, ♡□. '
                  'Vienodi simboliai žymi tą patį skaitmenį, o skirtingi simboliai – skirtingus skaitmenis. '
                  'Koks skaičius eina iš eilės po ♡□?',
        'options': {'A': '□♡', 'B': '□□', 'C': '♡♡', 'D': '◊□', 'E': '♡◊'}},
    ('2017', 3): {
        'prompt': 'Vėjūnė turi keturias tokios formos figūrėles (žr. paveikslėlį). '
                  'Kurios figūros ji negali sudėti iš tų 4 figūrėlių?',
        'options': {k: '' for k in 'ABCDE'}},
    ('2020', 3): {'options': {k: '' for k in 'ABCDE'}},
}
# sanity: the stored answer must survive the hand fix
EXPECT_CORRECT = {('2022', 28): 'D', ('2008', 24): 'C', ('2023', 12): 'C', ('2017', 3): 'E', ('2020', 3): 'E'}

with open(ARCHIVE_JSON, encoding='utf-8') as f:
    data = json.load(f)

cleared = hand = 0
for y in data['archive']:
    for q in y['questions']:
        key = (y['year'], q['num'])
        opts = q.get('options') or {}
        for k, v in list(opts.items()):
            if v and DEBRIS_RE.match(v):
                opts[k] = ''
                cleared += 1
        if key in HAND:
            assert q.get('correct') == EXPECT_CORRECT[key], (key, q.get('correct'))
            for field, val in HAND[key].items():
                if field == 'options':
                    q['options'] = dict(val)
                elif field.startswith('options.'):
                    q['options'][field.split('.')[1]] = val
                else:
                    q[field] = val
            hand += 1
        opts = q.get('options') or {}
        empty = [k for k in 'ABCDE' if not (opts.get(k) or '').strip()]
        q.pop('imageOnlyOptions', None)
        q.pop('hasMissingOptionText', None)
        if len(empty) == 5:
            q['imageOnlyOptions'] = True
        elif empty:
            q['hasMissingOptionText'] = True

with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
    f.write('window.KENGURA_ARCHIVE = ')
    json.dump(data, f, ensure_ascii=False, separators=(', ', ': '))
    f.write(';')
print(f'cleared {cleared} debris values, {hand} hand fixes')
