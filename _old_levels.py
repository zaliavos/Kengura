"""Nykštukas / Mažylis / Kadetas papers of 2000–2012 (added 2026-11-24).

kengura.lt has no per-level solution booklets for these years – only one test
booklet per year with every level (2000LT.pdf … 2008LT.pdf, TMK09…12_lietuviu.pdf,
in the project root since the Bičiulis archive was built) and one answer table
per year (levels_src/old-<name>.pdf, from https://www.kengura.lt/uzduotys/<name>).

This script cuts the question figures (figures/<L><year>-q<n>.png, with the
layout logic of _recrop.py) and reads the keys from the answer tables into
_levels_old.json. Prompts and options are NOT taken from the text layer (it is
garbled in these files): they were typed from the figures (_levels_old_text.json),
together with the kid solutions (_levels_kid.json) and the notes for wrong
options (_levels_misc.json). _extra_levels.py merges all of it into
kengura-levels.json; there is no official solution text or picture for these papers.

  python _old_levels.py            # figures + _levels_old.json
  python _old_levels.py --nofig    # keys / raw text only
  python _old_levels.py N2007-3 …  # re-cut single figures (prints the rectangle)
"""
import fitz, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _recrop
FIGDIR = os.path.join(HERE, 'figures')
SRC = {2000: '2000LT.pdf', 2001: '2001LT.pdf', 2002: '2002LT.pdf', 2003: '2003LT.pdf', 2004: '2004LT.pdf', 2005: '2005LT.pdf',
       2006: '2006LT.pdf', 2007: '2007LT.pdf', 2008: '2008LT.pdf', 2009: 'TMK09_lietuviu.pdf', 2010: 'TMK10_lietuviu.pdf',
       2011: 'TMK11_lietuviu.pdf', 2012: 'TMK12_lietuviu (1).pdf'}
ANSWERS = {2000: '2000ATS', 2001: '2001ATS', 2002: '2002ATS', 2003: '2003ATS', 2004: '2004ATS', 2005: '2005ATS', 2006: '2006ATS',
           2007: '2007ATS', 2008: '2008ATS', 2009: 'AT09', 2010: 'AT10', 2011: 'AT11', 2012: 'AT12'}
PLAIN = {2003, 2009, 2010, 2011, 2012}          # headers "1." (4 pages per level); the others print "M1."
TOTAL = {'N': 18, 'M': 24, 'B': 30, 'K': 30, 'J': 30, 'S': 30}
TAKE = {'N': range(1, 19), 'M': range(1, 25), 'K': range(1, 21)}      # Kadetas: the 3- and 4-point blocks, as for 2013+
POINTS = {'N': lambda n: 3 if n <= 6 else 4 if n <= 12 else 5, 'M': lambda n: 3 if n <= 8 else 4 if n <= 16 else 5,
          'K': lambda n: 3 if n <= 10 else 4 if n <= 20 else 5}
FIRST_N = 2007                                  # Nykštukas starts in 2007

# keys corrected after the blind re-solve from the figures (see CLAUDE.md): {(paper id, num): letter}
KEY_FIX_FILE = os.path.join(HERE, '_levels_old_keyfix.json')
KEY_FIX = json.load(open(KEY_FIX_FILE, encoding='utf-8')) if os.path.exists(KEY_FIX_FILE) else {}
# hand-cut figures {(paper id, num): (page index, (x0, y0, x1, y1), [mask rectangles])}
MANUAL = {
    ('K2010', 5): (12, (71, 420.4, 469.3, 485.5), [(71, 471.5, 430, 486)]),     # the hexagon's lowest dot hangs beside question 6
}
EXTRA_MASK = {
    ('M2000', 22): [(438, 658, 446, 671)],        # page number
    ('M2005', 1): [(398, 280, 452, 291.5)],        # a paw of the page mascot
    ('K2010', 3): [(378, 336, 470, 375)],         # top of question 4's stair figure
    ('K2010', 6): [(433, 477, 442, 486)],        # the lowest dot of question 5's hexagon
}
# the automatic rectangle ran into labels / the first word of the next question (found by the 2026-11 review): cut here
BOTTOM = {('K2002', 5): 593.5, ('K2006', 2): 308.5, ('K2006', 4): 446.5, ('K2006', 18): 217.8,
          ('K2012', 12): 402, ('M2001', 20): 162.8, ('M2002', 13): 477.5, ('M2012', 16): 336, ('K2001', 2): 426,
          ('K2001', 4): 586.8, ('K2001', 19): 210.8}
