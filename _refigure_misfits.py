"""Re-render figures that showed another question (2026-10-10).

Found by a duplicate-file check (2010-8, 2012-13, 2019-11, 2023-9 had
the figure of a neighbouring question) and by the kid-solution rewrite
(2022-25, 2023-23). Clips are in PDF points, located with
page.search_for() on the question's own wording. Needs PyMuPDF (fitz) –
run with plain `python`, not `python -I` (user site-packages).
2021-29/30 were split from one image instead (see git log, loop 51).
"""
import fitz, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = {  # key: (pdf, page (1-based), clip rect, zoom)
    ('2010', 8):  ('TMK10_lietuviu.pdf',     8, (58, 296, 478, 375), 2.7),
    ('2012', 13): ('TMK12_lietuviu (1).pdf', 10, (58, 510, 478, 573), 2.7),
    ('2019', 11): ('benjamin_lt (3).pdf',    2, (14, 212, 420, 272), 2.7),
    ('2023', 9):  ('benjamin_lt (10).pdf',   1, (428, 132, 830, 210), 2.7),
    ('2022', 25): ('benjamin_lt.pdf',        3, (14, 390, 585, 455), 2.0),
    ('2023', 23): ('benjamin_lt (10).pdf',   2, (8, 540, 422, 595), 2.7),
}
for (y, n), (pdf, pg, r, z) in CLIPS.items():
    fitz.open(os.path.join(HERE, pdf))[pg - 1].get_pixmap(clip=fitz.Rect(*r), matrix=fitz.Matrix(z, z)) \
        .save(os.path.join(HERE, 'figures', f'{y}-q{n}.png'))
J = os.path.join(HERE, 'kengura-archive.json'); JS = os.path.join(HERE, 'kengura-archive.js')
data = json.load(open(J, encoding='utf-8'))
Q = {(t['year'], q['num']): q for t in data['archive'] for q in t['questions']}
for (y, n) in CLIPS: Q[(y, n)]['figure'] = f'figures/{y}-q{n}.png'
Q[('2022', 25)]['prompt'] = ('Verneris pasirenka keturis skaičius iš penkių skaičių 2, 3, 4, 5, 6 ir įrašo po vieną '
                             'skaičių į kiekvieną langelį taip, kad lygybė □ + □ − □ = ■ būtų teisinga. '
                             'Keli iš duotų penkių skaičių tinka įrašyti į pilką langelį?')
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(JS, 'w', encoding='utf-8') as f:
    f.write('window.KENGURA_ARCHIVE = '); json.dump(data, f, ensure_ascii=False, separators=(', ', ': ')); f.write(';')
print('re-rendered', len(CLIPS))
