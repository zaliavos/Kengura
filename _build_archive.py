"""End-to-end builder: questions + answers + solutions + figures.

Strategy:
  • For each year that has a solution PDF, parse the "Bičiulio užduočių
    sąlygos" section out of the solution PDF — it's the cleanest source of
    all 30 questions.
  • If no clean conditions section is found, fall back to the matching
    competition PDF (the original test paper).
  • Answer keys and per-question solution text are pulled from the
    solution PDF using both the modern table format and the older
    "B<num>. <letter>" format.
  • Each question is also rendered as a clipped PNG of the page region in
    the solution PDF where it appears, so the original figures (which can
    not be reproduced from text alone) come along.

Output:
  • kengura-archive.js            — embeds questions + answers + solutions
  • figures/<year>-q<num>.png     — page-level images per question
"""
import sys, io, os, re, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pdfplumber
import fitz  # pymupdf, for rendering pages as images

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _extract as E
import _extract_solutions as S

# ---- file mappings ----------------------------------------------------------

SOLUTION_FILES = S.SOLUTION_FILES   # year -> filename of solution PDF

# competition PDF per year (used when no solution PDF gives sąlygos section)
COMPETITION_FILES = {
    "2000": "2000LT.pdf", "2001": "2001LT.pdf", "2002": "2002LT.pdf",
    "2003": "2003LT.pdf", "2004": "2004LT.pdf", "2005": "2005LT.pdf",
    "2006": "2006LT.pdf", "2007": "2007LT.pdf", "2008": "2008LT.pdf",
    "2009": "TMK09_lietuviu.pdf", "2010": "TMK10_lietuviu.pdf",
    "2011": "TMK11_lietuviu.pdf", "2012": "TMK12_lietuviu (1).pdf",
    "2013": "benjamin_lt (9).pdf", "2014": "benjamin_lt (8).pdf",
    "2015": "benjamin_lt (7).pdf", "2016": "benjamin_lt (6).pdf",
    "2017": "benjamin_lt (5).pdf", "2018": "benjamin_lt (4).pdf",
    "2019": "benjamin_lt (3).pdf", "2020": "benjamin_lt (2).pdf",
    "2021": "benjamin_lt (1).pdf", "2022": "benjamin_lt.pdf",
    "2023": "benjamin_lt (10).pdf", "2024": "benjamin_lt (11).pdf",
    "2025": "benjamin_lt (12).pdf",
}


# ---- conditions extraction --------------------------------------------------

# Markers that introduce the conditions section (questions only, no solutions)
SALYGOS_PATTERNS = [
    r'(?:[Bb]i[čc]iulio|BI[ČC]IULIO)[^\n]{0,60}užduočių\s+sąlygos',
    r'(?:[Bb]i[čc]iulio|BI[ČC]IULIO)[^\n]{0,60}klausimai',
    r'KLAUSIMAI\s+PO\s+3\s+TA[ŠS]KUS',
    r'Klausimai\s+po\s+3\s+ta[šs]kus',
]
SPRENDIMAI_PATTERNS = [
    r'(?:[Bb]i[čc]iulio|BI[ČC]IULIO)[^\n]{0,60}užduočių\s+sprendimai',
    r'Užduočių\s+sprendimai\b',
    r'SPRENDIMAI\b',
]


def find_match_after(text, patterns, after=0):
    for p in patterns:
        for m in re.finditer(p, text):
            if m.start() >= after:
                return m
    return None


def extract_conditions(full_text):
    """Return a substring containing just the question conditions (no
    solutions, no preface) or None if no clean section is identified."""
    # 1) Find a sąlygos header.  On modern PDFs the table-of-contents
    #    occupies first ~600 chars; we skip past it.
    salygos = find_match_after(full_text, SALYGOS_PATTERNS, after=600)
    if not salygos:
        return None
    sprendimai = find_match_after(full_text, SPRENDIMAI_PATTERNS, after=salygos.end())
    end = sprendimai.start() if sprendimai else len(full_text)
    return full_text[salygos.end():end]


# ---- per-question figures ---------------------------------------------------

FIG_DIR = os.path.join(HERE, "figures")


