"""Stricter figure crop for the neighbour-level booklets (single column).

_recrop.crop() leaves labels and picture tops of the NEXT question in a
crop when that picture starts beside this question's options. Here every
word and drawing is first assigned to a question, the rectangle is the
bounding box of the question's own things, and everything foreign inside
it is painted white. Used by _extra_levels.py for the papers/questions in
STRICT (found by the figure check of 2026-11-22).
"""
import fitz, re
import _recrop

def _merge(rects, gap):
    comps = [fitz.Rect(r) for r in rects]
    changed = True
    while changed:
        changed = False
        for i in range(len(comps)):
            for j in range(i + 1, len(comps)):
                if (comps[i] + (-gap, -gap, gap, gap)).intersects(comps[j]):
                    comps[i] = comps[i] | comps[j]; del comps[j]; changed = True; break
            if changed: break
    return comps

def page_layout(page):
    words = page.get_text('words')
    hs = _recrop.headers(page, False)
    if not hs: return None
    left = min(h[1].x0 for h in hs)
    hs = sorted([h for h in hs if h[1].x0 <= left + 10], key=lambda h: h[1].y0)
    # a fraction right after the number starts above the number's own line
    tops = []
    for n, r in hs:
        t = r.y0
        for w in words:
            if w[0] > r.x1 and w[1] < r.y0 and w[3] > r.y0 + 2 and r.y0 - w[1] < 14: t = min(t, w[1])
        tops.append(t - 3)
    sect = sorted(w[1] - 3 for w in words if w[4].lower() == 'klausimai' and w[0] < left + 40)
    raw = []
    top_rule = None
    for d in page.get_drawings():
        r = fitz.Rect(d['rect'])
        if r.width > page.rect.width * 0.75 and r.height < 3 and r.y0 < 60: top_rule = max(top_rule or 0, r.y1)
        if r.width > page.rect.width * 0.9 and r.height < 3: continue      # rules across the page
        if r.width > page.rect.width * 0.75 and r.height < 3 and (r.y0 < 60 or r.y1 > page.rect.height - 60): continue   # the rule under the running head
        if r.width > page.rect.width * 0.75 and r.height < 3 and (r.y0 < 60 or r.y1 > page.rect.height - 60): continue   # the rule under the running head
        raw.append(r + (-0.4, -0.4, 0.4, 0.4))                             # a hairline has an empty rect
    for img in page.get_images(full=True):
        raw += [fitz.Rect(r) for r in page.get_image_rects(img[0])]
    comps = [c for c in _merge(raw, 5)
             if not (c.height < 3 and c.width > 150) and c.height < page.rect.height * 0.7]
    return dict(words=words, hs=hs, tops=tops, sect=sect, comps=comps, left=left, top_rule=top_rule)

