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
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(HERE, 'kengura-archive.json')

MAP = {('z','ˇ'):'ž',('s','ˇ'):'š',('c','ˇ'):'č',('Z','ˇ'):'Ž',('S','ˇ'):'Š',('C','ˇ'):'Č',
       ('e','˙'):'ė',('E','˙'):'Ė',('a','˛'):'ą',('e','˛'):'ę',('i','˛'):'į',('u','˛'):'ų',
       ('A','˛'):'Ą',('E','˛'):'Ę',('I','˛'):'Į',('U','˛'):'Ų',('u','¯'):'ū',('U','¯'):'Ū'}
def ltnorm(t):
    t = re.sub(r'([A-Za-z])\s?([ˇ˙˛¯])', lambda m: MAP.get((m.group(1), m.group(2)), m.group(0)), t)
    t = t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    return unicodedata.normalize('NFC', t)

JUNK_LINE = re.compile(r'^(\d{1,3}|Bičiulis.*|Bičiulio užduočių sprendimai|UŽDUOČIŲ SPRENDIMAI|'
                       r'\d*\s*UŽDUOČIŲ SPRENDIMAI\s*\d*|Kadetas.*|Mažylis.*|KENGŪRA.*)$')
HDR_MODERN = re.compile(r'(?m)^(\d{1,2})\. ([A-E])\s*$')
HDR_OLD = re.compile(r'(?m)^([MBKJS])(\d{1,2})\.\s*$')

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
        lm = re.match(r'\s*([A-E])(?=\s|⃝)', body)
        key = (x.group(1), int(x.group(2)))
        if key not in segs:
            segs[key] = (lm.group(1) if lm else None, body[lm.end():] if lm else body)
    return segs

def sq(t): return ''.join(c.lower() for c in t if c.isalnum())

def main():
    data = json.load(open(J, encoding='utf-8'))
    changed = kept = 0
    for y in data['archive']:
        pdf = y.get('solutions_pdf')
        if not pdf: continue
        text = ltnorm('\n'.join(p.get_text() for p in fitz.open(os.path.join(HERE, pdf))))
        segs = segments(text)
        for q in y['questions']:
            hit = segs.get(('B', q['num']))
            if not hit: continue
            letter, body = hit
            ref = re.search(r'Žr\.\s*(?:uždavinio\s*)?([MKJ])(\d{1,2})\s*sprendim', body) or \
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
            new = join_lines(body)
            if via_ref:
                # the other level orders its options differently: drop its letters
                parts = re.split(r'(?<=[.!?])\s+', new)
                new = ' '.join(x for x in parts
                               if not re.search(r'(atsakym\w*|[Tt]inka|netinka)[^.]*\b[A-E]\b', x))
            elif q.get('correct'):
                # booklet typos like "Teisingas atsakymas D" under a solution of C
                new = re.sub(r'((?:[Tt]eisingas atsakymas(?: yra)?|[Rr]enkamės atsakymą)\s*[–-]?\s*)([A-E])(?=\.)',
                             lambda m: m.group(1) + q['correct'], new)
            if letter and q.get('correct') and letter != q['correct']:
                print(f"{y['year']}-{q['num']}: header letter {letter} != key {q['correct']} – kept old"); kept += 1; continue
            old = q.get('solution') or ''
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
