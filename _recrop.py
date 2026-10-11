"""Re-crop question figures from the test booklets by layout (2026-10-11).

The first crops cut each question at its own number line, so a picture
that starts above that line (it sits to the right of the previous
question's options) lost its top, and the previous figure got it instead.
Here a question's band runs from its header ("13." / "B13.") to the next
header in the same column; every drawing/image component (connected
vector paths + raster images) that straddles the top of the band is pulled
in whole, and one that straddles the bottom is left to the next question.
Usage: python _recrop.py 2018-9 2019-13 ...   (plain python: PyMuPDF)
The 58 figures the 2026-10-11 audit flagged were re-cut with it (see git log).
"""
import fitz, json, os, re, sys, io
sys.path.insert(0, os.environ.get('KENGURA_HOME') or os.path.dirname(os.path.abspath(__file__)))
from _reextract_solutions import ltnorm
HERE = os.environ.get('KENGURA_HOME') or os.path.dirname(os.path.abspath(__file__))
ZOOM = 2.7

def headers(page, old):
    """[(num, rect)] of question-number words that start a line."""
    out = []
    pat = re.compile(r'^B(\d{1,2})\.$' if old else r'^(\d{1,2})\.$')
    words = page.get_text('words')
    lines = {}
    for w in words:
        lines.setdefault((w[5], w[6]), []).append(w)
    for ws in lines.values():
        w = min(ws, key=lambda w: w[0])
        m = pat.match(w[4])
        if m: out.append((int(m.group(1)), fitz.Rect(w[:4])))
    return out

def components(page, col):
    rects = []
    for d in page.get_drawings():
        r = fitz.Rect(d['rect'])
        if r.width > col.width * 0.9 and r.height < 3: continue   # rules / separators
        if r.is_empty and r.width == 0 and r.height == 0: continue
        if r.intersects(col) or col.contains(r): rects.append(r)
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if r.intersects(col): rects.append(fitz.Rect(r))
    comps = []
    for r in rects:
        g = fitz.Rect(r) + (-3, -3, 3, 3)
        merged = [c for c in comps if c.intersects(g)]
        for c in merged: comps.remove(c); r = r | c
        comps.append(fitz.Rect(r))
    # second pass to merge chains
    changed = True
    while changed:
        changed = False
        for i in range(len(comps)):
            for j in range(i + 1, len(comps)):
                if (comps[i] + (-3, -3, 3, 3)).intersects(comps[j]):
                    comps[i] = comps[i] | comps[j]; del comps[j]; changed = True; break
            if changed: break
    return comps

LEVELS = re.compile(r'(?i)(nykštuk|mažyl|bičiul|kadet|junior|senjor|student)')
def bici_pages(doc, old):
    """Page range of the Bičiulis section in a multi-level booklet."""
    if old: return range(len(doc))
    starts = []
    for pno, page in enumerate(doc):
        if any(w[4] == '1.' and w[0] < 130 for w in page.get_text('words')):
            m = LEVELS.search(ltnorm(page.get_text()))
            if m: starts.append((pno, m.group(1).lower()))
    for i, (pno, lvl) in enumerate(starts):
        if lvl == 'bičiul':
            end = starts[i + 1][0] if i + 1 < len(starts) else len(doc)
            return range(pno, end)
    return range(len(doc))

def locate(doc, n, old):
    """(page, column rect, header rect, next header rect or None)"""
    for pno in bici_pages(doc, old):
        page = doc[pno]
        hs = headers(page, old)
        mine = [h for h in hs if h[0] == n]
        if not mine: continue
        hr = mine[0][1]
        W, H = page.rect.width, page.rect.height
        if W > H:   # landscape booklet: two columns
            col = fitz.Rect(0, 0, W / 2, H) if hr.x0 < W / 2 else fitz.Rect(W / 2, 0, W, H)
        else:
            col = fitz.Rect(0, 0, W, H)
        incol = [h for h in hs if col.contains(h[1])]
        left = min(h[1].x0 for h in incol)
        incol = [h for h in incol if h[1].x0 <= left + 10]      # "7." inside a sentence is not a header
        if hr.x0 > left + 10: continue
        below = [h for h in incol if h[1].y0 > hr.y0 + 2]
        seq = [h for h in below if h[0] == n + 1]
        pick = seq or below
        nxt = min(pick, key=lambda h: h[1].y0)[1] if pick else None
        return page, col, hr, nxt
    return None

