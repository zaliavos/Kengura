"""Other-level practice sets (2026-11-22; Nykštukas and whole Mažylis papers 2026-11-23).

Builds kengura-levels.json / .js with three extra collections taken from the
official solution booklets on kengura.lt (levels_src/, see DOWNLOAD below):

  N  Nykštukas (1-2 kl.) – the whole paper (Q1-18)
  M  Mažylis (3-4 kl.)   – the whole paper (Q1-24)
  K  Kadetas (7-8 kl.)   – only the 3- and 4-point blocks (Q1-20)

The booklets ("spP" / "spE" / "spC") carry the conditions with a clean text layer,
the worked solutions headed "17. D", and the pictures. Prompt, options, key
and solution come from the text; the figure is cut from the conditions
pages with the layout logic of _recrop.py (the questions in STRICT with the
stricter _extra_crop.py), blank strips trimmed. Every worked solution is also
cut as a picture (figures/<id>-s<n>.png, solution_images) – drawings and the
little symbols inside the lines do not survive as text.

  python _extra_levels.py            # text + figures (about 15 minutes)
  python _extra_levels.py --dry      # text only into _levels_dry.json; nothing else is written
  python _extra_levels.py --nofig    # text only; keeps the solution pictures already cut
The build stops without writing anything if a question, key, figure or a hand
fix (PROMPT_SUB) is not found. levels_src/SOURCES.txt lists the booklets with
their sha256 (for the record – it is not read here); the test booklets
<year>-preecolier.pdf / -ecolier.pdf / -cadet.pdf in levels_src/ are not used
(except 2015-preecolier.pdf for one figure, see MANUAL_Q).
Paper ids are "M2024" / "K2024" (no "-": keys are "<id>-<num>").
"""
import fitz, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _recrop, _extra_crop
from _reextract_solutions import join_lines, drop_label_lines      # (importing it also makes stdout UTF-8)
SRC = os.path.join(HERE, 'levels_src')
FIGDIR = os.path.join(HERE, 'figures')

# DOWNLOAD: https://www.kengura.lt/uzduotys/<year>/spE.pdf, spC.pdf (2018+),
# spGDPRE/spGDPRC (2016-17), spGDPRM/spGDPRK (2014-15), TMK13_M/TMK13_K (2013)
# saved as levels_src/<year>-spE.pdf / <year>-spC.pdf; Nykštukas: spP.pdf (2018+), spGDPRP (2016-17),
# spGDPRN (2014-15), TMK13_N (2013) saved as <year>-spP.pdf.
LEVELS = {
    'N': dict(file='spP', name='Nykštukas', grades='1–2 kl.', nums=range(1, 19), total=18, band='3–5 t.',
              test='preecolier', sol13='N', sol14='N', sol16='P',
              points=lambda n: 3 if n <= 6 else 4 if n <= 12 else 5),
    'M': dict(file='spE', name='Mažylis', grades='3–4 kl.', nums=range(1, 25), total=24, band='3–5 t.',
              test='ecolier', sol13='M', sol14='M', sol16='E',
              points=lambda n: 3 if n <= 8 else 4 if n <= 16 else 5),
    'K': dict(file='spC', name='Kadetas', grades='7–8 kl.', nums=range(1, 21), total=30, band='3–4 t.',
              test='cadet', sol13='K', sol14='K', sol16='C',
              points=lambda n: 3 if n <= 10 else 4 if n <= 20 else 5),
}
YEARS = range(2013, 2027)
BASE = 'https://www.kengura.lt/uzduotys/'
def source_urls(L, year):
    """(test booklet, solution booklet) on kengura.lt – the names changed over the years."""
    c = LEVELS[L]
    test = f"{BASE}{year}/{c['test']}_lt.pdf"
    if year == 2013: sol = f"{BASE}TMK13_{c['sol13']}.pdf"
    elif year <= 2015: sol = f"{BASE}{year}/spGDPR{c['sol14']}.pdf"
    elif year <= 2017: sol = f"{BASE}{year}/spGDPR{c['sol16']}.pdf"
    else: sol = f"{BASE}{year}/sp{c['sol16']}.pdf"
    return test, sol

MARK_AFTER = {('z', 'ˇ'): 'ž', ('s', 'ˇ'): 'š', ('c', 'ˇ'): 'č', ('Z', 'ˇ'): 'Ž', ('S', 'ˇ'): 'Š', ('C', 'ˇ'): 'Č',
              ('a', '˛'): 'ą', ('e', '˛'): 'ę', ('i', '˛'): 'į', ('u', '˛'): 'ų',
              ('A', '˛'): 'Ą', ('E', '˛'): 'Ę', ('I', '˛'): 'Į', ('U', '˛'): 'Ų'}
MARK_BEFORE = {('˙', 'e'): 'ė', ('˙', 'E'): 'Ė', ('¯', 'u'): 'ū', ('¯', 'U'): 'Ū',
               ('ˇ', 'z'): 'ž', ('ˇ', 's'): 'š', ('ˇ', 'c'): 'č', ('ˇ', 'Z'): 'Ž', ('ˇ', 'S'): 'Š', ('ˇ', 'C'): 'Č'}
def norm(t):
    """The TeX booklets set ė/ū as accent + letter and š/ž/ą as letter + accent."""
    t = re.sub(r'([˙¯ˇ])\s?([A-Za-z])', lambda m: MARK_BEFORE.get((m.group(1), m.group(2)), m.group(0)), t)
    t = re.sub(r'([A-Za-z])\s?([ˇ˛])', lambda m: MARK_AFTER.get((m.group(1), m.group(2)), m.group(0)), t)
    t = re.sub(r'([eEuU])\s?([˙¯])', lambda m: {'e˙': 'ė', 'E˙': 'Ė', 'u¯': 'ū', 'U¯': 'Ū'}.get(m.group(1) + m.group(2), m.group(0)), t)
    t = t.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
    t = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\uf000-\uf8ff]', '', t)
    return unicodedata.normalize('NFC', t)

SMALL_TOKEN = re.compile(r'^[0-9a-zA-Z+−\-,.·()]{1,7}$')
def _frac_part(spans):
    t = ''.join(x['t'] for x in sorted(spans, key=lambda x: x['r'].x0)).strip()
    t = re.sub(r'\s+', ' ', t)
    return '(' + t + ')' if re.search(r'[+−\-·× :]', t) else t

