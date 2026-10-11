"""Apply _audit_text.json: prompts and options transcribed from the figures
(2026-10-11 audit of all 777 questions, one agent per 3-4 years, each
reading every figure PNG). Fixes the pdfplumber word-spacing damage
("pavei kslėlyje", "slaptąabėcėlę"), figure labels pasted into prompts,
prompts that held a neighbouring (or the Mažylis) question, lost fractions
("1", "1" for 1/2, 1/3) and junk option values. Pictured options stay "".
Recomputes imageOnlyOptions / hasMissingOptionText afterwards.
"""
import json, os, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
fix = json.load(open(os.path.join(HERE, '_audit_text.json'), encoding='utf-8'))
Q = {f"{y['year']}-{q['num']}": q for y in data['archive'] for q in y['questions']}
np = no = 0
for key, d in fix.items():
    q = Q[key]
    if 'prompt' in d and d['prompt'] != q.get('prompt'): q['prompt'] = d['prompt']; np += 1
    if 'options' in d and d['options'] != q.get('options'): q['options'] = dict(d['options']); no += 1
for q in Q.values():
    opts = q.get('options') or {}
    empty = [k for k in 'ABCDE' if not (opts.get(k) or '').strip()]
    q.pop('imageOnlyOptions', None); q.pop('hasMissingOptionText', None)
    if len(empty) == 5: q['imageOnlyOptions'] = True
    elif empty: q['hasMissingOptionText'] = True
print('prompts', np, 'options', no)
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
