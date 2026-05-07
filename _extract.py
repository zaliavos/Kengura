"""Extract Kangaroo Benjamin (5–6 kl.) questions from local PDFs.

Recovers Lithuanian diacritics from (cid:NN) markers and classifies each
question into a pattern type matching the in-app quiz generators.

Outputs: kengura-archive.json next to this script.
"""
import re, json, os, sys, glob

import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))

# CID -> Lithuanian char.  Each cid is a combining mark that attaches to its
# adjacent base letter.  Position varies (sometimes before, sometimes after
# the base letter) depending on font kerning, so we try both directions.
CID_RULES = [
    # caron
    (r'\(cid:7\)\s*s', 'š'), (r's\s*\(cid:7\)', 'š'),
    (r'\(cid:7\)\s*S', 'Š'), (r'S\s*\(cid:7\)', 'Š'),
    (r'\(cid:7\)\s*c', 'č'), (r'c\s*\(cid:7\)', 'č'),
    (r'\(cid:7\)\s*C', 'Č'), (r'C\s*\(cid:7\)', 'Č'),
    (r'\(cid:7\)\s*z', 'ž'), (r'z\s*\(cid:7\)', 'ž'),
    (r'\(cid:7\)\s*Z', 'Ž'), (r'Z\s*\(cid:7\)', 'Ž'),
    # macron (only ū in Lithuanian)
    (r'u\s*\(cid:9\)', 'ū'), (r'\(cid:9\)\s*u', 'ū'),
    (r'U\s*\(cid:9\)', 'Ū'), (r'\(cid:9\)\s*U', 'Ū'),
    # dot above (only ė)
    (r'e\s*\(cid:10\)', 'ė'), (r'\(cid:10\)\s*e', 'ė'),
    (r'E\s*\(cid:10\)', 'Ė'), (r'\(cid:10\)\s*E', 'Ė'),
    # ogonek (ą/ę/į/ų)
    (r'a\s*\(cid:12\)', 'ą'), (r'\(cid:12\)\s*a', 'ą'),
    (r'A\s*\(cid:12\)', 'Ą'), (r'\(cid:12\)\s*A', 'Ą'),
    (r'e\s*\(cid:12\)', 'ę'), (r'\(cid:12\)\s*e', 'ę'),
    (r'E\s*\(cid:12\)', 'Ę'), (r'\(cid:12\)\s*E', 'Ę'),
    (r'i\s*\(cid:12\)', 'į'), (r'\(cid:12\)\s*i', 'į'),
    (r'I\s*\(cid:12\)', 'Į'), (r'\(cid:12\)\s*I', 'Į'),
    (r'u\s*\(cid:12\)', 'ų'), (r'\(cid:12\)\s*u', 'ų'),
    (r'U\s*\(cid:12\)', 'Ų'), (r'\(cid:12\)\s*U', 'Ų'),
    # dashes / misc
    (r'\(cid:21\)', '–'),
    (r'\(cid:13\)', ' '),
    (r'\(cid:24\)', '"'),
    (r'\(cid:25\)', '"'),
]

# Some PDFs (2000–2008 series) emit literal combining diacritics rather
# than (cid:N) markers, e.g. "cˇ" for č, "u¯" for ū, "a˛" for ą.
COMBINING_RULES = [
    ('cˇ', 'č'), ('Cˇ', 'Č'),
    ('sˇ', 'š'), ('Sˇ', 'Š'),
    ('zˇ', 'ž'), ('Zˇ', 'Ž'),
    ('u¯', 'ū'), ('U¯', 'Ū'),
    ('e˙', 'ė'), ('E˙', 'Ė'),
    ('a˛', 'ą'), ('A˛', 'Ą'),
    ('e˛', 'ę'), ('E˛', 'Ę'),
    ('i˛', 'į'), ('I˛', 'Į'),
    ('u˛', 'ų'), ('U˛', 'Ų'),
    # standalone leading diacritic right at start of word, e.g. "ˇsvietimo"
    ('ˇs', 'š'), ('ˇc', 'č'), ('ˇz', 'ž'),
    ('ˇS', 'Š'), ('ˇC', 'Č'), ('ˇZ', 'Ž'),
]


