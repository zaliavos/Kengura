"""Trim blank rows above and below every figure (keeps a 12 px margin).

Some crops ran to the bottom of the page or column (2000-30 was 811 of 890
px empty), which pushed the options far below the question on a phone.
Only all-white rows are removed, so no content can be lost. Run with plain
python (PyMuPDF). Bump FIGS in sw.js afterwards.
"""
import fitz, glob, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MARGIN = 12

def blank_rows(pm):
    w, h, n, s = pm.width, pm.height, pm.n, pm.samples
    def blank(r):
        base = r * w * n
        for x in range(0, w, 2):
            i = base + x * n
            if s[i] + s[i + 1] + s[i + 2] < 3 * 200: return False
        return True
    top = 0
    while top < h and blank(top): top += 1
    bot = 0
    while bot < h - top and blank(h - 1 - bot): bot += 1
    return top, bot

changed = 0
for path in sorted(glob.glob(os.path.join(HERE, 'figures', '*.png'))):
    pm = fitz.Pixmap(path)
    if pm.alpha or pm.n >= 4: pm = fitz.Pixmap(fitz.csRGB, pm)
    top, bot = blank_rows(pm)
    cut_t, cut_b = max(0, top - MARGIN), max(0, bot - MARGIN)
    if cut_t + cut_b < 8: continue
    doc = fitz.open(path)
    page = doc[0]
    sx = page.rect.width / pm.width; sy = page.rect.height / pm.height
    clip = fitz.Rect(0, cut_t * sy, page.rect.width, (pm.height - cut_b) * sy)
    out = page.get_pixmap(clip=clip, matrix=fitz.Matrix(1 / sx, 1 / sy))
    doc.close()
    out.save(path)
    changed += 1
print('trimmed', changed)
