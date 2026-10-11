"""Add the four questions the first build lost (2026-10-11):
2010, 2011, 2012 Q30 (last problem of the TMK booklets) and 2016 Q3
(its text had been merged into Q2). Text from the test booklets,
keys + solutions from the solution booklets (header letters), figures by
_recrop.py. Run with plain python (PyMuPDF), then _regen_js runs.
"""
import json, os, sys, subprocess
import fitz
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _reextract_solutions import ltnorm, segments, join_lines
import _recrop

NEW = {
    ('2010', 30): dict(mechanic='truth-tellers', patterns=['logika'], prompt=(
        'Vandenų valdovui tarnauja galvakojai – šešiakojai, septynkojai ir aštuonkojai. Septynkojai visada meluoja, '
        'o šešiakojai bei aštuonkojai visada sako tiesą. Susitiko sykį keturi įvairiaspalviai galvakojai. '
        'Mėlynasis sako: „Iš viso mes turime 28 kojas.“ Žaliasis sako: „Iš viso mes turime 27 kojas.“ '
        'Geltonasis sako: „Iš viso mes turime 26 kojas.“ Raudonasis sako: „Iš viso mes turime 25 kojas.“ '
        'Kuris galvakojis pasakė tiesą?'),
        options={'A': 'Raudonasis', 'B': 'Mėlynasis', 'C': 'Žaliasis', 'D': 'Geltonasis', 'E': 'Nė vienas'}),
    ('2011', 30): dict(mechanic='divisibility', patterns=['aritmetika'], prompt=(
        'Penkiaženklio skaičiaus skaitmenys yra 1, 2, 3, 4, 5 (tam tikra tvarka). Pirmas to skaičiaus skaitmuo '
        'dalijasi iš 1, pirmųjų dviejų skaitmenų sudarytas dviženklis skaičius dalijasi iš 2, pirmųjų trijų – iš 3, '
        'pirmųjų keturių – iš 4, o pats tas penkiaženklis skaičius dalijasi iš 5. Kiek yra tokių skaičių?'),
        options={'A': 'Nė vieno', 'B': '1', 'C': '2', 'D': '5', 'E': '10'}),
    ('2012', 30): dict(mechanic='logic-clues', patterns=['logika'], prompt=(
        'Aušra sugalvojo du gretimus natūraliuosius skaičius ir vieną jų pasakė Saulei, o kitą – Ryčiui. '
        'Saulė ir Rytis žino, kad jų skaičiai yra gretimi. Tada Saulė pasakė Ryčiui: „Aš nežinau tavo skaičiaus.“ '
        'Rytis Saulei atsakė: „Aš nežinau tavo skaičiaus.“ Tada Saulė pasakė Ryčiui: „Dabar aš žinau tavo skaičių, '
        'jis yra skaičiaus 20 daliklis.“ Koks Saulės skaičius?'),
        options={'A': '2', 'B': '3', 'C': '4', 'D': '5', 'E': '6'}),
    ('2016', 3): dict(mechanic='geometry-misc', patterns=['geometrija', 'paveikslelis'], prompt=(
        'Viela, kurios ilgis 10 cm, sulankstyta, kaip parodyta paveikslėlyje. Viela perkirpta dviejose '
        'pažymėtose vietose. Kokie gautų vielos atkarpų ilgiai?'),
        options={'A': '2 cm, 3 cm, 5 cm', 'B': '2 cm, 2 cm, 6 cm', 'C': '1 cm, 4 cm, 5 cm',
                 'D': '1 cm, 3 cm, 6 cm', 'E': '3 cm, 3 cm, 4 cm'}),
}
SOLPDF = {'2016': 'Solutions/spGDPRB.pdf'}

J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
for (yr, n), d in NEW.items():
    y = next(t for t in data['archive'] if t['year'] == yr)
    if any(q['num'] == n for q in y['questions']):
        print(yr, n, 'already there'); continue
    sol_pdf = y.get('solutions_pdf') or SOLPDF[yr]
    segs = segments(ltnorm('\n'.join(p.get_text() for p in fitz.open(os.path.join(HERE, sol_pdf)))))
    letter, body = segs[('B', n)]
    page, clip = _recrop.crop(y['test_pdf'], n, False, yr)
    page.get_pixmap(clip=clip, matrix=fitz.Matrix(_recrop.ZOOM, _recrop.ZOOM)).save(
        os.path.join(HERE, 'figures', f'{yr}-q{n}.png'))
    q = dict(num=n, prompt=d['prompt'], options=d['options'], points=3 if n <= 10 else 4 if n <= 20 else 5,
             patterns=d['patterns'], correct=letter, solution=join_lines(body),
             figure=f'figures/{yr}-q{n}.png', mechanic=d['mechanic'])
    y['questions'].append(q)
    y['questions'].sort(key=lambda q: q['num'])
    y['count'] = len(y['questions'])
    print(yr, n, 'added, key', letter)
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