def clean(text: str) -> str:
    if not text:
        return ""
    out = text
    for pat, rep in CID_RULES:
        out = re.sub(pat, rep, out)
    out = re.sub(r'\(cid:\d+\)', '', out)
    for src, dst in COMBINING_RULES:
        out = out.replace(src, dst)
    # tidy whitespace
    out = re.sub(r'[ \t]+', ' ', out)
    out = re.sub(r' *\n *', '\n', out)
    return out.strip()


def extract_page_text(page) -> str:
    """Extract a page's text, handling 2-up landscape booklet layouts.

    Kengūra PDFs from 2014-2020 and 2023-2025 are imposed as A4-landscape
    sheets with two A5 pages side-by-side. pdfplumber's default extraction
    interleaves the columns, mashing two questions' text together. For
    those pages we crop into halves and extract each independently."""
    w, h = page.width, page.height
    if w > h and w > 700:
        left = page.crop((0, 0, w / 2, h)).extract_text() or ""
        right = page.crop((w / 2, 0, w, h)).extract_text() or ""
        return clean(left) + "\n" + clean(right)
    return clean(page.extract_text() or "")


# section headers in old-style compendium PDFs
SECTION_RE = re.compile(
    r'(MA[ŽZ]YLIS|BI[ČC]IULIS|KADETAS|JUNIORAS|STUDENTAS)\b',
    re.IGNORECASE,
)


def _norm(s: str) -> str:
    return s.upper().replace('Č', 'C').replace('Ž', 'Z')


def extract_benjamin_slice(text: str):
    """Return the Bičiulis (5–6 kl.) section.  We slice from the FIRST
    Bičiulis header to the first non-Bičiulis section header following it
    (Kadetas/Junioras/Studentas).  Returns None if no Bičiulis is found."""
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return None
    start = None
    end = len(text)
    for i, m in enumerate(matches):
        if 'BICIULIS' in _norm(m.group(1)) and start is None:
            start = m.end()
        elif start is not None and 'BICIULIS' not in _norm(m.group(1)):
            end = m.start()
            break
    if start is None:
        return None
    return text[start:end]


# ---------- pattern classification ----------------------------------------
# Match each question against keyword rules.  Each rule has a list of
# trigger keywords/regex.  We assign ALL matching pattern tags so a problem
# can carry multiple labels (e.g., logic + counting).
PATTERN_RULES = [
    ("aritmetika",   ["sumav", "padaugin", "dauginimas", "atim", "padalink",
                       "skaičiuokli", "skaičiuokl", "sandauga", "skaitmen",
                       "skaičius", "kiek lygu", "lygyb", "pridėj", "atimt"]),
    ("geometrija",   ["plot", "perimet", "kvadrat", "trikamp", "stačiakamp",
                       "lygiagretain", "skritul", "apskritim", "kamp.+laips",
                       "kraštin", "tūr", "spindul", "diagonal", "įstrižain",
                       "pjūv", "rombas", "trapez", "veidrod"]),
    ("logika",       ["taisykl", "logišk", "teisinga.+jeigu", "pasakyti",
                       "iš kurių.+teisi", "kas teisinga", "ar gal", "spalv",
                       "melagi", "tiesos", "paslėp"]),
    ("skaiciavimas", ["kiek.+(yra|gali|skaič|būd)", "kiek mažiausiai",
                       "kiek daugiausi", "iš viso", "skaičiuoti", "skaičiuokim"]),
    ("erdve",        ["kub", "lokšt", "tinkl", "lygiagretain", "išklotin",
                       "iš trij.+pus", "matomą", "iš viršaus", "iš šono",
                       "atspindys", "veidrod", "paguld"]),
    ("uzdaviniai",   ["valand", "minu", "greit", "kelion", "automobil",
                       "amžiu", "metai", "diena", "savait", "mėnes",
                       "kaina", "litai", "eur", "centai", "pinig",
                       "vidurk", "klas", "mokin"]),
    ("seka",         ["seka", "sekoje", "kuris.+toliau", "kitas.+narys",
                       "tęsia", "po skaičiaus", "kitą skaičių"]),
    ("paveikslelis", ["paveiksl", "brėžin", "figūr", "atvaizd", "rodykl"]),
]

