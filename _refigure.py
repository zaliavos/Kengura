"""Re-render question figures from the correct source PDFs for years
2000-2005, 2007-2009 (and the Q1-Q6 of 2013/2018) where the original
build pulled figures from solution / wrong-section pages.

Strategy per year:
  - Open the test PDF (or compendium for years that have no dedicated test).
  - Find the BIČIULIS section by looking for the heading and the next
    section heading. Restrict figure search to that page range.
  - Try "Bn." markers first (used in compendiums); if too few found,
    fall back to plain "n." markers within the Bičiulis page range.
  - For each marker, locate its rect on the page using PyMuPDF and crop
    a region down to the next marker on the same page (or page bottom).
  - Save as figures/{year}-q{n}.png, OVERWRITING the bad existing file.
"""
import sys, io, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pdfplumber
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _extract as E

FIG_DIR = os.path.join(HERE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


def cleaned_pages(pdf_path):
    """Return per-page cleaned text using pdfplumber (handles combining
    diacritics so 'Bicˇiulis' becomes 'Bičiulis')."""
    out = []
    with pdfplumber.open(pdf_path) as d:
        for p in d.pages:
            out.append(E.extract_page_text(p) or "")
    return out

# year -> (test PDF, marker_mode)
#   marker_mode: 'B' -> use "Bn." markers
#                'plain' -> use bare "n." markers within Bičiulis section
#                'auto' -> try B first, fall back to plain
SOURCES = {
    "2000": ("2000LT.pdf",        "auto"),
    "2001": ("2001LT.pdf",        "auto"),
    "2002": ("2002LT.pdf",        "auto"),
    "2003": ("2003LT.pdf",        "plain"),  # plain numbering inside Bičiulis
    "2004": ("2004LT.pdf",        "auto"),
    "2005": ("2005LT.pdf",        "auto"),
    "2006": ("2006LT.pdf",        "auto"),
    "2007": ("2007kengura.pdf",   "auto"),
    "2008": ("2008LT.pdf",        "auto"),
    "2009": ("TMK09_lietuviu.pdf","plain"),
}

# Section header regexes
BICI_RE = re.compile(r'BI[ČC]IULIS|Bi[čc]iulis')
NEXT_SECTION_RE = re.compile(r'KADETAS|Kadetas|JUNIORAS|Junioras|STUDENTAS|Studentas|SENJORAS|Senjoras|TURINYS|Atsakymai|Sprendimai')


def find_bici_pages(doc, pdf_path):
    """Return (start_page_idx, end_page_idx_exclusive) for the Bičiulis
    questions section. Uses pdfplumber's cleaned text to detect section
    headings (handles 'Bicˇiulis' style raw extraction). The body section
    is identified as the page where Bičiulis header sits ABOVE a question
    "1." marker (skips TOC entries)."""
    pages = cleaned_pages(pdf_path)
    bici_pages = [i for i, t in enumerate(pages) if BICI_RE.search(t)]
    next_pages = [i for i, t in enumerate(pages) if NEXT_SECTION_RE.search(t)]
    if not bici_pages:
        return 0, len(doc)
    # Pick a Bičiulis-marked page that ALSO contains "1." in its body
    # (the TOC has Bičiulis but no question 1).
    start = None
    for b in bici_pages:
        if re.search(r'(?m)^\s*(?:B\s*)?1\.\s', pages[b]):
            start = b
            break
        # or a 1. marker on the next 1-2 pages (header on its own page)
        for j in (b+1, b+2):
            if j < len(pages) and re.search(r'(?m)^\s*(?:B\s*)?1\.\s', pages[j]):
                start = b
                break
        if start is not None:
            break
    if start is None:
        start = bici_pages[0]
    # End = next non-Bičiulis section page after start
    end = len(doc)
    for n in next_pages:
        if n > start:
            end = n
            break
    return start, end


def find_question_rects(doc, page_range, mode):
    """Return {num: (page_idx, rect)} for question markers in the given page range.

    - 'B' mode: searches for "Bn." literal
    - 'plain' mode: searches for "n." at left margin
    - 'auto': try B, fall back to plain if <10 found
    """
    def search_b(rng):
        out = {}
        for page_idx in rng:
            page = doc[page_idx]
            text = page.get_text() or ""
            for n in range(1, 31):
                if n in out:
                    continue
                if not re.search(rf'\bB\s*{n}\.', text):
                    continue
                # Try several literal forms
                for q in (f"B{n}.", f"B {n}.", f"B.{n}.", f"B{n} ."):
                    rects = page.search_for(q)
                    if rects:
                        rects.sort(key=lambda r: (r.y0, r.x0))
                        out[n] = (page_idx, rects[0])
                        break
        return out

    def search_plain(rng):
        out = {}
        for page_idx in rng:
            page = doc[page_idx]
            page_w = page.rect.width
            text = page.get_text() or ""
            for n in range(1, 31):
                if n in out:
                    continue
                if not re.search(rf'(?m)^\s*{n}\.\s', text):
                    continue
                rects = page.search_for(f"{n}.")
                if not rects:
                    continue
                # filter to left-of-page-margin rects (avoid in-line refs)
                left_rects = [r for r in rects if r.x0 < page_w * 0.55]
                if not left_rects:
                    left_rects = rects
                # prefer the rect whose y0 is smallest (top of page)
                left_rects.sort(key=lambda r: (r.y0, r.x0))
                out[n] = (page_idx, left_rects[0])
        return out

    rng = list(range(*page_range))
    if mode == 'B':
        return search_b(rng)
    if mode == 'plain':
        return search_plain(rng)
    # auto
    out = search_b(rng)
    if len(out) < 10:
        out = search_plain(rng)
    return out


def render_year(year, force=False):
    if year not in SOURCES:
        return 0, 0
    pdf_name, mode = SOURCES[year]
    pdf_path = os.path.join(HERE, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"!! {year}: source PDF missing: {pdf_path}", file=sys.stderr)
        return 0, 0
    doc = fitz.open(pdf_path)
    try:
        page_range = find_bici_pages(doc, pdf_path)
        rects = find_question_rects(doc, page_range, mode)
        rendered = 0
        # Group rects by page so we can find each question's bottom y
        per_page = {}
        for n, (pidx, r) in rects.items():
            per_page.setdefault(pidx, []).append((n, r))
        for pidx, items in per_page.items():
            items.sort(key=lambda x: x[1].y0)
            page = doc[pidx]
            page_w, page_h = page.rect.width, page.rect.height
            for k, (n, r) in enumerate(items):
                y_top = max(0, r.y0 - 6)
                y_bot = items[k+1][1].y0 - 4 if k+1 < len(items) else page_h - 20
                if y_bot - y_top < 25:  # too small, extend
                    y_bot = page_h - 20
                clip = fitz.Rect(0, y_top, page_w, y_bot)
                rel = f"figures/{year}-q{n}.png"
                full = os.path.join(HERE, rel.replace("/", os.sep))
                if not force and not os.path.exists(full):
                    pass  # render below
                pix = page.get_pixmap(dpi=140, clip=clip)
                pix.save(full)
                rendered += 1
        return rendered, len(rects)
    finally:
        doc.close()


# ---- 2013 / 2018 special-case: re-render Q1-Q6 from benjamin_lt landscape ----

LANDSCAPE_OVERRIDES = {
    "2013": ("benjamin_lt (9).pdf", [1, 2, 3, 4, 5, 6]),
    "2018": ("benjamin_lt (4).pdf", [1, 2, 3, 4, 5, 6]),
    # 2014-2017: full 30 questions (no figures existed before)
    "2014": ("benjamin_lt (8).pdf", list(range(1, 31))),
    "2015": ("benjamin_lt (7).pdf", list(range(1, 31))),
    "2016": ("benjamin_lt (6).pdf", list(range(1, 31))),
    "2017": ("benjamin_lt (5).pdf", list(range(1, 31))),
}


def _strict_question_markers(page):
    """Return [(n, x0, y0, x1, y1)] for actual question-number markers on
    a landscape booklet page. A marker is a 'N.' word that is NOT preceded
    by a digit on the same line (filters out 25.→5., 28.→8., etc.)."""
    words = page.get_text("words")
    out = []
    for w in words:
        x0, y0, x1, y1, txt, *_ = w
        m = re.fullmatch(r'(\d{1,2})\.', txt)
        if not m:
            continue
        n = int(m.group(1))
        if not 1 <= n <= 30:
            continue
        # check preceding token immediately to the left (same column),
        # not far across the page in another column
        prev = [v for v in words
                if abs(v[1] - y0) < 3 and v[0] < x0 and (x0 - v[2]) < 12]
        if prev:
            prev.sort(key=lambda v: -v[0])
            ptxt = prev[0][4]
            if re.search(r'\d$', ptxt):
                continue
        out.append((n, x0, y0, x1, y1))
    return out


def render_landscape_year(year):
    pdf_name, qnums = LANDSCAPE_OVERRIDES[year]
    pdf_path = os.path.join(HERE, pdf_name)
    if not os.path.exists(pdf_path):
        print(f"!! {year}: source PDF missing: {pdf_path}", file=sys.stderr)
        return 0, 0
    doc = fitz.open(pdf_path)
    try:
        rendered = 0
        located = 0
        seen_q = set()
        for pidx in range(len(doc)):
            page = doc[pidx]
            page_w, page_h = page.rect.width, page.rect.height
            markers = _strict_question_markers(page)
            if not markers:
                continue
            # Cluster markers into columns by x0. We greedily collect
            # cluster centers in left-to-right order, then keep ONLY clusters
            # with >= 3 markers (a real question column has many).
            sorted_markers = sorted(markers, key=lambda m: m[1])
            cluster_centers = []
            for m in sorted_markers:
                if not cluster_centers or m[1] - cluster_centers[-1] > 40:
                    cluster_centers.append(m[1])
            columns = []
            for cx in cluster_centers:
                col = [m for m in markers if abs(m[1] - cx) < 40]
                if len(col) >= 3:
                    columns.append(sorted(col, key=lambda m: m[2]))
            # Render each requested qnum
            for col in columns:
                # x-range of the column: from this col's x0 to next col's x0
                col_x0 = max(0, col[0][1] - 6)
                col_x_right = page_w
                for other in columns:
                    if other is col:
                        continue
                    if other[0][1] > col[0][1] + 10:
                        col_x_right = min(col_x_right, other[0][1] - 4)
                for k, (n, x0, y0, x1, y1) in enumerate(col):
                    if n not in qnums or n in seen_q:
                        continue
                    y_top = max(0, y0 - 6)
                    y_bot = (col[k+1][2] - 4) if k+1 < len(col) else (page_h - 20)
                    clip = fitz.Rect(col_x0, y_top, col_x_right, y_bot)
                    rel = f"figures/{year}-q{n}.png"
                    full = os.path.join(HERE, rel.replace("/", os.sep))
                    pix = page.get_pixmap(dpi=160, clip=clip)
                    pix.save(full)
                    rendered += 1
                    located += 1
                    seen_q.add(n)
        return rendered, located
    finally:
        doc.close()


def main():
    summary = {}
    for year in sorted(SOURCES):
        rendered, located = render_year(year, force=True)
        summary[year] = (rendered, located)
        print(f"{year}: rendered {rendered} / located {located}", file=sys.stderr)
    for year in sorted(LANDSCAPE_OVERRIDES):
        rendered, located = render_landscape_year(year)
        summary[year + " (Q1-6)"] = (rendered, located)
        print(f"{year} Q1-6: rendered {rendered} / located {located}", file=sys.stderr)
    return summary


if __name__ == "__main__":
    main()