def crop(page, n, lay=None):
    """(clip, masks) or None"""
    lay = lay or page_layout(page)
    if not lay: return None
    idx = next((i for i, h in enumerate(lay['hs']) if h[0] == n), None)
    if idx is None: return None
    hr = lay['hs'][idx][1]
    top = lay['tops'][idx]
    bounds = [t for t in lay['tops'] if t > top + 4] + [s for s in lay['sect'] if s > top + 4]
    nb = min(bounds) if bounds else page.rect.y1
    H = page.rect.height
    lines = {}
    for w in lay['words']: lines.setdefault((w[5], w[6]), []).append(w)
    is_main = lambda ws: min(w[0] for w in ws) <= hr.x1 + 30
    # the options are the last text of a question: its main text ends there
    def main_bottom(a, b):
        ys = [w[3] for ws in lines.values() if is_main(ws) for w in ws if a <= (w[1] + w[3]) / 2 < b]
        return max(ys) if ys else a
    mb = main_bottom(top, nb)
    prev_tops = [t for t in lay['tops'] if t < top - 4]
    prev_mb = main_bottom(max(prev_tops), top) if prev_tops else None
    nxt = [h[1] for h, t in zip(lay['hs'], lay['tops']) if t > top + 4]
    nh = min(nxt, key=lambda r: r.y0) if nxt else None
    inline = lambda r, h: r.height < 45 and r.y0 < h.y1 - 3 and r.y1 > h.y0 - 1 and r.y0 > h.y0 - 22 and r.x0 > h.x1
    def inband(r, main=False):
        mid = (r.y0 + r.y1) / 2
        if main: return top <= mid < nb
        if nh is not None and inline(r, nh): return False          # set inside the next number's line
        # a small picture set inside the number's own line can rise above it
        if inline(r, hr): return True
        if top <= mid < nb: return r.y0 < mb + 1                 # entirely under our options: the next question's
        return prev_mb is not None and mid < top and r.y0 >= prev_mb + 1 and r.y0 > max(prev_tops)   # … and the same for us
    own_c = [c for c in lay['comps'] if inband(c)]
    for_c = [c for c in lay['comps'] if not inband(c)]
    own_w, for_w = [], []
    for ws in lines.values():
        main = is_main(ws)
        lone_num = len(ws) == 1 and re.fullmatch(r'\d{1,3}', ws[0][4]) and (ws[0][1] > H - 90 or ws[0][3] < 90)
        run_head = max(w[3] for w in ws) < 95 and all(re.fullmatch(r'\d{1,3}', w[4]) or w[4].upper() == 'SĄLYGOS' for w in ws) and any(w[4].upper() == 'SĄLYGOS' for w in ws)
        run_head = max(w[3] for w in ws) < 95 and all(re.fullmatch(r'\d{1,3}', w[4]) or w[4].upper() == 'SĄLYGOS' for w in ws) and any(w[4].upper() == 'SĄLYGOS' for w in ws)
        for w in ws:
            r = fitz.Rect(w[:4])
            on_own = any((c + (-10, -14, 10, 14)).intersects(r) for c in own_c)
            on_for = any((c + (-14, -16, 14, 16)).intersects(r) for c in for_c)
            head = r.y1 < 95 and w[4].upper() == 'SĄLYGOS'
            above_rule = lay.get('top_rule') and r.y1 <= lay['top_rule'] + 1        # running head / page number
            if (lone_num and not on_own) or above_rule or head or run_head or run_head or (not inband(r, main) and re.fullmatch(r'[A-E]\)', w[4])): for_w.append(r)
            elif inband(r, main): (for_w if (not main and on_for and not on_own) else own_w).append(r)
            elif on_own and not main: own_w.append(r)        # a label of our picture outside the band
            else: for_w.append(r)
    mine = own_w + own_c
    if not mine: return None
    clip = fitz.Rect(min(r.x0 for r in mine) - 6, min(r.y0 for r in mine) - 5,
                     max(r.x1 for r in mine) + 6, max(r.y1 for r in mine) + 5) & page.rect
    if lay.get('top_rule') and own_w and min(r.y0 for r in own_w) > lay['top_rule']:
        clip.y0 = max(clip.y0, lay['top_rule'] + 1.5)        # nothing of a question lies above the running head's rule
    masks = [r + (-1, -1, 1, 1) for r in for_w if clip.intersects(r)]
    for c in for_c:
        if not clip.intersects(c): continue
        m = c + (-1.5, -1.5, 1.5, 1.5)
        if any(m.intersects(r) for r in own_w): continue      # never paint over our own words
        masks.append(m)
    return clip, masks

def render(page, clip, masks, path, zoom=_recrop.ZOOM):
    pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(zoom, zoom), alpha=False)
    for m in masks:
        r = m & clip
        if r.is_empty: continue
        pix.set_rect(fitz.IRect(int(r.x0 * zoom), int(r.y0 * zoom), int(r.x1 * zoom) + 1, int(r.y1 * zoom) + 1), (255, 255, 255))
    pix.save(path)