def classify(prompt: str):
    p = prompt.lower()
    tags = []
    for tag, kws in PATTERN_RULES:
        for kw in kws:
            if re.search(kw, p):
                tags.append(tag)
                break
    if not tags:
        tags = ["uzdaviniai"]
    # preserve order, dedupe
    out = []
    for t in tags:
        if t not in out:
            out.append(t)
    return out


# ---------- question splitting --------------------------------------------
# Heuristic: lines starting with "<num>. " where num in 1..30 begin a
# question.  Options A) B) C) D) E) come after.  Answer keys are NOT in
# the test PDFs themselves.

# Match option labels.  Two formats are common:
#   strict:  "A) val", "A. val"   — modern PDFs
#   bare:    "A val"              — 2007 compendium
# The strict form is preferred because bare letters can falsely match prompt
# fragments like "raidėmis A, B, C, D ir E".  We try strict first and fall
# back to bare only when strict yields <5 options.
OPT_RE_STRICT = re.compile(
    r'([A-E])[).]\s+'                                # label + required ) or .
    r'([^\n]{1,80}?)'                                # short value
    r'(?=\s+[A-E][).]\s+|\s*\n|\s*$)',               # next strict option or break
    re.S,
)
OPT_RE_BARE = re.compile(
    r'([A-E])(?:\)|\.)?\s+'                          # label + optional ) or .
    r'([^A-E\n]{1,80}?)'                             # short value
    r'(?=\s+[A-E](?:\)|\.)?\s+|\s*\n|\s*$)',          # next option or break
    re.S,
)
OPT_RE = OPT_RE_STRICT  # kept for callers that import OPT_RE


def _build_qnum_re(prefix: str):
    if prefix:
        # Bičiulis questions in compendiums are tagged like "B1.", "B12."
        # We allow optional space between letter and digits because the PDF
        # extractor sometimes inserts a separator.
        return re.compile(rf'(?m)^\s*{prefix}\s*(\d{{1,2}})\.\s+([^\n]+(?:\n(?!\s*{prefix}\s*\d{{1,2}}\.\s)(?!\s*Klausimai po)[^\n]*)*)')
    return re.compile(r'(?m)^\s*(\d{1,2})\.\s+([^\n]+(?:\n(?!\s*\d{1,2}\.\s)(?!\s*Klausimai po)[^\n]*)*)')


# Strings that bleed into questions from page headers / figures / TOCs
JUNK_PATTERNS = [
    r'Kengūros konkurso organizavimo komitetas[^\n]*',
    r'Lietuvos Respublikos[^\n]*',
    r'VU Matematikos[^\n]*',
    r'Leidykla\s*TEV[^\n]*',
    r'Konkurso trukmė[^\n]*',
    r'KENGŪRA\s*\d{4}[^\n]*',
    r'KENGURA\s*\d{4}[^\n]*',
    r'Klausimai po \d ta[šs]kus[^\n]*',
    r'KLAUSIMAI PO \d TA[ŠS]KUS[^\n]*',
    r'P\s*S\s*frag\s*replacements?',
    r'PSfrag\s*[a-zA-Z]*',
    r'\(V\s*ir\s*VI\s*klasės\)\s*\d*',
    r'5\s*ir\s*6\s*klasės?',
    r'Bi[čc]iulis',
    r'Ši priemonė[^\n]*',
    r'Užduotis dalyvis[^\n]*',
    r'savaranki[šs]kai',
]

