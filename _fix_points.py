"""Point bands follow the question number (2026-10-11).

Every Bičiulis booklet prints "PO 3 TAŠKUS" before Q1 (B1), "PO 4 TAŠKUS"
before Q11 and "PO 5 TAŠKUS" before Q21 (checked in 2000LT, 2005LT, 2008LT,
TMK10, TMK12). The first build stored 2000-2012 entirely as 3-pointers and
2014-2017 Q23-30 as 3-pointers, so ~160 contest 5-pointers were treated as
warm-ups (band routing, race pool, contest maximum 90 instead of 120).
2006 is a Mažylis paper (see CLAUDE.md) and is left alone.
"""
import json, os, sys, io, subprocess, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
moved = collections.Counter()
for y in data['archive']:
    if y['year'] == '2006': continue
    for q in y['questions']:
        band = 3 if q['num'] <= 10 else 4 if q['num'] <= 20 else 5
        if q.get('points') != band:
            moved[(q.get('points'), band)] += 1
            q['points'] = band
print(dict(moved))
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