def render_question_figures(year, sol_pdf_path, qnums_with_pos):
    """Render the page region of each question into figures/<year>-qN.png.

    qnums_with_pos: list of (num, char_position) — char_position is the
    offset within full_text of the question's "N." marker.  We use page
    boundaries (joined with "\\n") to determine which page each question
    is on, then render that whole page as a PNG.

    Returns list of {num, file, page} entries describing what's rendered.
    """
    if not qnums_with_pos:
        return []
    os.makedirs(FIG_DIR, exist_ok=True)
    # build page offset list: cumulative char counts after cleaning
    page_texts = []
    with pdfplumber.open(sol_pdf_path) as d:
        for p in d.pages:
            page_texts.append(E.extract_page_text(p))
    # Reconstruct full text in the same way as the caller did, so that
    # offsets line up.  We assume the caller used "\n".join on the cleaned
    # page texts.
    cum = []
    n = 0
    for t in page_texts:
        cum.append(n)
        n += len(t) + 1   # +1 for the joining "\n"

    def page_for_offset(off):
        # find largest cum[i] <= off
        for i in range(len(cum)-1, -1, -1):
            if cum[i] <= off:
                return i
        return 0

    # Use PyMuPDF to find each "{num}." marker's bounding box on the page
    # where it lives, then crop a region from that y-coord down to the
    # next question marker (or the page bottom).  This gives a per-question
    # figure that includes the prompt, options, AND any inline drawings.
    out = []
    doc = fitz.open(sol_pdf_path)

    # Pre-locate each question marker on its page.
    marker_locations = {}  # num -> (page_idx, y_top, y_bottom_of_marker)
    for num in {n for n, _ in qnums_with_pos}:
        for page_idx, page_text in enumerate(page_texts):
            if not re.search(rf'(?<!\d){num}\.\s', page_text):
                continue
            page = doc[page_idx]
            # search variants: "{num}."   ", {num}."   etc.
            rects = page.search_for(f"{num}.")
            if not rects:
                continue
            # Among rects on a page, pick the one whose preceding text on
            # the line is empty/whitespace (this is the actual question
            # numbering, not a citation like ".12.").  Heuristic: choose the
            # left-most one near the left margin.
            rects.sort(key=lambda r: (r.x0, r.y0))
            chosen = rects[0]
            for r in rects:
                if r.x0 < page.rect.width * 0.18:
                    chosen = r; break
            marker_locations[num] = (page_idx, chosen.y0, chosen.y1)
            break

    for num, _ in qnums_with_pos:
        loc = marker_locations.get(num)
        if not loc:
            continue
        page_idx, y_top, _ = loc
        page = doc[page_idx]
        page_w, page_h = page.rect.width, page.rect.height
        # find next question marker on same page
        same_page = sorted([(n, info[1]) for n, info in marker_locations.items()
                             if info[0] == page_idx and info[1] > y_top + 1])
        y_bot = same_page[0][1] - 4 if same_page else page_h - 20
        # add a small upper margin
        y0 = max(0, y_top - 6)
        clip_rect = fitz.Rect(0, y0, page_w, y_bot)
        rel = f"figures/{year}-q{num}.png"
        full = os.path.join(HERE, rel.replace("/", os.sep))
        if not os.path.exists(full):
            pix = page.get_pixmap(dpi=140, clip=clip_rect)
            pix.save(full)
        out.append({"num": num, "file": rel, "page": page_idx + 1})
    doc.close()
    return out


# ---- main pipeline ----------------------------------------------------------

def load_full(path):
    with pdfplumber.open(path) as d:
        return "\n".join(E.extract_page_text(p) for p in d.pages)


def load_full_naive(path):
    """Naive extraction (no column split). Used as a fallback source for
    questions that the column-aware pass missed (e.g. when a question's
    number marker landed in the gap between split halves)."""
    with pdfplumber.open(path) as d:
        return "\n".join(E.clean(p.extract_text() or "") for p in d.pages)


def parse_questions_anywhere(text, max_count=30):
    """Try plain and B-prefix parsing, return whichever gives more results."""
    a = E.parse_questions(text, prefix="")
    b = E.parse_questions(text, prefix="B")
    out = a if len(a) >= len(b) else b
    return out


def question_quality(q):
    """Higher score = cleaner question. Used to pick between two parses."""
    score = 0
    opts = q.get("options", {})
    placeholders = sum(1 for v in opts.values() if v.startswith('('))
    score -= placeholders * 5
    bleed = sum(1 for v in opts.values() if len(v) > 50 and not v.startswith('('))
    score -= bleed * 3
    real = sum(1 for v in opts.values() if v and not v.startswith('('))
    score += real * 2
    p = q.get("prompt", "")
    if 30 <= len(p) <= 400:
        score += 5
    if re.search(r'\b[BCDE]\)\s', p):
        score -= 5
    if p.count('?') >= 2:
        score -= 2
    return score


def merge_question_sets(primary, *fallbacks):
    """Take the highest-quality version of each question across multiple
    parsings.  primary is column-aware; fallbacks are naive/sliced."""
    by_num = {}
    for source in (primary,) + fallbacks:
        for q in source:
            n = q["num"]
            if n not in by_num or question_quality(q) > question_quality(by_num[n]):
                by_num[n] = q
    return [by_num[k] for k in sorted(by_num)]


