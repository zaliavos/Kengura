"""Archive fixes found while rewriting the 5-point kid solutions (2026-10-10).

Each was checked against the figure PNG / official solution text:

  2021-10  held the second half of Q29's troll problem (and was marked
           5 points). The real Q10 is the 3-point "which square is 1/8 of
           the big square" question (figure + official solution agree, D).
  2021-29  prompt was cut off mid-sentence and the options were lost to
           Q10; restored from the figure (A 1 … E 7, key B = 3).
  2021-29/30  the figure 2021-q29.png held both problems and
           2021-q30.png showed another paper's problem – split by
           _pngrows (see the commit), q30 now shows the card puzzle.
  2022-25  the figure showed Q5; prompt boxes were lost in extraction.
           Text-only now (figure removed), prompt rewritten with □.
  2023-23  the figure showed the tail of Q15; text-only now, options are
           the letters themselves.
  2024-23  key A -> B: the official solution's description (left
           black-black, top white-black, bottom black-white, right
           white-black) is option B in the Lithuanian booklet's order.
  2024-24  key B -> A: the official solution text says 3 colours (A);
           option E held "7 4 5 6 7".
"""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json'); JS = os.path.join(HERE, 'kengura-archive.js')
data = json.load(open(J, encoding='utf-8'))
Q = {(y['year'], q['num']): q for y in data['archive'] for q in y['questions']}

q = Q[('2021', 10)]
q.update(points=3, correct='D', mechanic='area-compute',
         prompt='Kvadrato viduje buvo nubrėžtos kelios atkarpos. Atkarpomis sujungti jau esamų figūrų kampai '
                'arba kraštinių vidurio taškai. Algis nuspalvino 1/8 didžiojo kvadrato ploto. '
                'Kuris iš žemiau pavaizduotų kvadratų yra Algio nuspalvintasis?',
         options={k: '' for k in 'ABCDE'})
for k in ('solutionKid', 'misconceptions'): q.pop(k, None)

q = Q[('2021', 29)]
q.update(prompt='Varžybose dalyvavo keli troliai, kurie visada meluoja, ir keli elfai, kurie visada sako tiesą, '
                'iš viso 10 būtybių. Jie gavo po žetoną, ant kurių buvo užrašyti jų startiniai numeriai nuo 1 iki 10. '
                'Kiekvieno iš jų paklausė, koks skaičius užrašytas ant jo žetono. Visi pasakė natūraliuosius skaičius '
                'nuo 1 iki 10, o tų skaičių suma buvo 36. Kiek mažiausiai trolių galėjo dalyvauti varžybose?',
         options={'A': '1', 'B': '3', 'C': '4', 'D': '5', 'E': '7'})
assert q['correct'] == 'B'

q = Q[('2022', 25)]
assert q['correct'] == 'E'
q['prompt'] = ('Verneris pasirenka keturis skaičius iš penkių skaičių 2, 3, 4, 5, 6 ir įrašo po vieną skaičių '
               'į kiekvieną lygybės □ + □ − □ = ■ langelį taip, kad lygybė būtų teisinga. '
               'Kiek iš duotų penkių skaičių galima įrašyti į pilką langelį ■?')
q.pop('figure', None)

q = Q[('2023', 23)]
assert q['correct'] == 'C'
q['options'] = {k: k for k in 'ABCDE'}
q['prompt'] = ('Raidės A, B, C, D ir E žymi 5 skirtingus skaitmenis. Padauginus šešiaženklį skaičių 1ABCDE '
               'iš 3, gautas šešiaženklis skaičius ABCDE1. Kuri raidė žymi skaitmenį 8?')
q.pop('figure', None)

q = Q[('2024', 23)]; q['correct'] = 'B'
if (q.get('solution') or '').startswith('(A).'): q['solution'] = '(B).' + q['solution'][4:]
q = Q[('2024', 24)]; q['correct'] = 'A'; q['options']['E'] = '7'

for q in Q.values():
    empty = [k for k in 'ABCDE' if not (q.get('options') or {}).get(k, '').strip()]
    q.pop('imageOnlyOptions', None); q.pop('hasMissingOptionText', None)
    if len(empty) == 5: q['imageOnlyOptions'] = True
    elif empty: q['hasMissingOptionText'] = True

json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with open(JS, 'w', encoding='utf-8') as f:
    f.write('window.KENGURA_ARCHIVE = '); json.dump(data, f, ensure_ascii=False, separators=(', ', ': ')); f.write(';')
print('fixed')