# words outside the question's band that sit within a drawing's label margin
# but belong to the previous question (checked by eye)
FORCE_MASK = {('2017', 14): {'9818192'}, ('2010', 12): {'20', '+', '10'}}

MANUAL = {  # (year, num): (page index, clip[, masks]) – picture spread over neighbouring questions
    ('2003', 5): (4, (71, 308, 469, 439)),
    # the grid's top row sits beside Q19's options (its centre is above the header)
    ('2024', 20): (1, (424, 286, 830, 377), [(420, 270, 734, 292)]),
}

def crop(pdf, n, old, year=None):
    crop.last_masks = []
    if (year, n) in MANUAL:
        pno, r, *mk = MANUAL[(year, n)]
        crop.last_masks = [fitz.Rect(*m) for m in (mk[0] if mk else [])]
        return fitz.open(os.path.join(HERE, pdf))[pno], fitz.Rect(*r)
    doc = fitz.open(os.path.join(HERE, pdf))
    loc = locate(doc, n, old)
    if not loc: return None
    page, col, hr, nxt = loc
    top = hr.y0 - 3
    comps = components(page, col)
    # a section heading ("KLAUSIMAI PO 4 TAŠKUS") under the last question of a band ends it
    sect = [fitz.Rect(w[:4]) for w in page.get_text('words') if w[4].lower() == 'klausimai'
            and col.contains(fitz.Rect(w[:4])) and w[1] > hr.y1 and (not nxt or w[1] < nxt.y0)]
    sect_y = None
    if sect:
        nxt = fitz.Rect(min(sect, key=lambda r: r.y0)); sect_y = nxt.y1
    if nxt:
        bottom = nxt.y0 - 2
    else:   # last question of the column: down to its last word / drawing
        words = page.get_text('words')
        # copyright footer lines ("© 2014 Kengūros konkurso organizavimo komitetas";
        # in the TeX booklets the © is a "c" inside a drawn circle)
        foot = {round(w[1]) for w in words if w[4].startswith('©') or w[4] in ('organizavimo', 'komitetas', 'TEV,')}
        ys = [w[3] for w in words if col.contains(fitz.Rect(w[:4])) and w[1] > hr.y0
              and all(abs(w[1] - f) > 3 for f in foot)]
        ys += [c.y1 for c in comps if c.y0 > hr.y0 - 40 and c.y1 > hr.y0
               and all(abs(c.y0 - f) > 6 for f in foot)]
        bottom = (max(ys) + 4) if ys else col.y1 - 8
    # a drawing belongs to the question whose band holds its vertical centre
    band_top, band_bot = hr.y0 - 3, bottom
    for c in comps:
        mid = (c.y0 + c.y1) / 2
        if band_top <= mid < band_bot + 2:
            if c.y0 < top: top = c.y0 - 14          # + room for a label above the drawing
            if c.y1 > bottom: bottom = c.y1 + 12           # + room for a label under it
    own_text = [w[3] for w in page.get_text('words')
                if col.contains(fitz.Rect(w[:4])) and hr.y0 - 1 <= w[1] < band_bot]
    floor = (max(own_text) + 3) if own_text else hr.y1
    for c in comps:      # someone else's drawing poking into our band (never cut our own text)
        mid = (c.y0 + c.y1) / 2
        if mid >= band_bot + 2 and c.y0 < bottom and c.y0 > hr.y1: bottom = max(floor, min(bottom, c.y0 - 2))
    # text of this question decides the width; components inside the band widen it
    # never cut through a text line or a drawing: snap outwards to whole lines
    for _ in range(3):
        for w in page.get_text('words'):
            r = fitz.Rect(w[:4])
            if not col.contains(r): continue
            if r.y0 < top < r.y1 - 1: top = r.y0 - 2
            if r.y0 + 1 < bottom < r.y1: bottom = r.y1 + 2
        for c in comps:
            mid = (c.y0 + c.y1) / 2              # only drawings that are ours
            if c.y0 < top < c.y1 - 1 and c.height < 80 and mid > top: top = c.y0 - 2
            if c.y0 + 1 < bottom < c.y1 and c.height < 80 and mid < bottom: bottom = c.y1 + 2
    band = fitz.Rect(col.x0, top, col.x1, bottom)
    xs = [fitz.Rect(w[:4]) for w in page.get_text('words') if band.contains(fitz.Rect(w[:4]))]
    xs += [c for c in comps if band.intersects(c) and c.width < band.width * 0.95]
    if xs:
        x0 = max(col.x0, min(r.x0 for r in xs) - 6); x1 = min(col.x1, max(r.x1 for r in xs) + 6)
    else:
        x0, x1 = col.x0 + 4, col.x1 - 4
    clip = fitz.Rect(x0, top, x1, bottom) & page.rect
    # Neighbour debris: words of the previous / next question that the
    # rectangle had to include (a picture starting beside the previous
    # question's options). They get painted white - unless they sit on one
    # of our own drawings (labels like "2 cm"). Same for other questions'
    # drawings poking into the rectangle.
    lo, hi = hr.y0 - 1, (nxt.y0 - 1) if nxt else clip.y1 + 1
    own = [c + (-8, -8, 8, 8) for c in comps if lo - 2 <= (c.y0 + c.y1) / 2 < hi + 2]
    masks = []
    # a text line with >= 3 words outside the band is a neighbour's sentence or
    # options row, never a drawing label – it goes even when it touches a drawing
    from collections import Counter
    out_lines = Counter(round(w[3] / 3) for w in page.get_text('words')
                        if clip.intersects(fitz.Rect(w[:4])) and (w[3] <= lo + 1 or w[1] >= hi))
    for w in page.get_text('words'):
        r = fitz.Rect(w[:4])
        if not clip.intersects(r): continue
        outside = r.y1 <= lo + 1 or r.y0 >= hi
        if outside and out_lines[round(w[3] / 3)] >= 3: masks.append(r + (-1, -1, 1, 1)); continue
        heading = sect_y is not None and abs(w[3] - sect_y) < 2.5   # same baseline as the section heading
        forced = heading or (outside and w[4] in FORCE_MASK.get((year, n), ()))
        if forced or (outside and not any(o.intersects(r) for o in own)): masks.append(r + (-1, -1, 1, 1))
    # our own words (inside the band) are never painted over – a neighbour's
    # drawing box or a rotated page banner can overlap them (2017-3, 2021-11)
    mine = [fitz.Rect(w[:4]) for w in page.get_text('words')
            if clip.intersects(fitz.Rect(w[:4])) and lo + 1 < (w[1] + w[3]) / 2 < hi]
    for c in comps:
        mid = (c.y0 + c.y1) / 2
        if clip.intersects(c) and not (lo - 2 <= mid < hi + 2) and not any(o.contains(c) for o in own)                 and not any(c.intersects(r) for r in mine):
            masks.append(c + (-1, -1, 1, 1))
    crop.last_masks = masks
    return page, clip