DEC = '\u201a'        # stands for a decimal comma until tidy() (a plain comma gets a space after it on the way)
def page_text_fr(page):
    """_pagetext.page_text plus: fractions found by their BAR (a thin
    horizontal rule with text right above and right under it – the booklets
    set many fractions at nearly body size, which the size test misses), and
    raised small digits after a number or letter as "^n"."""
    d = page.get_text('dict')
    sizes = {}
    for b in d['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if s['text'].strip(): sizes[round(s['size'], 1)] = sizes.get(round(s['size'], 1), 0) + len(s['text'])
    if not sizes: return page.get_text()
    body = max(sizes, key=sizes.get)
    blocks, spans = [], []
    for b in d['blocks']:
        if b['type'] != 0: continue
        lines = []
        for l in b['lines']:
            L = dict(bbox=fitz.Rect(l['bbox']), items=[], spans=[])
            for s in l['spans']:
                if not s['text'].strip(): continue
                sp = dict(L=L, r=fitz.Rect(s['bbox']), t=s['text'], size=s['size'], used=False, font=s['font'])
                L['spans'].append(sp); spans.append(sp)
            for i, sp in enumerate(L['spans']):
                if sp['t'].strip() == ',' and 'Math' in sp['font'] and 0 < i < len(L['spans']) - 1:
                    a, b = L['spans'][i - 1], L['spans'][i + 1]
                    if re.search(r'\d$', a['t']) and re.match(r'\d', b['t']) and abs(sp['r'].x0 - a['r'].x1) < 0.6 and abs(b['r'].x0 - sp['r'].x1) < 0.6 \
                            and abs(a['size'] - b['size']) < 0.5:
                        sp['t'] = DEC
            lines.append(L)
        blocks.append(lines)
    all_lines = [L for lines in blocks for L in lines]
    bars = []
    for dr in page.get_drawings():
        r = fitz.Rect(dr['rect'])
        if r.height < 1.5 and 3 < r.width < 160: bars.append(r)
    fracs = []
    for bar in sorted(bars, key=lambda r: (r.y0, r.x0)):
        y = (bar.y0 + bar.y1) / 2
        inside = lambda sp: sp['r'].x0 >= bar.x0 - 2.5 and sp['r'].x1 <= bar.x1 + 2.5 and not sp['used']
        num = [sp for sp in spans if inside(sp) and abs(sp['r'].y1 - y) <= 3.2 and sp['r'].y0 < y - 4]
        den = [sp for sp in spans if inside(sp) and abs(sp['r'].y0 - y) <= 3.2 and sp['r'].y1 > y + 4]
        if not num or not den: continue
        for sp in num + den: sp['used'] = True
        fracs.append((bar, y, _frac_part(num) + '/' + _frac_part(den)))
    def host_for(y, x, need_free=True):
        c = [L for L in all_lines if L['bbox'].y0 - 1 <= y <= L['bbox'].y1 + 1
             and (not need_free or any(not sp['used'] for sp in L['spans']))]
        if not c: return None
        return min(c, key=lambda L: 0 if L['bbox'].x0 - 3 <= x <= L['bbox'].x1 + 3
                   else min(abs(x - L['bbox'].x0), abs(x - L['bbox'].x1)))
    extra = []       # fractions with no text line at their height: lines of their own
    for bar, y, tok in fracs:
        h = host_for(y, bar.x0)
        if h is None:
            h = dict(bbox=fitz.Rect(bar.x0, y - 5, bar.x1, y + 5), items=[], spans=[]); extra.append(h); all_lines.append(h)
        h['items'].append((bar.x0, ' ' + tok + ' '))
    for sp in spans:
        if sp['used']: continue
        L, t = sp['L'], sp['t']
        small = sp['size'] < body * 0.85 and SMALL_TOKEN.match(t.strip())
        if small:
            prev = [(x, tx) for x, tx in L['items'] if x < sp['r'].x0 and tx.strip()]
            before = [x for x in L['spans'] if x is not sp and x['t'].strip() and x['r'].x1 <= sp['r'].x0 + 1.5 and x['size'] >= body * 0.85]
            if before:
                ps = max(before, key=lambda x: x['r'].x1)['r']
                raised = sp['r'].y1 < ps.y1 - 2.5 and sp['r'].y0 < ps.y0 + 3 and sp['r'].x0 - ps.x1 < 4
            else:
                raised = sp['r'].y1 < L['bbox'].y1 - 2.5 and sp['r'].y0 <= L['bbox'].y0 + 1.5
            if prev and raised and sp['size'] < body * 0.8:
                last = max(prev)[1]
                if t.strip() in ('2', '3') and re.search(r'(^|[\s\d])(cm|m|dm|mm|km)\s*$', last):
                    L['items'].append((sp['r'].x0, '²' if t.strip() == '2' else '³')); continue
                # after a number, a bracket or a one-letter variable – not after a word (a footnote mark)
                if re.search(r'([0-9)]|(^|[^A-Za-zÀ-ž])[A-Za-z])$', last.strip()) and re.fullmatch(r'[0-9a-zA-Z+−\-]{1,5}', t.strip()):
                    L['items'].append((sp['r'].x0, '^' + t.strip())); continue
        L['items'].append((sp['r'].x0, t if not small else ' ' + t.strip() + ' '))
    # re-insert the space spans' effect: join items of a line with single spaces where the PDF had gaps
    out = []
    for lines in blocks + [[e] for e in extra]:
        texts = []
        for L in lines:
            its = sorted(L['items'], key=lambda it: it[0])
            t = ' '.join(x.strip() if x.startswith(('^', '²', '³')) else x for _, x in its)
            t = re.sub(r' (\^|²|³)', r'\1', t)
            t = re.sub(r'  +', ' ', t).strip()
            if t: texts.append(t)
        if texts: out.append('\n'.join(texts))
    return '\n'.join(out) + '\n'

def sections(doc):
    """(conditions pages, solutions pages) of a single-level solution booklet."""
    cond0 = sol0 = end = None
    for pno, page in enumerate(doc):
        t = norm(page.get_text())
        head = t.strip()[:160].upper()
        lines = [l.strip() for l in t.split('\n') if l.strip()]
        if pno < 3 or 'TURINYS' in head: continue
        if cond0 is None and re.search(r'(?m)^1\.\s', t) and re.search(r'(?m)^\s*A\)', t) and not re.search(r'(?m)^1\. [A-E]\s*$', t): cond0 = pno
        if cond0 is not None and sol0 is None and re.search(r'(?m)^1\. [A-E]\s*$', t): sol0 = pno
        if sol0 is not None and end is None and pno > sol0 and lines and \
                any(re.fullmatch(r'ATSAKYMAI', l.upper()) for l in lines[:3]): end = pno
    return range(cond0, sol0), range(sol0, end if end else len(doc))

OPT = re.compile(r'(?m)^\s*([A-E])\)[ \t]*')
def parse_conditions(text, total):
    """{num: (prompt, {A..E})} – questions run 1..total in order."""
    text = re.sub(r'(?mi)^\s*(SĄLYGOS|\d{1,3}|Klausimai po \d taškus?|Nykštukas.*|Mažylis.*|Kadetas.*|KENGŪRA.*)\s*$', '', text)
    pos, out = 0, {}
    marks = []
    for n in range(1, total + 1):
        m = re.compile(r'(?m)^%d\.\s' % n).search(text, pos)
        if not m: marks.append(None); continue
        marks.append(m); pos = m.end()
    for i, m in enumerate(marks):
        if not m: continue
        nxt = next((x for x in marks[i + 1:] if x), None)
        seg = text[m.end(): nxt.start() if nxt else len(text)]
        # all five options set on ONE line ("A) Raudona B) Mėlyna …"): one per line
        seg = re.sub(r'(?m)^[ \t]*A\) .*$', lambda mm: re.sub(r'[ \t]+(?=[B-E]\) )', chr(10), mm.group(0))
                     if all((' %s) ' % c) in mm.group(0) for c in 'BCDE') else mm.group(0), seg)
        # options: the LAST run A) … E) of the segment
        om = list(OPT.finditer(seg))
        start = None
        for j in range(len(om) - 1, -1, -1):
            if om[j].group(1) == 'A': start = j; break
        opts = {}
        if start is not None:
            run = om[start:]
            for k, o in enumerate(run):
                end = run[k + 1].start() if k + 1 < len(run) else len(seg)
                ls = [l.strip() for l in seg[o.end():end].split('\n') if l.strip()]
                # an option is one line; more only when a long sentence wraps
                # (anything else under it is lettering of a picture)
                keep = ls[:1]
                for l in ls[1:]:
                    if len(keep[-1]) > 45 and re.search(r'[a-ząčęėįšųūž]{3}', l): keep.append(l)
                    else: break
                opts[o.group(1)] = ' '.join(keep)
            prompt = seg[:run[0].start()]
        else:
            prompt = seg
        prompt = join_lines(prompt)
        # lettering of the picture that the text layer puts after the question
        m2 = re.match(r'^(.*\?)([^?]*)$', prompt, re.S)
        if m2 and m2.group(2).strip() and not re.search(r'[a-ząčęėįšųūž]{4}', m2.group(2)): prompt = m2.group(1)
        vals = [v for v in opts.values() if v]
        if len(vals) == 1 and len(vals[0]) < 12: opts = {k: '' for k in opts}   # lettering of one option's picture
        if len(set(vals)) < len(vals): opts = {k: '' for k in opts}       # equal texts: the difference is in the picture
        out[i + 1] = (prompt, opts)
    return out

# Keys where the booklet's header AND its answer table are wrong; the worked
# solution decides (checked by hand against the figure, 2026-11-22):
#   M2024-20: triangle 7, circle 4, square 1 -> product 28 = D (printed: C)
KEY_FIX = {('M2024', 20): 'D'}
# the solution first walks into the trap on purpose ("?? … Renkamės atsakymą E") – its letters stay
KEEP_TEXT_LETTERS = {('N2017', 14)}
# The key letter is right but the VALUE printed beside it is a slip of the booklet
# (M2016-21: "21. B 1914" – 1914 is an option of question 22). The header line is left
# out of the solution picture and the value out of the text.
HEAD_HIDE = {('M2016', 21), ('K2021', 7),
             ('N2014', 2), ('N2015', 3), ('M2015', 3)}      # N2014-2: option B's value; N2015-3: "14" for 19; M2015-3: "16" for 6       # K2021-7: "7. B 138137" for 13837
# the value in the text layer is damaged (a framed number plate) – the picture shows it right
TEXT_HEAD_DROP = {('K2022', 4)}
# solution texts that are unreadable without their little pictures: picture only
SOLUTION_TEXT_DROP = {('M2024', 20), ('M2015', 5), ('N2024', 7),
    # overlined numbers, big brackets, systems and inline pictures that the text layer turns into
    # something false or empty (found by re-reading every text against its picture)
    ('M2014', 22), ('M2017', 17), ('M2017', 18), ('M2023', 20),
    ('K2015', 15), ('K2016', 5), ('K2016', 8), ('K2018', 17), ('K2018', 18), ('K2019', 11), ('K2020', 13),
    ('K2021', 5), ('K2021', 7), ('K2023', 17), ('K2025', 17), ('K2026', 5), ('K2026', 14)}
# solutions whose every "d, d" is a decimal the span test missed (digits and comma in one span)
SOLUTION_DECIMALS = {('K2013', 8), ('K2015', 3), ('K2015', 12), ('K2015', 16), ('K2019', 18), ('K2021', 14), ('K2024', 18)}
# (old, new) in a solution text; the build fails if "old" is not there
SOLUTION_SUB = {('K2019', 20): ('Tokiu atveju teisingas atsakymas C.', 'Tokiu atveju teisingas atsakymas B.'),   # the remark is about the OTHER reading
                ('K2024', 19): ('674, 666...', '674,666...'),
                ('K2024', 9): (' ab/cd 8 ', ' '), ('K2025', 13): ('(žr. pirmą pav.). a b c ', '(žr. pirmą pav.). ')}
# Text the layer cannot give (checked against the figures, 2026-11-22):
PROMPT_FIX = {   # a price table whose rules were read as fraction bars
    ('M2014', 21): 'Dėdei Jonui parduotuvėje patiko 5 žaislai, kurių kainas matome žemiau. Jis išsirinko tris iš jų, '
                   'užmokėjo 200 litų banknotu ir gavo 18 litų grąžos. Staiga jis persigalvojo ir vieną iš žaislų pakeitė kitu, '
                   'o tada gavo dar 25 litus grąžos. Kuriuos žaislus galop nusipirko dėdė Jonas? '
                   'Kainos: sviedinys – 40 Lt, lėlė – 73 Lt, meškiukas – 52 Lt, dėlionė – 48 Lt, šachmatai – 57 Lt.',
    # captions of the two drawings were set into the sentence
    ('M2018', 19): 'Pavaizduotą juostelę galima susegti į žiedą penkiais būdais – susegus pirmoje skylutėje, antroje, trečioje, '
                   'ketvirtoje, penktoje skylutėje. (Paveikslėlyje: nesusegta juostelė, tarp gretimų skylučių – 2 cm, ir pirmoje '
                   'skylutėje susegta juostelė.) Kiek ilgesnė juostelė, susegta pirmoje skylutėje, už juostelę, susegtą penktoje skylutėje?'}
PROMPT_FIX.update({
    # the weights are printed on the boxes: the text layer gave them in another order (2, 6, 5, 7, 16)
    ('M2021', 22): 'Į kiekvieną iš penkių dėžių sudėti arba tik obuoliai, arba tik bananai. Dėžės sveria: 1-oji – 7 kg, '
                   '2-oji – 5 kg, 3-ioji – 6 kg, 4-oji – 2 kg, 5-oji – 16 kg. Visi bananai sveria tris kartus daugiau nei visi '
                   'obuoliai. Į kurias dėžes sudėti obuoliai?',
    # the note itself is a picture
    ('M2025', 23): 'Markas užrašė, kiek kokių penkių rūšių vaisių jis turi. Iš viso tai 106 vaisiai. Nelaimei, dalis užrašo '
                   'sutepta – matyti tik paskutiniai skaitmenys: mangai …2, obuoliai …0, kriaušės …1, bananai …3, o slyvų – 30. '
                   'Dviejų rūšių vaisių yra tiek pat. Vienos rūšies vaisių yra dvigubai daugiau nei kitos, o kiekvienos rūšies '
                   'vaisių yra daugiau nei 10. Kiek bananų turi Markas?',
    ('M2014', 22): 'Įrašykite kiekvieną iš skaičių 0, 1, 2, 3, 4, 5, 6 į kvadratėlius □□ + □□ = □□□ taip, kad sudėtis būtų atlikta '
                   'teisingai. Koks skaitmuo bus pilkajame (paskutiniame) kvadratėlyje?',
    ('M2016', 21): 'Jorė turi trijų rūšių trinkeles: △, ○, □. Skirtingų trinkelių svoris skirtingas, tos pačios rūšies trinkelių '
                   'svoris vienodas. Jorė į tris vienodas dėžutes sudėjo po keturias trinkeles. Tada dėžutes ji išrikiavo pagal svorį '
                   'nuo lengviausios iki sunkiausios (paveikslėlyje iš kairės į dešinę): □△○△, △□□□, ○□△□. Kuri iš trinkelių '
                   'sunkiausia, o kuri lengviausia?',
    ('M2018', 20): 'Senovinėje kalboje penki simboliai (žr. paveikslėlį) atitinka skaitmenis 1, 2, 3, 4 ir 5, tik nepasakyta, kuris '
                   'simbolis atitinka kurį skaitmenį. Buvo nustatytos trys lygybės (jos parodytos paveikslėlyje). Kuris simbolis atitinka skaitmenį 3?',
    ('M2019', 17): 'Vienodos figūrėlės reiškia vienodus skaičius. Kiekvienos eilutės trijų skaičių suma nurodyta tos eilutės dešinėje. '
                   'Kokį skaičių reiškia žvaigždutė ★?',
    ('M2021', 17): 'Luknė turi penkis lipdukus: trikampį, skritulį, žvaigždę, gėlę ir obuolį. Ji suklijavo lipdukus po vieną į penkis '
                   'langelius (1, 2, 3, 4, 5) taip, kad žvaigždė nėra 5-ame langelyje, obuolys yra 1-ame langelyje, o gėlė yra greta '
                   'skritulio ir greta trikampio. Į kurį langelį Luknė įklijavo gėlę?',
    ('M2021', 24): 'Kajus į trejų svarstyklių lėkštes sudėjo šešiakampius, kvadratus ir trikampius (žr. paveikslėlį). Ką jam reikia '
                   'įdėti į trečiųjų svarstyklių kairiąją lėkštę, kad svarstyklės būtų pusiausviros?',
    ('M2023', 22): 'Evaldas turi du įrenginius R ir S. Įrenginys R įdėtą kortelę pasuka ketvirtadaliu pilno apsisukimo, kaip tai parodyta '
                   'pirmame paveikslėlyje. Įrenginys S įdėtoje kortelėje atspausdina ženklą ♣. Kokia tvarka Evaldas pasinaudojo savo '
                   'įrenginiais, jeigu įdėjęs kortelę, pavaizduotą kairėje, gavo kortelę, pavaizduotą dešinėje?',
    ('M2024', 18): 'Ieva tris skirtingas figūras pasvėrė po dvi, rezultatai parodyti paveikslėlyje: 200 g, 100 g ir 240 g. '
                   'Kiek tos trys figūros sveria kartu?',
    ('M2024', 20): 'Paveikslėlyje vienodos figūros slepia vienodus skaitmenis, skirtingos figūros – skirtingus skaitmenis: '
                   '△ + △ = ■●, ● + △ = ■■. Kam lygi sandauga △ × ● × ■?',
    ('M2024', 24): 'Stasys turi dviejų rūšių detales: baltas ir pilkas (žr. paveikslėlį). Mažą kubelį galima sudėti arba iš keturių '
                   'baltųjų detalių, arba iš vienos baltosios ir vienos pilkosios. Iš mažųjų kubelių Stasys sudėjo didelį kubą '
                   '(žr. paveikslėlį). Kiek mažiausiai jam reikėjo baltųjų detalių?',
    ('K2024', 7): 'Ant stalo gulėjo penki skanėstai: obuolys, vynuogės, vyšnios, braškė ir bananas. Elena mėgsta obuolį. Ema mėgsta '
                  'obuolį, vyšnias, braškę ir bananą. Austėja mėgsta vynuoges, vyšnias, braškę ir bananą. Gerda mėgsta obuolį, vynuoges '
                  'ir vyšnias. Adomas mėgsta obuolį ir vyšnias. Kiekvienas vaikas gavo tokį skanėstą, kokį mėgsta. Kas gavo vyšnias?',
    ('K2026', 6): 'Dominykas į kiekvieną išraiškos (□ + □)/(□ − □) langelį įrašė po vieną šiuos keturis skaičius: 2, 0, 2 ir 6. Tada jis '
                  'suskaičiavo gautos trupmenos reikšmę. Kokią mažiausią teigiamą reikšmę galėjo gauti Dominykas?',
})
PROMPT_FIX.update({
    ('M2024', 10): 'Ant padėklo buvo penki vaisiai: obuolys, vyšnia, kriaušė, braškė ir bananas. Emilija mėgsta kriaušę, braškę ir bananą, '
                   'Jonas mėgsta kriaušę, Lukas mėgsta visus penkis vaisius, Agnė mėgsta kriaušę ir bananą, Liepa mėgsta vyšnią ir braškę. '
                   'Kiekvienas vaikas gavo po mėgiamą vaisių. Ką gavo Lukas?',
})
PROMPT_SUB = {('M2019', 9): (' Fr/q|r', ''),       # a piece of the drawing read as text
              ('K2019', 20): (' 2/(2 1 0 3)', ''),      # numbers of the grid read as a fraction
              ('K2021', 7): (' CD/137 CBAD/?', ''),       # the addition on the blackboard read as fractions
              ('K2015', 3): ('2, 015 × 510, 2', '2,015 × 510,2'),
              ('K2022', 7): ('Diagramoje pavaizduoti penki tušti langeliai.', 'Lygybėje 6 □ 9 □ 12 □ 15 □ 18 □ 21 = 45 yra penki tušti langeliai.'),
              ('K2020', 11): ('Paveiklėlyje', 'Paveikslėlyje'),   # the booklet's hyphenation slip      # math-mode decimals
              ('K2024', 12): (' 2 2 2 1 3 1 3 1 2,', ' (žr. paveikslėlį),')}     # the three pieces are pictures
# prompts / option sets re-typed from the figures by the review of 2026-11-23 (all Nykštukas, Mažylis 1–16):
# {'N2013-8': {'prompt': …, 'options': {A..E} or {} = the options are pictures}}
# Child-language solutions for Nykstukas and Mazylis (2026-11-24): written from the figures by agents,
# reviewed, kept in _levels_kid.json {"N2013-1": "Gudrybe: ... Atsakymas: D) 6 ir 9."}; shown before the booklet page.
_kid_path = os.path.join(HERE, '_levels_kid.json')
KID = json.load(open(_kid_path, encoding='utf-8')) if os.path.exists(_kid_path) else {}
# "Your mistake" notes per wrong option {"N2013-2": {"A": "4 - tiek knygu vaikai paeme, ..."}} (same day)
_misc_path = os.path.join(HERE, '_levels_misc.json')
MISC = json.load(open(_misc_path, encoding='utf-8')) if os.path.exists(_misc_path) else {}
TEXT_FIX = json.load(open(os.path.join(HERE, '_levels_text_fix.json'), encoding='utf-8'))
for _k, _v in TEXT_FIX.items():
    if 'prompt' in _v: PROMPT_FIX[(_k.split('-')[0], int(_k.split('-')[1]))] = _v['prompt']
PROMPT_CUT_TAIL = {('M2016', 24), ('K2015', 19)}      # lettering of the picture after the question mark
OPTION_FIX = {
              # the shapes are little pictures in the booklet
              ('M2016', 21): {'A': 'Lengviausia △, sunkiausia □', 'B': 'Lengviausia △, sunkiausia ○', 'C': 'Lengviausia □, sunkiausia ○',
                              'D': 'Lengviausia ○, sunkiausia □', 'E': 'Lengviausia ○, sunkiausia △'},
              # number plates drawn in frames: digits of the frame were lost / read as exponents
              ('K2022', 4): {'A': '04 NSN 40', 'B': '60 HOH 09', 'C': '80 BNB 08', 'D': '03 HNH 30', 'E': '08 XBX 80'},
              ('K2021', 13): {'A': '3 cm²', 'B': '7/2 cm²', 'C': '4 cm²', 'D': '11/2 cm²', 'E': '6 cm²'},      # unit after a fraction
              ('K2021', 18): {'A': '5 cm', 'B': '5,5 cm', 'C': '6 cm', 'D': '6,5 cm', 'E': '4√2 cm'}}         # the radical is a drawing
OPTION_BLANK = {('K2024', 12),                         # the options are pieces of a table (pictures)
                # compound fractions, mixed numbers, powers, rows of symbols: unreadable as typed text
                ('K2015', 1), ('K2015', 12), ('K2017', 4), ('K2019', 3), ('K2020', 4), ('K2023', 12)}
# figures the layout check flagged: cut with the stricter _extra_crop.py
STRICT = set('''M2013-21 M2013-22 M2014-21 M2014-22 M2015-19 M2017-17 M2021-18 M2021-19 M2024-21 M2024-24
K2013-1 K2013-2 K2013-11 K2013-12 K2013-15 K2013-16 K2014-2 K2014-3 K2014-4 K2014-15 K2014-16 K2015-6 K2015-7
K2016-9 K2016-10 K2017-5 K2017-6 K2017-9 K2017-17 K2017-18 K2018-1 K2018-2 K2018-4 K2018-5 K2018-6 K2018-11
K2018-12 K2018-13 K2018-14 K2018-15 K2021-2 K2021-3 K2021-7 K2022-13 K2023-1 K2023-3 K2023-4 K2024-3 K2024-4
K2025-6 K2025-7 K2025-19 K2026-5 K2026-6 M2021-23
M2014-11 M2014-8 M2015-3 M2016-13 M2016-7 M2017-10 M2018-3 M2019-4 M2022-5 M2024-1 M2025-1 N2016-16 N2017-16 N2021-1 N2021-16 N2022-16 N2026-17 N2013-7 N2014-11 N2023-11 N2023-12
M2017-8
N2013-14 N2015-5 N2016-9 N2016-10 N2017-8 N2018-3 N2018-4 N2020-1 N2020-2 N2020-13 N2022-6 N2022-9 N2022-10 N2024-8 M2016-4 M2016-5 M2017-1 M2018-2 M2018-12 M2019-1 M2019-2 M2020-7 N2014-9 N2019-7 N2021-12 N2024-14 M2014-5 N2017-12 M2017-16
M2024-9 M2013-15'''.split())

# Question figures cut by hand (page index in the booklet, rectangle in pt, rectangles to paint white):
# a drawing that stands beside the neighbour's text, which neither cropper can assign.
MANUAL_Q = {
    'N2022-6': dict(page=5, clip=(50, 678, 556, 757)),
    'N2022-9': dict(page=6, clip=(50, 303, 556, 366), masks=[(480, 356, 560, 420)]),
    'N2022-10': dict(page=6, clip=(40, 356, 556, 432), masks=[(40, 356, 495, 385)]),
    'N2024-8': dict(page=6, clip=(50, 236, 556, 357), masks=[(282, 353.4, 300, 360), (300, 352, 376, 360)]),
    'M2016-5': dict(page=8, clip=(50, 582, 558, 713)),
    'M2017-1': dict(page=8, clip=(50, 143, 558, 205)),
    'M2017-2': dict(page=8, clip=(50, 206, 558, 244)),
    'M2019-1': dict(page=5, clip=(50, 152, 440, 200)),
    'M2019-2': dict(page=5, clip=(50, 176, 558, 273.5), masks=[(50, 176, 440, 204)]),
    'M2014-5': dict(page=8, clip=(50, 492, 560, 606)),
    # the solution booklet prints a broken drawing here: the question comes from the test booklet
    'N2015-6': dict(pdf='2015-preecolier.pdf', page=1, clip=(14, 466, 412, 576)),
}
def manual_cut(qid, doc):
    """Cut a MANUAL_Q figure; True if qid is one."""
    m = MANUAL_Q.get(qid)
    if not m: return False
    d = fitz.open(os.path.join(SRC, m['pdf'])) if m.get('pdf') else doc
    out = os.path.join(FIGDIR, qid.replace('-', '-q') + '.png')
    _extra_crop.render(d[m['page']], fitz.Rect(m['clip']), [fitz.Rect(r) for r in m.get('masks', [])], out)
    trim_png(out)
    return True

SOL_ZOOM = 2.0
def ink_groups(page, cell=4):
    """Rectangles of ink that is NOT text: figures placed as embedded pictures (form
    XObjects) are invisible to get_drawings(), so they are found on the rendered page.
    The page is rendered at 1 pt/px, the words are blanked, and the remaining dark
    cells (cell × cell pt) are grouped by flood fill."""
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1), colorspace=fitz.csGRAY, alpha=False)
    W, H = pix.width, pix.height
    buf = bytearray(pix.samples)
    for w in page.get_text('words'):
        x0, y0, x1, y1 = max(0, int(w[0]) - 1), max(0, int(w[1]) - 1), min(W, int(w[2]) + 2), min(H, int(w[3]) + 2)
        for yy in range(y0, y1): buf[yy * W + x0: yy * W + x1] = b'\xff' * (x1 - x0)
    gw, gh = W // cell + 1, H // cell + 1
    dark = set()
    for yy in range(H):
        row = buf[yy * W:(yy + 1) * W]
        if min(row) > 170: continue
        for xx in range(W):
            if row[xx] <= 170: dark.add((xx // cell, yy // cell))
    out = []
    while dark:
        seed = dark.pop(); stack = [seed]; x0 = x1 = seed[0]; y0 = y1 = seed[1]
        while stack:
            cx, cy = stack.pop()
            x0 = min(x0, cx); x1 = max(x1, cx); y0 = min(y0, cy); y1 = max(y1, cy)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (cx + dx, cy + dy)
                    if nb in dark: dark.discard(nb); stack.append(nb)
        out.append(fitz.Rect(x0 * cell, y0 * cell, (x1 + 1) * cell, (y1 + 1) * cell))
    return out

def _blank_rows(im):
    g = im.convert('L')
    W = g.size[0]
    px = g.tobytes()
    H = g.size[1]
    return [min(px[y * W:(y + 1) * W]) > 245 for y in range(H)]

def trim_sheet(im):
    """Cut the blank rows that drop_edge_bits leaves at the top and the bottom."""
    blank = _blank_rows(im)
    a = 0
    while a < len(blank) - 1 and blank[a]: a += 1
    b = len(blank)
    while b > a + 1 and blank[b - 1]: b -= 1
    a = max(0, a - 8); b = min(len(blank), b + 6)
    return im if (a == 0 and b == len(blank)) else im.crop((0, a, im.size[0], b))

def squeeze_blank(im, keep=40, limit=80):
    """Blank bands taller than `limit` px (page ends, display gaps) shrink to `keep`."""
    blank = _blank_rows(im)
    H = len(blank); rows = []; y = 0
    while y < H:
        if blank[y]:
            e = y
            while e < H and blank[e]: e += 1
            n = e - y
            rows += list(range(y, y + (keep if n > limit else n)))
            y = e
        else: rows.append(y); y += 1
    if len(rows) == H: return im
    from PIL import Image
    out = Image.new(im.mode, (im.size[0], len(rows)), 255 if im.mode == 'L' else (255, 255, 255))
    # copy runs of consecutive rows
    i = 0; dy = 0
    while i < len(rows):
        j = i
        while j + 1 < len(rows) and rows[j + 1] == rows[j] + 1: j += 1
        out.paste(im.crop((0, rows[i], im.size[0], rows[j] + 1)), (0, dy)); dy += j - i + 1; i = j + 1
    return out

def trim_png(path, margin=10):
    """Cut blank strips above and under a question figure (the gap to the next question)."""
    from PIL import Image
    im = Image.open(path); im.load()
    blank = _blank_rows(im)
    ink = [y for y, b in enumerate(blank) if not b]
    if not ink: return
    a, b = max(0, ink[0] - margin), min(len(blank), ink[-1] + 1 + margin)
    if a > 0 or b < len(blank): im.crop((0, a, im.size[0], b)).save(path, optimize=True)
# Where the automatic cut between two solutions goes wrong (an answer drawing that starts far above
# its header line, the booklet's own stray mark): the y (pt, on the header's page) where solution n starts …
SOL_START = {('N2017', 9): 72, ('N2022', 8): 356, ('M2013', 9): 348, ('M2015', 4): 403, ('M2015', 5): 553.2}
# … and (page index, y) where solution n ends
SOL_END = {('N2026', 10): (12, 326), ('M2015', 4): (12, 558.3)}
# (page index, x0, y0, x1, y1) painted white in the picture of solution n
SOL_MASK = {('N2023', 13): [(10, 440, 240, 560, 301)],      # the last row of solution 12's table
            ('M2015', 4): [(12, 60, 552.5, 200, 559)],        # the circle round the next key
            ('N2016', 5): [(13, 0, 0, 600, 40.8)],            # running head right above the second maze
            # the booklet's last line "Teisingas atsakymas X." names a letter that contradicts its own header and argument
            ('N2015', 5): [(13, 91.5, 344.9, 212.0, 358.9)],     # says E, key B
            ('M2014', 24): [(28, 91.5, 716.5, 217.4, 730.5)],    # says C, key D
            ('M2016', 10): [(14, 91.5, 301.2, 218.0, 315.2)],    # says D, key B
            ('M2016', 17): [(17, 91.5, 229.6, 217.8, 243.6)],    # says A, key D
            ('M2024', 2): [(9, 91.5, 416.1, 216.5, 430.1)]}      # says E, key A

def drop_edge_bits(im, max_h=46):
    """White out small ink pieces that touch the top or bottom edge of a solution picture
    (a page number cut in half, the foot of a neighbour's drawing). Pieces taller than max_h px stay."""
    W, H = im.size
    px = im.load()
    dark = lambda x, y: px[x, y] < 150
    seen = set()
    for y0 in list(range(0, min(3, H))) + list(range(max(0, H - 3), H)):
        for x0 in range(W):
            if (x0, y0) in seen or not dark(x0, y0): continue
            comp, stack = [], [(x0, y0)]; seen.add((x0, y0))
            lo, hi = y0, y0
            while stack and len(comp) < 60000:
                x, y = stack.pop(); comp.append((x, y)); lo = min(lo, y); hi = max(hi, y)
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        q = (x + dx, y + dy)
                        if 0 <= q[0] < W and 0 <= q[1] < H and q not in seen and dark(*q): seen.add(q); stack.append(q)
            if hi - lo < max_h and not stack:
                xs = [c[0] for c in comp]
                if y0 < 3 and min(xs) < 0.4 * W: continue        # top left is the header line (its circle may touch the edge)
                im.paste(255, (max(0, min(xs) - 3), max(0, lo - 3), min(W, max(xs) + 4), min(H, hi + 4)))
    return im

def solution_images(doc, sol, nums, prefix, nohead=()):
    """Cut every worked solution as a picture (figures/<id>-s<n>.png): the
    text layer loses the drawings and the little symbols set inside the
    lines. A solution runs from its "n. X" header to the next one, over page
    breaks; the pieces are stacked."""
    from PIL import Image
    import io as _io
    groups = {}
    def page_groups(pp):
        """Connected groups of drawings / images of a page (the figures of the solutions)."""
        if pp not in groups:
            page = doc[pp]
            raw = [fitz.Rect(dr['rect']) for dr in page.get_drawings()]
            for img in page.get_images(full=True): raw += [fitz.Rect(r) for r in page.get_image_rects(img[0])]
            raw = [r + (-0.4, -0.4, 0.4, 0.4) for r in raw if not (r.height < 2 and r.width > 150) and r.height < page.rect.height * 0.6]
            raw += [r for r in ink_groups(page) if r.height < page.rect.height * 0.6 and not (r.height <= 8 and r.width > 150)]
            groups[pp] = [c for c in _extra_crop._merge(raw, 3) if c.height >= 12]
        return groups[pp]
    marks = []            # (page, y, n) in reading order
    tall = {}             # n -> rect of an answer picture that starts above its header line
    want = 1
    for p in sol:
        page = doc[p]
        lines = {}
        for w in page.get_text('words'): lines.setdefault((w[5], w[6]), []).append(w)
        heads = []
        for ws in lines.values():
            ws.sort(key=lambda w: w[0])
            if len(ws) >= 2 and re.fullmatch(r'\d{1,2}\.', ws[0][4]) and re.fullmatch(r'[A-E]', ws[1][4]) and ws[0][0] < 120:
                heads.append((ws[0][1], int(ws[0][4][:-1]), ws[1][2], ws[0][3]))
        draws = None
        for y, n, hx, hy1 in sorted(heads):
            if n != want: continue
            # A picture printed as the answer's value (cubes, a grid, a cup) stands taller than
            # the header line and reaches up beside the end of the previous solution. It is one
            # connected group of drawings touching the header line right of the key letter: the
            # whole group goes to this solution and is painted out of the previous one (`tall`).
            if draws is None:
                draws = [fitz.Rect(dr['rect']) for dr in page.get_drawings()]
                for img in page.get_images(full=True): draws += [fitz.Rect(r) for r in page.get_image_rects(img[0])]
            near = [r + (-0.4, -0.4, 0.4, 0.4) for r in draws if r.x1 > hx and r.x0 < 360 and r.y1 > y - 170 and r.y0 < hy1 + 6
                    and r.height < 170 and r.width < 320 and not (r.height < 2 and r.width > 150)]
            band = fitz.Rect(hx + 1, y, 400, hy1)
            wanted = n in nums or (n - 1) in nums          # our own header, or the end of a solution we cut
            cand = [c for c in (page_groups(p) if wanted else []) + _extra_crop._merge(near if wanted else [], 2)
                    if c.height < 170 and c.width < 330 and c.x0 > hx - 14 and c.x0 < 400 and c.y1 > y - 170 and c.y0 < hy1 + 6]
            hit = [c for c in cand if c.intersects(band)]
            if hit:
                T = hit[0]
                for c in hit[1:]: T = T | c
                inside = lambda c: c.x0 >= T.x0 - 0.01 and c.y0 >= T.y0 - 0.01 and c.x1 <= T.x1 + 0.01 and c.y1 <= T.y1 + 0.01
                for _ in range(len(cand) + 1):            # each pass adds at least one group or stops
                    more = [c for c in cand if not inside(c) and (T + (-7, -7, 7, 7)).intersects(c) and c.y0 < hy1 and (T | c).height < 175]
                    if not more: break
                    T = T | more[0]
                # a drawing's rectangle can be larger than its ink (clipped hatching): it never
                # reaches into the sentences of the previous solution
                above = [w[3] for ws in lines.values() for w in ws if (w[1] + w[3]) / 2 < y - 3 and w[3] > T.y0
                         and w[2] > T.x0 and w[0] < T.x1 and re.search(r'[A-Za-ząčęėįšųūžĄČĘĖĮŠŲŪŽ]{3,}', w[4])]
                if above: T = fitz.Rect(T.x0, max(above) + 2.5, T.x1, T.y1)     # + the 2 pt the cut starts above T
                if T.y0 < y - 3: tall[n] = T
            # the header LINE starts where its tallest text starts: the circle round the key
            # letter and the numerator of an answer like (60·50)/(8·70) stand above the number
            ytop = y
            for ws in lines.values():
                for w in ws:
                    if w[0] > hx - 14 and w[1] < hy1 - 2 and w[3] > y + 1 and y - 26 < w[1] < ytop: ytop = w[1]
            for r in near:
                if r.height < 30 and r.width < 60 and r.x0 < hx + 6 and r.y0 < hy1 and r.y1 > y and r.y0 < ytop: ytop = r.y0   # the circle
            marks.append((p, ytop, n)); want += 1
    def content(page):
        H = page.rect.height
        rs = []
        lines = {}
        heads_y = []
        figs = [r for r in ink_groups(page) if r.height >= 20 and r.width >= 20]
        for w in page.get_text('words'): lines.setdefault((w[5], w[6]), []).append(w)
        for ws in lines.values():
            t = norm(' '.join(w[4] for w in ws)).strip()       # the text layer sets accents apart: "UZˇDUOCˇIU˛"
            y0 = min(w[1] for w in ws)
            # running head / page number: a line of capital WORDS ("N = 6, A = 8" is part of a solution)
            if (y0 < 110 or y0 > H - 130) and (re.fullmatch(r'\d{1,3}', t) or re.fullmatch(r'(?=(?:.*[A-ZĄČĘĖĮŠŲŪŽ]){6})[A-ZĄČĘĖĮŠŲŪŽ0-9 ]+', t)):
                box = fitz.Rect(min(w[0] for w in ws), y0, max(w[2] for w in ws), max(w[3] for w in ws))
                if not any((f + (-14, -14, 14, 14)).intersects(box) for f in figs):      # a number beside a figure is its label
                    heads_y.append(box.y1); continue
            rs += [fitz.Rect(w[:4]) for w in ws]
        for dr in page.get_drawings():
            r = fitz.Rect(dr['rect'])
            if r.width > page.rect.width * 0.7 and r.height < 3: continue
            if r.height < 3 and r.width > 60 and any(-4 < r.y0 - hy < 14 for hy in heads_y): continue      # the rule under a running head
            if r.height > H * 0.8: continue
            rs.append(r)
        for img in page.get_images(full=True): rs += [fitz.Rect(r) for r in page.get_image_rects(img[0])]
        # figures placed as embedded pictures (their lettering included) are only visible as ink
        for r in ink_groups(page):
            if r.height > H * 0.6 or (r.height <= 8 and r.width > 150): continue
            if r.height <= 8 and r.width > 60 and any(-6 < r.y0 - hy < 16 for hy in heads_y): continue
            if (r.y0 < 40 or r.y1 > H - 40) and r.height < 30: continue      # crop marks / page furniture (a figure may reach the foot)
            rs.append(r)
        return rs
    out = {}
    cache = {}
    def hanging(pp, yline, skip):
        """Figures of the solution ABOVE the header line at `yline` that hang down past it
        (a drawing set to the right of the text is often taller than the text)."""
        return [c for c in page_groups(pp) if c.y0 < yline - 8 and c.y1 > yline - 2 and c.height < 420
                and not (skip and (skip + (-2, -2, 2, 2)).intersects(c))]
    marks = [(p, SOL_START.get((prefix, n), y), n) for p, y, n in marks]
    for i, (p, y, n) in enumerate(marks):
        if n not in nums: continue
        end = marks[i + 1] if i + 1 < len(marks) else (sol[-1], doc[sol[-1]].rect.height, None)
        if (prefix, n) in SOL_END: end = SOL_END[(prefix, n)] + (None,)
        pieces = []
        for pp in range(p, end[0] + 1):
            page = doc[pp]
            if pp not in cache: cache[pp] = content(page)
            a = (y + 18 if n in nohead else y - 2.5) if pp == p else 0     # nohead: the printed key is wrong
            b = end[1] - 2 if pp == end[0] else page.rect.height
            paint = [fitz.Rect(r[1:]) for r in SOL_MASK.get((prefix, n), []) if r[0] == pp]
            words = cache.setdefault(('w', pp), [fitz.Rect(w[:4]) for w in page.get_text('words')])
            if pp == end[0] and end[2] is not None:
                last = [w.y1 for w in words if a <= (w.y0 + w.y1) / 2 < end[1] - 2 and w.y1 > b - 3]
                if last: b = max(b, max(last) + 1.5)
            if pp == p and n not in nohead:
                prev = [w.y1 for w in words if (w.y0 + w.y1) / 2 < y - 2 and w.y1 > a]
                if prev: a = max(prev) + 0.5
            T = tall.get(n) if pp == p and n not in nohead else None
            if T: a = min(a, T.y0 - 2)
            rs = [r for r in cache[pp] if r.y1 > a + 1 and r.y0 < b - 1 and (r.y0 + r.y1) / 2 >= a and (r.y0 + r.y1) / 2 < b]
            if T:      # what lies above our header line and is not the picture belongs to the previous solution
                mine = lambda r: (r.y0 + r.y1) / 2 >= y - 3 or (T + (-2, -2, 2, 2)).intersects(r)
                paint += [w for w in words if (w.y0 + w.y1) / 2 < y - 3 and w.y1 > a and not (T + (-1, -1, 1, 1)).contains(w)]
                rs = [r for r in rs if mine(r)]
            E = tall.get(end[2]) if pp == end[0] and end[2] is not None else None
            if E:
                paint.append(E + (-1, -1, 1, 1))
                rs = [r for r in rs if not (E + (-1, -1, 1, 1)).contains(r)]
            if pp == end[0] and end[2] is not None:
                # our own figure hanging past the next header: keep it whole, paint the next solution's start out of it
                low = [c for c in hanging(pp, end[1], E) if pp != p or c.y0 > y - 3]
                if low:
                    b2 = max(c.y1 for c in low) + 2
                    ours = lambda r: (r.y0 + r.y1) / 2 < end[1] - 2 or any((c + (-2, -2, 2, 2)).contains(r) or (r.width < 16 and r.height < 16 and (c + (-12, -12, 12, 12)).contains(r)) for c in low)
                    more = [r for r in cache[pp] if b - 1 <= (r.y0 + r.y1) / 2 < b2 + 14 or (r.y0 < b2 and r.y1 > b)]     # + labels under the figure
                    paint += [r for r in more if not ours(r)]
                    rs += [c for c in low] + [r for r in more if ours(r)]
                    b = max(b2, max([r.y1 for r in more if ours(r)] + [b2]) + 2.5)
            if pp == p and n not in nohead:
                # … and the previous solution's figure hanging into ours is painted out (never over our words)
                for c in hanging(pp, y, T):
                    own = [r for r in rs if (r.y0 + r.y1) / 2 >= y - 3 and r.width < 200 and (c + (-1, -1, 1, 1)).intersects(r) and not (c + (-2, -2, 2, 2)).contains(r)]
                    if not own: paint.append(c + (-1, -1, 1, 1)); rs = [r for r in rs if not (c + (-2, -2, 2, 2)).contains(r)]
            if not rs: continue
            clip = fitz.Rect(min(r.x0 for r in rs) - 6, max(a, min(r.y0 for r in rs) - 4), max(r.x1 for r in rs) + 6, min(b, max(r.y1 for r in rs) + 2.5)) & page.rect
            if clip.height < 4: continue
            pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(SOL_ZOOM, SOL_ZOOM), alpha=False)
            for r in paint:
                r = (r + (-0.5, -0.5, 0.5, 0.5)) & clip
                if not r.is_empty:
                    pix.set_rect(fitz.IRect(int(r.x0 * SOL_ZOOM), int(r.y0 * SOL_ZOOM), int(r.x1 * SOL_ZOOM) + 1, int(r.y1 * SOL_ZOOM) + 1), (255, 255, 255))
            pieces.append((Image.open(_io.BytesIO(pix.tobytes('png'))).convert('L'), clip.x0))
        if not pieces: continue
        x_min = min(x for _, x in pieces)
        off = lambda x: int(round((x - x_min) * SOL_ZOOM))
        W = max(off(x) + im.size[0] for im, x in pieces)
        sheet = Image.new('L', (W, sum(im.size[1] for im, _ in pieces)), 255)
        yy = 0
        for im, x in pieces: sheet.paste(im, (off(x), yy)); yy += im.size[1]
        before = sheet.tobytes()
        sheet = drop_edge_bits(sheet)
        sheet = trim_sheet(squeeze_blank(sheet)) if sheet.tobytes() != before else squeeze_blank(sheet)
        name = f'{prefix}-s{n}.png'
        sheet.save(os.path.join(FIGDIR, name), optimize=True)
        out[n] = 'figures/' + name
    solution_images.tall = getattr(solution_images, 'tall', []) + [f'{prefix}-s{k}' for k in tall if k in nums]
    return out

def tidy(t, solution=False):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'(?<=\d) ?' + DEC + r' ?(?=\d)', ',', t).replace(DEC, ',')
    t = re.sub(r'(\d) ?(cm|m|dm|mm|km) ?([23])(?=[\s.,;)?]|$)', lambda m: f"{m.group(1)} {m.group(2)}{'²' if m.group(3) == '2' else '³'}", t)
    t = re.sub(r'̸ ?=', '≠', t).replace('⩽', '≤').replace('⩾', '≥')
    t = re.sub(r'(\d) °', r'\1°', t.replace('◦', '°'))
    t = re.sub(r'(\d) , (\d)', r'\1,\2', t)                    # "2 , 015" – math-mode decimals
    if not solution:
        t = re.sub(r'(?<=[^\s?]) \?(?=\s|$)', '?', t)            # "kampas δ ?"
        t = re.sub(r'((?:[a-ząčęėįšųūž]{2,}|[,(:=]) )− (?=\d)', r'\1−', t)     # "gavo − 14", "− 5, − 3": a sign, not a subtraction
    t = re.sub(r'\b([01]?\d|2[0-4]): ([0-5]\d)\b', r'\1:\2', t)   # "17: 00" (a clock time only – not "lygi 51: 20 + 10")
    t = re.sub(r'\bt\.y\.', 't. y.', t)
    t = re.sub(r'(\d)%', r'\1 %', t)                            # "30%" → "30 %"
    t = t.replace('): (', ') : (')
    return t.replace('∗', '*')