# a question that runs over a page break: rectangles pasted under each other
STITCH = {('K2000', 18): [(9, (102.6, 659.2, 495.1, 715.9)), (10, (102.6, 130.5, 495.1, 190.5))]}

def stitch(pid, n):
    from PIL import Image
    doc = fitz.open(os.path.join(HERE, SRC[int(pid[1:])]))
    Z = _recrop.ZOOM
    ims = []
    for pno, r in STITCH[(pid, n)]:
        pix = doc[pno].get_pixmap(clip=fitz.Rect(*r), matrix=fitz.Matrix(Z, Z), alpha=False)
        ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
    W = max(i.size[0] for i in ims)
    out = Image.new('RGB', (W, sum(i.size[1] for i in ims)), 'white')
    y = 0
    for i in ims: out.paste(i, (0, y)); y += i.size[1]
    out.save(os.path.join(FIGDIR, f'{pid}-q{n}.png'))

def levels_of(year): return 'NMBKJS' if year >= FIRST_N else 'MBKJS'

def read_keys(year):
    """{level: {num: letter}} from the answer table (rows "7 A D B A D", shorter levels drop out)."""
    doc = fitz.open(os.path.join(HERE, 'levels_src', f'old-{ANSWERS[year]}.pdf'))
    keys = {}
    for page in doc:
        toks = page.get_text().split()
        cols = None
        i = 0
        # the 2012 table is split over three pages, two levels each: the header names them
        first = next((k for k, t in enumerate(toks) if re.fullmatch(r'\d{1,2}', t)), 0)
        head = [t for t in toks[:first] if t in ('N', 'M', 'B', 'K', 'J', 'S')]
        order = [L for L in levels_of(year) if L in head] if len(doc) > 1 else list(levels_of(year))
        while i < len(toks):
            if re.fullmatch(r'\d{1,2}', toks[i]):
                n = int(toks[i]); j = i + 1; row = []
                while j < len(toks) and re.fullmatch(r'[A-E]', toks[j]): row.append(toks[j]); j += 1
                want = [L for L in order if TOTAL[L] >= n]
                if row and len(row) == len(want) and 1 <= n <= 30:
                    for L, a in zip(want, row): keys.setdefault(L, {})[n] = a
                    i = j; continue
            i += 1
    return keys

def level_pages(doc, year, L):
    if year in PLAIN:
        k = levels_of(year).index(L)
        return range(4 * k, 4 * k + 4)
    pat = re.compile(r'^' + L + r'(\d{1,2})\.$')
    return [p for p in range(len(doc)) if any(pat.match(w[4]) for w in doc[p].get_text('words'))]

def cut(year, L, n, save=True):
    """Cut one question; returns (page, clip, masks) or None."""
    pid = f'{L}{year}'
    pdf = SRC[year]
    doc = fitz.open(os.path.join(HERE, pdf))
    if (pid, n) in MANUAL:
        pno, r, *mk = MANUAL[(pid, n)]
        page, clip, masks = doc[pno], fitz.Rect(*r), [fitz.Rect(*m) for m in (mk[0] if mk else [])]
    else:
        pages = level_pages(doc, year, L)
        pat = re.compile(r'^(\d{1,2})\.$' if year in PLAIN else r'^' + L + r'(\d{1,2})\.$')
        def headers(page, old, _pat=pat):
            lines = {}
            for w in page.get_text('words'): lines.setdefault((w[5], w[6]), []).append(w)
            out = []
            for ws in lines.values():
                w = min(ws, key=lambda w: w[0]); m = _pat.match(w[4])
                if m: out.append((int(m.group(1)), fitz.Rect(w[:4])))
            return out
        keep = (_recrop.headers, _recrop.bici_pages)
        _recrop.headers, _recrop.bici_pages = headers, (lambda d, old, _p=pages: _p)
        try: r = _recrop.crop(pdf, n, False, pid)
        finally: _recrop.headers, _recrop.bici_pages = keep
        if not r: return None
        page, clip = r
        masks = list(getattr(_recrop.crop, 'last_masks', [])) + [fitz.Rect(*m) for m in EXTRA_MASK.get((pid, n), [])]
        if (pid, n) in BOTTOM: clip = fitz.Rect(clip.x0, clip.y0, clip.x1, min(clip.y1, BOTTOM[(pid, n)]))
    if save and (pid, n) in STITCH:
        stitch(pid, n)
    elif save:
        Z = _recrop.ZOOM
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(Z, Z), alpha=False)
        for m in masks:
            rr = m & clip
            if rr.is_empty: continue
            pix.set_rect(fitz.IRect(int(rr.x0 * Z), int(rr.y0 * Z), int(rr.x1 * Z) + 1, int(rr.y1 * Z) + 1), (255, 255, 255))
        out = os.path.join(FIGDIR, f'{pid}-q{n}.png')
        pix.save(out)
        try:
            import _extra_levels
            _extra_levels.trim_png(out)
        except Exception as e: print('trim failed', pid, n, e)
    return page, clip, masks