if __name__ == '__main__':
    data = json.load(open(os.path.join(HERE, 'kengura-archive.json'), encoding='utf-8'))
    Y = {y['year']: y for y in data['archive']}
    outdir = os.environ.get('RECROP_OUT', os.path.join(HERE, 'figures'))
    for spec in sys.argv[1:]:
        yr, n = spec.split('-'); n = int(n)
        old = Y[yr]['test_pdf'] in ('2000LT.pdf', '2001LT.pdf', '2002LT.pdf', '2004LT.pdf', '2005LT.pdf', '2006LT.pdf', '2007kengura.pdf', '2008LT.pdf')
        r = crop(Y[yr]['test_pdf'], n, old, yr)
        if not r: print(spec, 'NOT FOUND'); continue
        page, clip = r
        pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(ZOOM, ZOOM), alpha=False)
        for m in getattr(crop, 'last_masks', []):
            r = (m & clip)
            if r.is_empty: continue
            # the pixmap lives in page coordinates × ZOOM (its irect isn't at 0,0)
            ir = fitz.IRect(int(r.x0 * ZOOM), int(r.y0 * ZOOM), int(r.x1 * ZOOM) + 1, int(r.y1 * ZOOM) + 1)
            pix.set_rect(ir, (255, 255, 255))
        pix.save(os.path.join(outdir, f'{yr}-q{n}.png'))
        print(spec, 'page', page.number + 1, [round(v) for v in clip])
