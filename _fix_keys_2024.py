"""2024 answer keys: the answer table printed at the back of the official
solution booklet (spB (1).pdf, p. 19) disagrees with the same booklet's
worked solutions on 9 questions. Every one was re-checked by hand
(2026-10-11) and the worked solution is right each time:

  Q1  20·24 / (2·0+2·4) = 480/8 = 60            -> D (table B)
  Q2  "Renkamės atsakymą A" (view from behind)    -> A (table C)
  Q4  word PONIA in the secret alphabet: "C"      -> C (table D)
  Q5  "patikrinę atsakymą D ... jis tikrai tinka" -> D (table B)
  Q6  dog ate 1+1+1 = 3 biscuits                  -> E (table B)
  Q7  in the "0" the two diamonds fold together   -> A (table B; checked on the figure)
  Q8  3+1+1+2 = 7 cm                              -> B (table C)
  Q11 24-15 = 9 rhombi only, 15-9 = 6 squares     -> B (table E)
  (Q23/Q24 were fixed earlier in _fix_misfiled_2021_2024.py)
"""
import json, os, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
FIX = {1: 'D', 2: 'A', 4: 'C', 5: 'D', 6: 'E', 7: 'A', 8: 'B', 11: 'B'}
for y in data['archive']:
    if y['year'] != '2024': continue
    for q in y['questions']:
        if q['num'] in FIX and q['correct'] != FIX[q['num']]:
            print(f"2024-{q['num']}: {q['correct']} -> {FIX[q['num']]}")
            q['correct'] = FIX[q['num']]
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
