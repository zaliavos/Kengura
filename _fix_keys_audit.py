"""Answer keys corrected by the 2026-10-11 audit of all 777 questions.

Run AFTER _reextract_solutions.py (it patches the official texts too).
Each change was checked by hand on the figure / by computation:

  2000-8   null -> B  two lengthwise loops 2·(30+10) + two crosswise 2·(10+10) = 240 cm
  2000-15  null -> C  B, D, E only lose corners (perimeter unchanged); C has mid-side notches
  2000-24  null -> B  hexagon (6+3)/2·3 = 13,5 minus rhombus 3·3/2 = 4,5 -> 9
  2001-10  null -> A  three 3×3 match squares give 8 squares; brute force: 2 matches reach 11
  2000-23  D -> E     the official text solves the 999-fold version; 1999 = 333·6 + 1 -> E
  2003-28  B -> A     □ = 6, △ = 7, ○ = 0 and the question asks □ + ○ = 6
  2005-24  D -> B     421, 463, 931, 962 – four numbers, and 4 is option B
  2009-24  D -> C     the official text finds the UNshaded 52; shaded = 100 − 52 = 48
  2010-4   C -> D     21 steps: the 10th from the bottom is the 12th from the top
  2011-10  A -> B     the official text itself ends with 60·7 + 80·7 = 980 g
(2014-11 was flagged by the audit but the key E is right: the 8 tiles hold
3 units of dark area and would need 4,5.)
"""
import json, os, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')
data = json.load(open(J, encoding='utf-8'))
Q = {(y['year'], q['num']): q for y in data['archive'] for q in y['questions']}

KEYS = {('2000', 8): 'B', ('2000', 15): 'C', ('2000', 24): 'B', ('2001', 10): 'A', ('2000', 23): 'E',
        ('2003', 28): 'A', ('2005', 24): 'B', ('2009', 24): 'C', ('2010', 4): 'D', ('2011', 10): 'B'}
SOL = {
    ('2000', 8): '2 m 40 cm ! Juosta apjuosia dėžę keturis kartus. Dvi juostos eina išilgai: viena aplink šonus, '
                 'kita per viršų, galus ir apačią – kiekviena po 2 · (30 + 10) = 80 cm. Dvi juostos eina skersai – '
                 'kiekviena po 2 · (10 + 10) = 40 cm. Iš viso 80 + 80 + 40 + 40 = 240 cm = 2 m 40 cm.',
    ('2000', 15): '! Jei iš stačiakampio kampo iškerpame stačiakampį, tvoros ilgis nepasikeičia: dvi nukirptos '
                  'atkarpos pakeičiamos dviem tokio pat ilgio atkarpomis. Todėl B, D ir E tvoros tokio pat ilgio kaip A. '
                  'C sklype įpjovos yra kraštinių viduryje: kiekviena įpjova prideda du savo gylius. '
                  'Taigi ilgiausia tvora – C.',
    ('2000', 24): '9 ! Šešiakampio plotis 6, aukštis 3, viršutinė ir apatinė kraštinės po 3. Jį sudaro 3 × 3 kvadratas '
                  'ir du trikampiai, kurių kiekvieno plotas 3 · 1,5 : 2 = 2,25. Šešiakampio plotas 9 + 4,5 = 13,5. '
                  'Baltojo rombo įstrižainės po 3, jo plotas 3 · 3 : 2 = 4,5. Užtušuota dalis: 13,5 − 4,5 = 9.',
    ('2001', 10): '2 ! Suskaičiuokime kvadratus dabar: trys dideli 3 × 3, du 2 × 2 (ten, kur dideli kvadratai persidengia) '
                  'ir trys maži 1 × 1 – iš viso 8. Pridėjus vieną degtuką naujų kvadratų atsiranda per mažai, '
                  'o dviem degtukais galima uždaryti tris naujus kvadratus, pavyzdžiui, du 1 × 1 ir vieną 2 × 2. '
                  'Taigi mažiausiai reikia 2 degtukų.',
}

def patch(key, old, new):
    q = Q[key]
    if new in q['solution']: return          # already patched (re-run)
    assert old in q['solution'], (key, old)
    q['solution'] = q['solution'].replace(old, new)

for k, v in KEYS.items():
    print(f'{k[0]}-{k[1]}: {Q[k].get("correct")} -> {v}'); Q[k]['correct'] = v
for k, v in SOL.items():
    Q[k]['solution'] = v
patch(('2000', 23), 'po 166 · 6 = 996 lenkimų turėsime padėtį A. Vadinasi, dar po 3 lenkimų gausime padėtį D.',
      'po 333 · 6 = 1998 lenkimų turėsime padėtį A. Vadinasi, dar po 1 lenkimo gausime padėtį E.')
patch(('2003', 28), 'Taigi x + z = 6.', 'Taigi x + z = 6: klausiama □ + ○ = 6 + 0 = 6.')
if Q[('2003', 28)]['solution'].startswith('7'): Q[('2003', 28)]['solution'] = '6' + Q[('2003', 28)]['solution'][1:]
patch(('2009', 24), 'taigi neužtušuotas plotas lygus 16 + 36 = 52 cm2.',
      'taigi neužtušuotas plotas lygus 16 + 36 = 52 cm2. Klausiama užtušuotos dalies: 100 − 52 = 48 cm2.')
Q[('2009', 24)]['solution'] = Q[('2009', 24)]['solution'].replace('52 cm2', '48 cm2', 1)
patch(('2010', 4), 'o Mikas buvo pastovėjęs ant 20 −10 = 10 laiptelių. Taigi Mikas dabar stovi ant 11 laiptelio',
      'o Mikas buvo pastovėjęs ant 21 − 10 = 11 laiptelių. Taigi Mikas dabar stovi ant 12 laiptelio')
if Q[('2010', 4)]['solution'].startswith('11'): Q[('2010', 4)]['solution'] = '12' + Q[('2010', 4)]['solution'][2:]
if Q[('2011', 10)]['solution'].startswith('840'): Q[('2011', 10)]['solution'] = '980' + Q[('2011', 10)]['solution'][3:]
for k in KEYS:   # the booklet's "Teisingas atsakymas X" follows the key
    import re
    Q[k]['solution'] = re.sub(r'((?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą)\s*[–-]?\s*)([A-E])(?=\.)',
                              lambda m: m.group(1) + KEYS[k], Q[k]['solution'])
json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
