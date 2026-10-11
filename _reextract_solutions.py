"""Re-extract the official solutions with PyMuPDF (2026-10-11).

The first build used pdfplumber, which dropped and invented word breaks
("pavei kslėlyje", "slaptąabėcėlę") all over q.solution. PyMuPDF keeps the
real spacing. Each solution booklet heads a problem's solution with its
number and answer letter:

  modern (2013, 2018-2025):  "7. A" line
  old (2000-2012):           "B7." line, then the letter (+ "⃝ value")

The segment up to the next header is the solution. "Žr. uždavinio M16
sprendimą" (see Mažylis/Kadetas problem 16) is resolved to that problem's
text. The header letter must equal q.correct (it does for every year after
_fix_keys_2024.py); a segment whose content differs too much from the old
extraction is reported and the old text kept.

Output keeps the booklet's markers, which kengura.html renders:
  "<answer value> ? quick way (spėjimas) ! full solution !! other solution"
Run with plain `python` (PyMuPDF lives in the user site-packages).
"""
import json, os, re, sys, io, difflib, unicodedata, subprocess
import fitz
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _pagetext import page_text
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')

MAP = {('z','ˇ'):'ž',('s','ˇ'):'š',('c','ˇ'):'č',('Z','ˇ'):'Ž',('S','ˇ'):'Š',('C','ˇ'):'Č',
       ('e','˙'):'ė',('E','˙'):'Ė',('a','˛'):'ą',('e','˛'):'ę',('i','˛'):'į',('u','˛'):'ų',
       ('A','˛'):'Ą',('E','˛'):'Ę',('I','˛'):'Į',('U','˛'):'Ų',('u','¯'):'ū',('U','¯'):'Ū'}
def ltnorm(t):
    t = re.sub(r'([A-Za-z])\s?([ˇ˙˛¯])', lambda m: MAP.get((m.group(1), m.group(2)), m.group(0)), t)
    t = t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    t = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', t)   # stray control chars from the PDF text layer
    return unicodedata.normalize('NFC', t)

JUNK_LINE = re.compile(r'^(\d{1,3}|Bičiulis.*|Bičiulio užduočių sprendimai|UŽDUOČIŲ SPRENDIMAI|'
                       r'\d*\s*UŽDUOČIŲ SPRENDIMAI\s*\d*|Kadetas.*|Mažylis.*|KENGŪRA.*)$')
HDR_MODERN = re.compile(r'(?m)^(\d{1,2})\. ([A-E])(?=[ \t]*$|[ \t]+\d)')   # "7. A", or "2. C 2021/29" when _pagetext set the value on the line
HDR_OLD = re.compile(r'(?m)^([MBKJS])(\d{1,2})\.(?=[ \t]*$|\s+Žr\.)')   # "B24." alone or "B24. Žr. M23 ..."

def join_lines(seg):
    lines = [l.strip() for l in seg.split('\n')]
    lines = [l for l in lines if l and not JUNK_LINE.match(l)]
    out = ''
    for l in lines:
        if out.endswith('-') and l[:1].islower() and not out.endswith(' -'):
            out = out[:-1] + l
        else:
            out = (out + ' ' + l) if out else l
    out = out.replace('⃝', ' ').replace('––', '–')
    out = re.sub(r'\s+', ' ', out).strip()
    out = re.sub(r'\s+([.,;:)])', r'\1', out)
    out = re.sub(r'([(„])\s+', r'\1', out)
    return out

def drop_label_lines(seg):
    """Between the answer value line and the first "?"/"!" paragraph the
    booklets often leave the figure's labels ("D", "N", "M", "C") - drop
    lines made only of such short tokens there."""
    lines = seg.split('\n')
    out, seen_value, in_head = [], False, True
    for l in lines:
        st = l.strip()
        if in_head and re.match(r'^(\?\??|!!?)(\s|$)', st): in_head = False
        if in_head and st:
            if not seen_value: seen_value = True
            elif all(len(tok) <= 3 for tok in st.split()) and not re.search(r'\d', st): continue
        out.append(l)
    return '\n'.join(out)

def segments(text):
    """{(level, num): (letter or None, raw segment)}"""
    segs = {}
    m = list(HDR_MODERN.finditer(text))
    if len(m) >= 25:
        # the conditions section can repeat "n." lines; keep the LAST run 1..30
        starts = [x for x in m]
        for i, x in enumerate(starts):
            end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
            body = text[x.end():end]
            body = body.split('\nAtsakymai\n')[0]
            segs[('B', int(x.group(1)))] = (x.group(2), body)
        return segs
    m = list(HDR_OLD.finditer(text))
    for i, x in enumerate(m):
        end = m[i + 1].start() if i + 1 < len(m) else len(text)
        body = text[x.end():end]
        lm = re.match(r'\s*⃝?\s*([A-E])(?=\s|⃝|\d)', body)   # "C⃝2641" or, via _pagetext, "⃝C2641"
        key = (x.group(1), int(x.group(2)))
        if key not in segs:
            segs[key] = (lm.group(1) if lm else None, body[lm.end():] if lm else body)
    return segs