def build():
    archive = []
    for year, comp_file in sorted(COMPETITION_FILES.items()):
        comp_path = os.path.join(HERE, comp_file)
        sol_file = SOLUTION_FILES.get_year_file(year) if hasattr(SOLUTION_FILES, "get_year_file") else None
        # SOLUTION_FILES is filename->year; invert
        sol_for_year = next((f for f, y in SOLUTION_FILES.items() if y == year), None)
        sol_path = os.path.join(HERE, sol_for_year) if sol_for_year else None

        # 1) Load full text(s) — both column-aware and naive, so we can fill
        #    in questions whose number marker landed in a column gap.
        comp_full = load_full(comp_path) if os.path.exists(comp_path) else ""
        comp_naive = load_full_naive(comp_path) if os.path.exists(comp_path) else ""
        sol_full = load_full(sol_path) if sol_path and os.path.exists(sol_path) else ""
        sol_naive = load_full_naive(sol_path) if sol_path and os.path.exists(sol_path) else ""

        # 2) Try to use solution PDF's conditions section as primary source
        questions = []
        used_source = ""
        if sol_full:
            cond = extract_conditions(sol_full)
            cond_naive = extract_conditions(sol_naive) if sol_naive else None
            if cond:
                qs = parse_questions_anywhere(cond)
                qs_naive = parse_questions_anywhere(cond_naive) if cond_naive else []
                qs = merge_question_sets(qs, qs_naive)
                if len(qs) >= 20:
                    questions = qs
                    used_source = sol_for_year + " (sąlygos)"

        # 3) Fall back to competition PDF
        if not questions and comp_full:
            qs = parse_questions_anywhere(comp_full)
            qs_naive = parse_questions_anywhere(comp_naive) if comp_naive else []
            qs = merge_question_sets(qs, qs_naive)
            if len(qs) >= 5:
                questions = qs
                used_source = comp_file
            else:
                # try slice
                sl = E.extract_benjamin_slice(comp_full)
                if sl:
                    qs = parse_questions_anywhere(sl)
                    if len(qs) >= 5:
                        questions = qs
                        used_source = comp_file + " (slice)"

        if not questions:
            print(f"-- {year}: no questions extracted", file=sys.stderr)
            continue

        # 4) Sort by num and dedupe
        seen = set()
        clean_qs = []
        for q in sorted(questions, key=lambda x: x["num"]):
            if q["num"] in seen:
                continue
            seen.add(q["num"])
            clean_qs.append(q)
        questions = clean_qs

        # 5) Merge in answer keys + solutions
        if sol_full:
            table = S.parse_table(sol_full)
            blocks_b = S.parse_per_q(sol_full, use_b_prefix=True)
            blocks_p = S.parse_per_q(sol_full, use_b_prefix=False)
            blocks = blocks_b if len(blocks_b) >= len(blocks_p) else blocks_p
            for q in questions:
                n = q["num"]
                if n in table:
                    q["correct"] = table[n]
                if n in blocks:
                    if "correct" not in q:
                        q["correct"] = blocks[n]["correct"]
                    q["solution"] = blocks[n]["solution"]

        # 6) Render figure per question (page-level image from solution PDF)
        figures = []
        if sol_path and os.path.exists(sol_path):
            try:
                figures = render_question_figures(year, sol_path,
                    [(q["num"], 0) for q in questions])
            except Exception as exc:
                print(f"!! {year} figures: {exc}", file=sys.stderr)
        # attach figure file path to each question
        fig_by_num = {f["num"]: f["file"] for f in figures}
        for q in questions:
            if q["num"] in fig_by_num:
                q["figure"] = fig_by_num[q["num"]]

        title_pdf = sol_for_year or comp_file
        archive.append({
            "year": year,
            "title": f"Kengūra {year} · Bičiulis (5–6 kl.)",
            "test_pdf": comp_file if os.path.exists(comp_path) else None,
            "solutions_pdf": sol_for_year,
            "count": len(questions),
            "source": used_source,
            "questions": questions,
        })
        n_ans = sum(1 for q in questions if q.get("correct"))
        n_sol = sum(1 for q in questions if q.get("solution"))
        n_fig = sum(1 for q in questions if q.get("figure"))
        print(f"OK {year}  q={len(questions):>2d}  ans={n_ans:>2d}  sol={n_sol:>2d}  fig={n_fig:>2d}  src={used_source}", file=sys.stderr)

    # Save archive JSON
    out_json = os.path.join(HERE, "kengura-archive.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"archive": archive}, f, ensure_ascii=False, indent=1)

    # Save embeddable JS (compact)
    out_js = os.path.join(HERE, "kengura-archive.js")
    with open(out_js, "w", encoding="utf-8") as f:
        f.write("window.KENGURA_ARCHIVE = ")
        json.dump({"archive": archive}, f, ensure_ascii=False, separators=(',', ':'))
        f.write(";\n")

    total_q = sum(t["count"] for t in archive)
    print(f"\nDone.  Years={len(archive)}  Questions={total_q}", file=sys.stderr)


if __name__ == "__main__":
    build()