def raw_text(page, clip, masks):
    ws = [w for w in page.get_text('words') if clip.contains(fitz.Rect(w[:4])) and not any((m & fitz.Rect(w[:4])).get_area() > 0.5 * fitz.Rect(w[:4]).get_area() for m in masks)]
    ws.sort(key=lambda w: (w[5], w[6], w[7]))
    return ' '.join(w[4] for w in ws)

def build(with_figs=True):
    out, report = {'levels': {'N': [], 'M': [], 'K': []}}, []
    for year in sorted(SRC):
        keys = read_keys(year)
        for L in 'NMK':
            if L == 'N' and year < FIRST_N: continue
            if len(keys.get(L, {})) != TOTAL[L]: report.append(f'{L}{year}: {len(keys.get(L, {}))} keys read, want {TOTAL[L]}')
            qs = []
            for n in TAKE[L]:
                r = cut(year, L, n, save=with_figs)
                if not r: report.append(f'{L}{year}-{n}: figure NOT FOUND'); continue
                page, clip, masks = r
                key = KEY_FIX.get(f'{L}{year}-{n}') or keys.get(L, {}).get(n)
                if not key: report.append(f'{L}{year}-{n}: no key')
                qs.append({'num': n, 'points': POINTS[L](n), 'correct': key, 'tableKey': keys.get(L, {}).get(n),
                           'figure': f'figures/{L}{year}-q{n}.png', 'level': L, 'page': page.number, 'raw': raw_text(page, clip, masks)})
            out['levels'][L].append({'year': f'{L}{year}', 'realYear': str(year), 'level': L,
                                     'test_pdf': f"https://www.kengura.lt/uzduotys/{SRC[year].replace(' (1)', '')}",
                                     'answers_pdf': f'https://www.kengura.lt/uzduotys/{ANSWERS[year]}.pdf', 'questions': qs})
        # the Bičiulis column checks that the table is read right (those keys were audited in 2026-10)
        try:
            arch = json.load(open(os.path.join(HERE, 'kengura-archive.json'), encoding='utf-8'))['archive']
            t = next((t for t in arch if str(t['year']) == str(year)), None)
            if t:
                diff = [q['num'] for q in t['questions'] if q.get('correct') and keys.get('B', {}).get(q['num']) != q['correct']]
                report.append(f'{year}: Bičiulis table vs archive – {len(diff)} differ {diff}')
        except Exception as e: report.append(f'{year}: archive check failed {e}')
    return out, report

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    single = [a for a in sys.argv[1:] if re.fullmatch(r'[NMK]\d{4}-\d{1,2}', a)]
    if single:
        for s in single:
            L, year, n = s[0], int(s[1:5]), int(s.split('-')[1])
            r = cut(year, L, n)
            print(s, 'NOT FOUND' if not r else ('page', r[0].number, [round(v, 1) for v in r[1]], 'masks', len(r[2])))
        sys.exit()
    data, report = build('--nofig' not in sys.argv)
    json.dump(data, open(os.path.join(HERE, '_levels_old.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    for r in report: print(r)
    print({L: (len(v), sum(len(p['questions']) for p in v)) for L, v in data['levels'].items()})