def strip_junk(s: str) -> str:
    for pat in JUNK_PATTERNS:
        s = re.sub(pat, ' ', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# Standalone runs of "A B C D E" (figure labels for image-option questions)
# often bleed into the prompt when pdfplumber merges text from inline figures.
INLINE_LABEL_PATTERNS = [
    r'(?<!\w)A\s+B\s+C\s+D\s+E(?!\w)',
    r'(?<!\w)A\)\s*B\)\s*C\)\s*D\)\s*E\)(?!\w)',
    r'(?<!\w)1\s*pav\.?\s*2\s*pav\.?(?!\w)',
]

def strip_inline_labels(s: str) -> str:
    for pat in INLINE_LABEL_PATTERNS:
        s = re.sub(pat, ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def parse_questions(text: str, prefix: str = ""):
    """Return list of {num, prompt, options:{A,B,C,D,E}, points}.

    If prefix is given (e.g. "B"), only questions tagged with that prefix
    (B1., B2., …) are extracted — used for multi-grade compendium PDFs.
    """
    text = re.sub(r'\r\n', '\n', text)
    # detect points sections: "Klausimai po N taskus"
    point_sections = []
    for m in re.finditer(r'Klausimai po (\d) ta[šs]kus', text):
        point_sections.append((m.start(), int(m.group(1))))
    def points_for(pos):
        cur = 3
        for start, pts in point_sections:
            if pos >= start:
                cur = pts
        return cur

    qnum_re = _build_qnum_re(prefix)
    questions = []
    seen_nums = set()
    matches = list(qnum_re.finditer(text))
    for idx, m in enumerate(matches):
        num = int(m.group(1))
        body = m.group(2).strip()
        # First locate the start of the option block so options aren't pulled
        # out of mid-prompt fragments like "raidėmis A, B, C, D ir E".  We
        # search for the LAST occurrence of "A) " or "A. " that still has
        # B/C/D/E markers following it.
        opt_start = -1
        for am in re.finditer(r'(?:^|\s)A[).]\s', body):
            tail = body[am.start():]
            # require at least B and C labels in the tail
            if re.search(r'\sB[).]\s', tail) and re.search(r'\sC[).]\s', tail):
                opt_start = am.start()
        opt_section = body[opt_start:] if opt_start >= 0 else ""

        opts = {}
        # Strict-format pass on the option section if found, else whole body
        scan_text = opt_section if opt_section else body
        for om in OPT_RE_STRICT.finditer(scan_text):
            letter = om.group(1)
            val = om.group(2).strip()
            val = re.sub(r'\s+', ' ', val).rstrip('.,;')
            # Reject values that are just another option marker (e.g. "B)" or
            # "B" alone) — these come from image-option questions where each
            # label has no text after it.
            if re.fullmatch(r'[A-E][).]?', val):
                continue
            if not val or letter in opts or len(val) > 200:
                continue
            opts[letter] = val
        # Fallback: bare-letter format (older compendiums) — only if strict
        # found nothing AND bare yields a near-complete set.  Requiring
        # near-completeness prevents prompt fragments like "raidėmis A, B,
        # C, D ir E" from being captured as options.
        if len(opts) == 0:
            bare = {}
            for om in OPT_RE_BARE.finditer(body):
                letter = om.group(1)
                val = om.group(2).strip()
                val = re.sub(r'\s+', ' ', val).rstrip('.,;')
                if re.fullmatch(r'[A-E][).]?', val):
                    continue
                if not val or letter in bare or len(val) > 200:
                    continue
                bare[letter] = val
            if len(bare) >= 4:
                opts = bare
        # If the body genuinely lacks text options (e.g. all 5 are images)
        # fall back to placeholder so the question is still kept; the user
        # will see the original figure and can tap A–E based on the image.
        if not opts:
            opts = {l: f"({l})" for l in "ABCDE"}
        # tolerate missing letters (placeholder them)
        for letter in "ABCDE":
            opts.setdefault(letter, f"({letter})")
        if num in seen_nums and num <= 5:
            continue
        seen_nums.add(num)
        # Prompt is everything before the option block
        if opt_start > 0:
            prompt = body[:opt_start].strip()
        else:
            ai = body.find('A)')
            if ai < 0:
                ai = body.find('A ')
            prompt = body[:ai].strip() if ai > 0 else body
        prompt = strip_junk(prompt)
        prompt = strip_inline_labels(prompt)
        # Allow short prompts (>=5) to keep image-heavy questions like
        # "20·24 / (2·0+2·4) =" where the formula is mostly in the figure.
        if len(prompt) < 5 or len(prompt) > 600:
            continue

        # cleanup options (strip junk, filter garbage)
        opts = {k: strip_junk(v) for k, v in opts.items()}
        bad = sum(1 for v in opts.values() if not v or len(v) < 1 or 'PSfrag' in v.lower() or 'replaements' in v.lower())
        if bad >= 2:
            continue

        questions.append({
            "num": num,
            "prompt": prompt,
            "options": opts,
            "points": points_for(m.start()),
            "patterns": classify(prompt),
        })
    return questions


# ---------- year detection -------------------------------------------------
def detect_year(text, fname):
    m = re.search(r'KENG[ŪU]?RA\s*(\d{4})', text)
    if m:
        return m.group(1)
    m = re.search(r'(\d{4})', fname)
    if m:
        return m.group(1)
    return "?"


def is_benjamin_dedicated(text):
    """True for PDFs that contain ONLY 5–6 klasė questions."""
    return bool(re.search(r'5\s*[–-]\s*6\s*klas', text)
                and not re.search(r'\b[KJSM]\d{1,2}\.\s', text))


def has_benjamin_section(text):
    """True for compendium PDFs that include a B-prefixed section."""
    return bool(re.search(r'\bB\s*\d{1,2}\.\s', text))


def main():
    pdfs = sorted(glob.glob(os.path.join(HERE, '*.pdf')))
    archive = []
    for pdf in pdfs:
        fname = os.path.basename(pdf)
        try:
            with pdfplumber.open(pdf) as doc:
                pages = []
                for p in doc.pages:
                    t = p.extract_text() or ""
                    pages.append(clean(t))
                full = "\n".join(pages)
        except Exception as e:
            sys.stderr.write(f"!! {fname}: {e}\n")
            continue
        if not full.strip():
            sys.stderr.write(f"-- {fname}: empty\n")
            continue

        # Strategy:
        #  1. Dedicated Benjamin PDF (header says 5–6 klasė, no other levels) → "1."-style
        #  2. Compendium with B1./B2. tags (some 2010s PDFs)
        #  3. Compendium with Bičiulis section header (most 2000–2008 PDFs)
        #  4. Last-ditch: parse plain "1." numbering from whole text
        # Try every plausible parsing strategy and keep the best result.
        candidates = []  # (qs, source)

        # 1. Whole document, plain "1." numbering — works for dedicated
        #    Benjamin PDFs.
        candidates.append((parse_questions(full, prefix=""), "plain-full"))

        # 2. Whole document, B-prefixed numbering — works for some
        #    compendiums where Benjamin questions are tagged "B1.", "B2." …
        candidates.append((parse_questions(full, prefix="B"), "B-prefix-full"))

        # 3. Section slice (Bičiulis … next-section), parsed both ways.
        sliced = extract_benjamin_slice(full)
        if sliced:
            candidates.append((parse_questions(sliced, prefix=""), "slice-plain"))
            candidates.append((parse_questions(sliced, prefix="B"), "slice-B-prefix"))

        # Pick the best:
        # - prefer something that yields 18-30 questions (a real Benjamin test)
        # - else the largest non-trivial set
        in_range = [(q, s) for q, s in candidates if 18 <= len(q) <= 32]
        if in_range:
            qs, source = max(in_range, key=lambda x: len(x[0]))
        else:
            qs, source = max(candidates, key=lambda x: len(x[0]))
            if len(qs) < 10:
                qs = []

        if not qs:
            sys.stderr.write(f"-- {fname}: no Benjamin questions found — skipping\n")
            continue

        year = detect_year(full, fname)
        archive.append({
            "file": fname,
            "year": year,
            "title": f"Kengūra {year} · Bičiulis (5–6 kl.)",
            "count": len(qs),
            "source": source,
            "questions": qs,
        })
        print(f"OK  {fname}: {len(qs)} klausimų (y={year}, {source})", file=sys.stderr)

    out_path = os.path.join(HERE, "kengura-archive.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"archive": archive}, f, ensure_ascii=False, indent=1)
    print(f"\nSaved: {out_path}", file=sys.stderr)
    print(f"Tests: {len(archive)} | Total Q: {sum(t['count'] for t in archive)}", file=sys.stderr)


if __name__ == "__main__":
    main()