def build(with_figs=True):
    out = {'levels': {}}
    report = []
    for L, cfg in LEVELS.items():
        papers = []
        for year in YEARS:
            pdf = os.path.join(SRC, f"{year}-{cfg['file']}.pdf")
            if not os.path.exists(pdf): report.append(f'{L}{year}: no solution booklet – skipped'); continue
            doc = fitz.open(pdf)
            cond, sol = sections(doc)
            ctext = norm('\n'.join(page_text_fr(doc[p]) for p in cond))
            stext = norm('\n'.join(page_text_fr(doc[p]) for p in sol))
            conds = parse_conditions(ctext, cfg['total'])
            segs = {}
            # "7. A" alone, or with the answer's value after it ("1. A (2+0)/(1+5)");
            # numbers must come in order (a "3. B" inside a solution is no header)
            hs, want = [], 1
            for x in re.finditer(r'(?m)^(\d{1,2})\. ([A-E])(?=[ \t]*$|[ \t]+\S)', stext):
                if int(x.group(1)) == want: hs.append(x); want += 1
            for i, x in enumerate(hs):
                n = int(x.group(1))
                body = stext[x.end(): hs[i + 1].start() if i + 1 < len(hs) else len(stext)]
                segs[n] = (x.group(2), body)
            qs = []
            for n in cfg['nums']:
                if n not in conds: report.append(f'{L}{year}-{n}: condition not found'); continue
                prompt, opts = conds[n]
                letter, body = segs.get(n, (None, ''))
                solution = tidy(join_lines(drop_label_lines(body)), solution=True) if body else ''
                # running heads of the booklet pages and a lone sign left at the end
                solution = re.sub(r'\s*\b(?:(?:NYKŠTUKO|MAŽYLIO|KADETO) )?(?:UŽDUOČIŲ )?SPRENDIMAI\b', '', solution)
                solution = re.sub(r'\s+[−–-]$', '', solution).strip()
                # lettering of the solution's drawings (runs of 4+ single letters / digits) says nothing as text
                solution = re.sub(r'(?:(?<=\s)|^)(?:[A-Za-zα-ωΑ-Ω0-9′]\s+){3,}[A-Za-zα-ωΑ-Ω0-9′](?=[\s.,;:)]|$)', '', solution)
                solution = re.sub(r'\s{2,}', ' ', solution).strip()
                m3 = re.match(r'^(.*[.!?:])\s+([^.!?:]{1,40})$', solution, re.S)
                if m3 and not re.search(r'[A-Za-ząčęėįšųūžĄČĘĖĮŠŲŪŽ]{3,}', m3.group(2)) and not re.search(r'\d{2,}', m3.group(2)): solution = m3.group(1)
                # "92. ! …": the answer value of a sentence-completion question keeps its full stop
                solution = re.sub(r'^([^!?]{1,40}?)\.(?=\s+(?:\?\??|!!?)\s)', r'\1', solution)
                letter = KEY_FIX.get((f'{L}{year}', n), letter)
                if (f'{L}{year}', n) in SOLUTION_DECIMALS: solution = re.sub(r'(\d), (?=\d)', r'\1,', solution)
                if (f'{L}{year}', n) in SOLUTION_TEXT_DROP: solution = ''
                if (f'{L}{year}', n) in HEAD_HIDE or (f'{L}{year}', n) in TEXT_HEAD_DROP: solution = re.sub(r'^[^!?]{0,40}?(?=(?:\?\??|!!?)\s)', '', solution)
                for mm in re.finditer(r'(?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą)\s*[–-]?\s*([A-E])(?=[ .]|$)', solution):
                    if letter and mm.group(1) != letter: report.append(f'{L}{year}-{n}: text says {mm.group(1)}, header says {letter}')
                if letter and (f'{L}{year}', n) not in KEEP_TEXT_LETTERS:   # booklet slips like "Teisingas atsakymas C" under a solution of D
                    solution = re.sub(r'((?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą)\s*[–-]?\s*)([A-E])(?=[ .]|$)',
                                      lambda m: m.group(1) + letter, solution)
                if (f'{L}{year}', n) in SOLUTION_SUB:
                    old, new = SOLUTION_SUB[(f'{L}{year}', n)]
                    if old not in solution: report.append(f'{L}{year}-{n}: SOLUTION_SUB (PROMPT_SUB kind) text not found')
                    solution = solution.replace(old, new)
                opts = {k: re.sub(r'^− (?=\d)', '−', tidy(v)) for k, v in opts.items()}
                pid = (f'{L}{year}', n)
                prompt = PROMPT_FIX.get(pid, prompt)
                if pid in PROMPT_SUB:
                    old, new = PROMPT_SUB[pid]
                    if old not in prompt: report.append(f'{L}{year}-{n}: PROMPT_SUB text not found')
                    prompt = prompt.replace(old, new)
                if pid == ('K2021', 14): prompt = re.sub(r'[?][\s.…?]*$', '?', prompt.strip())      # the "…" and "?" of the drawing
                if pid in PROMPT_CUT_TAIL: prompt = prompt[:prompt.rindex('?') + 1]
                if pid in OPTION_FIX: opts = dict(OPTION_FIX[pid])
                if pid in OPTION_BLANK: opts = {}
                _tf = TEXT_FIX.get(f'{pid[0]}-{pid[1]}', {})
                if 'options' in _tf: opts = dict(_tf['options']); blank_ok = True
                else: blank_ok = False
                # "17. B" with the value missing leaves the letter in front of the text
                if letter and re.match(r'^%s (?=[!?])' % letter, solution) and opts.get(letter) != letter: solution = solution[2:]
                prompt = tidy(prompt)
                if pid not in PROMPT_FIX:
                    # a little picture set inside the sentence leaves "tokias korteles:." / ":,,." – point to the figure
                    prompt = re.sub(r':[, ]*[.]', ' (žr. paveikslėlį).', prompt)
                    prompt = re.sub(r'[?](?: [?])+$', '?', prompt)        # question marks drawn in the picture
                q = {'num': n, 'prompt': prompt, 'options': {k: opts.get(k, '') for k in 'ABCDE'},
                     'points': cfg['points'](n), 'correct': letter, 'solution': solution,
                     'figure': f'figures/{L}{year}-q{n}.png', 'level': L}
                empty = [k for k in 'ABCDE' if not q['options'][k]]
                if len(empty) == 5: q['imageOnlyOptions'] = True
                elif empty: q['hasMissingOptionText'] = True
                if len(opts) != 5 and pid not in OPTION_BLANK and not blank_ok: report.append(f'{L}{year}-{n}: {len(opts)} options parsed')
                if not letter: report.append(f'{L}{year}-{n}: no key')
                if len(q['prompt']) < 25: report.append(f"{L}{year}-{n}: short prompt {q['prompt']!r}")
                if len(solution) < 30 and (f'{L}{year}', n) not in SOLUTION_TEXT_DROP: report.append(f'{L}{year}-{n}: short solution {solution!r}')
                if re.search(r'[ˇ˙˛¯]', q['prompt'] + solution + ''.join(opts.values())): report.append(f'{L}{year}-{n}: stray accent mark')
                _kid = KID.get(f'{L}{year}-{n}')
                if _kid:
                    if not re.search(r'\sAtsakymas: ' + (letter or '?') + r'\)', _kid): report.append(f'{L}{year}-{n}: kid solution does not end with the key')
                    q['solutionKid'] = _kid
                elif KID: report.append(f'{L}{year}-{n}: no kid solution')
                _mc = {k: v for k, v in (MISC.get(f'{L}{year}-{n}') or {}).items() if k in 'ABCDE' and k != letter and v}
                if _mc: q['misconceptions'] = _mc
                qs.append(q)
            if not with_figs:      # text-only rebuild: keep the pictures that are already cut
                for q in qs:
                    f = f"figures/{L}{year}-s{q['num']}.png"
                    if os.path.exists(os.path.join(HERE, f)): q['solutionFigure'] = f
            if with_figs:
                simg = solution_images(doc, sol, set(cfg['nums']), f'{L}{year}', {n for (pid, n) in list(KEY_FIX) + list(HEAD_HIDE) if pid == f'{L}{year}'})
                for q in qs:
                    if q['num'] in simg: q['solutionFigure'] = simg[q['num']]
                    else: report.append(f"{L}{year}-{q['num']}: no solution picture")
                _recrop.bici_pages = lambda d, old, _c=cond: _c
                lays = {}
                for q in qs:
                    if manual_cut(f"{L}{year}-{q['num']}", doc): continue
                    if f"{L}{year}-{q['num']}" in STRICT:
                        for p in cond:
                            if p not in lays: lays[p] = _extra_crop.page_layout(doc[p])
                            r = _extra_crop.crop(doc[p], q['num'], lays[p]) if lays[p] else None
                            if r:
                                _extra_crop.render(doc[p], r[0], r[1], os.path.join(FIGDIR, f"{L}{year}-q{q['num']}.png"))
                                trim_png(os.path.join(FIGDIR, f"{L}{year}-q{q['num']}.png")); break
                        else: report.append(f"{L}{year}-{q['num']}: figure NOT FOUND (strict)")
                        continue
                    r = _recrop.crop(os.path.relpath(pdf, HERE), q['num'], False, f'{L}{year}')
                    if not r: report.append(f"{L}{year}-{q['num']}: figure NOT FOUND"); continue
                    page, clip = r
                    Z = _recrop.ZOOM
                    pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(Z, Z), alpha=False)
                    for m in getattr(_recrop.crop, 'last_masks', []):
                        rr = m & clip
                        if rr.is_empty: continue
                        pix.set_rect(fitz.IRect(int(rr.x0 * Z), int(rr.y0 * Z), int(rr.x1 * Z) + 1, int(rr.y1 * Z) + 1), (255, 255, 255))
                    pix.save(os.path.join(FIGDIR, f"{L}{year}-q{q['num']}.png"))
                    trim_png(os.path.join(FIGDIR, f"{L}{year}-q{q['num']}.png"))
            band = cfg['band']
            test_url, sol_url = source_urls(L, year)
            papers.append({'year': f'{L}{year}', 'realYear': str(year), 'level': L, 'test_pdf': test_url, 'solutions_pdf': sol_url,
                           'title': f"Kengūra {year} · {cfg['name']} ({cfg['grades']}) · {band} uždaviniai",
                           'source': f"https://www.kengura.lt/uzduotys/ ({year}, {cfg['name']})",
                           'count': len(qs), 'questions': qs})
        out['levels'][L] = {'name': cfg['name'], 'grades': cfg['grades'], 'papers': papers}
    return out, report

if __name__ == '__main__':
    solution_images.tall = []
    data, report = build('--nofig' not in sys.argv and '--dry' not in sys.argv)
    if '--dry' in sys.argv:
        json.dump(data, open(os.path.join(HERE, '_levels_dry.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        print('\n'.join(report)); print(len(report), 'report lines (dry run: _levels_dry.json)'); sys.exit(0)
    fatal = [r for r in report if re.search(r'PROMPT_SUB|NOT FOUND|no key|condition not found|no solution picture|options parsed', r)]
    if fatal:
        print('\n'.join(fatal)); print('BUILD FAILED – nothing written'); sys.exit(1)
    json.dump(data, open(os.path.join(HERE, 'kengura-levels.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, 'kengura-levels.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.KENGURA_LEVELS = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    if getattr(solution_images, 'tall', None): print('tall answer pictures:', ' '.join(solution_images.tall))
    for L, v in data['levels'].items():
        print(L, len(v['papers']), 'papers', sum(len(p['questions']) for p in v['papers']), 'questions')
    print('\n'.join(report)); print(len(report), 'report lines')