# booklets whose stacked fractions (small numerator over denominator) _pagetext
# rebuilds as "a/b"; checked by eye - elsewhere figure labels get mixed in.
# PT_YEARS=2000,2001 overrides it for experiments.
FRACTION_YEARS = set(os.environ['PT_YEARS'].split(',')) if os.environ.get('PT_YEARS') else \
    {'2000', '2001', '2002', '2003', '2004', '2005',
     '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'}
# keys where the booklet itself is wrong (see _fix_keys_audit.py, run after this script)
BOOKLET_KEY_ERRORS = {('2000', 23), ('2003', 28), ('2005', 24), ('2009', 24), ('2010', 4), ('2011', 10)}
SOLUTION_BOOKLETS = {'2014': 'Solutions/spGDPRB (1).pdf', '2015': 'Solutions/spGDPRB (2).pdf',
                     '2016': 'Solutions/spGDPRB.pdf', '2017': 'Solutions/spGDPRB (3).pdf'}

def sq(t): return ''.join(c.lower() for c in t if c.isalnum())

def main():
    data = json.load(open(J, encoding='utf-8'))
    # 2014-2017: the full solution booklets live in Solutions/ (they were
    # only used for the answer tables before)
    for y in data['archive']:
        if y['year'] in SOLUTION_BOOKLETS and not y.get('solutions_pdf'):
            y['solutions_pdf'] = SOLUTION_BOOKLETS[y['year']]
    changed = kept = 0
    for y in data['archive']:
        pdf = y.get('solutions_pdf')
        if not pdf: continue
        doc = fitz.open(os.path.join(HERE, pdf))
        use_pt = y['year'] in FRACTION_YEARS
        text = ltnorm('\n'.join((page_text(p) if use_pt else p.get_text()) for p in doc))
        segs = segments(text)
        for q in y['questions']:
            hit = segs.get(('B', q['num']))
            if not hit: continue
            letter, body = hit
            ref = re.search(r'Žr\.\s*(?:uždavinio\s*)?([MKJ])(\d{1,2})\s*(?:uždavinio\s*)?sprendim', body) or \
                  re.search(r'Žr\.\s*(Mažylio|Kadeto)\s*(\d{1,2})\s*uždavinio', body)
            via_ref = False
            if ref:
                lvl = {'Mažylio': 'M', 'Kadeto': 'K'}.get(ref.group(1), ref.group(1))
                other = segs.get((lvl, int(ref.group(2))))
                if other:
                    # keep THIS paper's answer value, take the reasoning from the other level
                    own_value = join_lines(body[:ref.start()])
                    other_text = join_lines(other[1])
                    mk = re.search(r'(^|\s)[!?]', other_text)
                    body = own_value + ' ' + (other_text[mk.start():] if mk else other_text)
                    via_ref = True
            new = join_lines(drop_label_lines(body))
            if re.fullmatch(r'.{0,40}Žr\..{0,40}sprendimą\.?', new):
                new = ''          # pointer to a level whose solutions this booklet lacks
            if q.get('imageOnlyOptions'):
                # picture options have no value line; stacked figure numbers
                # can masquerade as one ("2021/29") - drop it
                mk = re.search(r'(^|\s)(\?\??|!!?)\s', new)
                if mk and '/' in new[:mk.start()]: new = new[mk.start():].strip()
            if via_ref:
                # the other level orders its options differently: drop its letters
                parts = re.split(r'(?<=[.!?])\s+', new)
                new = ' '.join(x for x in parts
                               if not re.search(r'(atsakym\w*|[Tt]inka|netinka)[^.]*\b[A-E]\b', x))
            elif q.get('correct'):
                # booklet typos like "Teisingas atsakymas D" under a solution of C
                new = re.sub(r'((?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą)\s*[–-]?\s*)([A-E])(?=\.)',
                             lambda m: m.group(1) + q['correct'], new)
            if letter and q.get('correct') and letter != q['correct'] and (y['year'], q['num']) not in BOOKLET_KEY_ERRORS:
                print(f"{y['year']}-{q['num']}: header letter {letter} != key {q['correct']} – kept old"); kept += 1; continue
            old = q.get('solution') or ''
            if not new:
                if old: q['solution'] = ''; changed += 1
                continue
            if len(sq(new)) < 20: continue
            if old:
                r = difflib.SequenceMatcher(None, sq(old)[:1500], sq(new)[:1500], autojunk=False).ratio()
                if r < 0.55 and not via_ref and sq(new)[:200] not in sq(old):
                    print(f"{y['year']}-{q['num']}: low overlap {r:.2f} – kept old | {new[:80]}"); kept += 1; continue
            if new != old:
                q['solution'] = new; changed += 1
    json.dump(data, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(HERE, '_regen_js.py')], cwd=HERE, check=True)
    print('changed', changed, 'kept', kept)

if __name__ == '__main__':
    main()
