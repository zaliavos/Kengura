"""Extract answer keys + per-question solutions from solution PDFs.

Two formats are supported:

  1. Modern PDFs (sp*.pdf, TMK13_B.pdf, recent spB.pdf):
        - have an "Atsakymai" table at the back: Question # | Letter
        - usually also have per-question solutions in the body

  2. Older PDFs (200*spB.pdf, 200*kengura.pdf, 201*spBK.pdf):
        - no table; instead each question has the form
              B<num>. <Letter> <answer-value>
              ! <solution paragraph>
        - We capture the letter + the paragraph that follows.

For each year we produce:
    {Q# -> {"correct": "A".."E", "solution": "..."}}

Output: kengura-keys.json next to this script.
"""
import sys, io, os, re, glob, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import pdfplumber
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _extract as E  # for clean()

# Manual filename → year map (more reliable than scraping the PDF text).
SOLUTION_FILES = {
    "2000spB.pdf": "2000",
    "2001spB.pdf": "2001",
    "2002spB.pdf": "2002",
    "2003spB.pdf": "2003",
    "2004spB.pdf": "2004",
    "2005spB.pdf": "2005",
    "2007kengura.pdf": "2007",
    "2008kengura.pdf": "2008",
    "2009kengura.pdf": "2009",
    "2010spBK.pdf": "2010",
    "2011spBK.pdf": "2011",
    "2012spBK.pdf": "2012",
    "TMK13_B.pdf":  "2013",
    "spB (7).pdf":  "2018",
    "spB (6).pdf":  "2019",
    "spB (5).pdf":  "2020",
    "spB (4).pdf":  "2021",
    "spB (3).pdf":  "2022",
    "spB (2).pdf":  "2023",
    "spB (1).pdf":  "2024",
    "spB.pdf":      "2025",
}


def parse_table(text):
    """Detect the modern 'Atsakymai' table and return {q# -> letter}."""
    m = re.search(r'Atsakymai\s*Uždavinio.{0,40}Atsakymas\s+(.+)$', text, re.S)
    if not m:
        return {}
    body = m.group(1)
    out = {}
    # Match lines or runs like "1 B" / "1) B" / "1.\nB"
    for q, letter in re.findall(r'(?:^|\s)(\d{1,2})[\.\)]?\s+([A-E])(?=\s|$)', body):
        n = int(q)
        if 1 <= n <= 30 and n not in out:
            out[n] = letter
    return out


def parse_per_q(text, use_b_prefix=False):
    """Capture per-question solution blocks.

    Two layout flavours are accepted:

      - older compendium PDFs:  ``B12. D <value>\\n<solution>``
      - modern dedicated PDFs:  ``12. D <value>\\n<solution>``

    The right pattern is selected via ``use_b_prefix``.  When ``False`` we
    additionally restrict matches to lie *after* the words "Užduočių
    sprendimai" so that we skip the table of contents and the conditions
    section that just numbers the problems without showing answers.
    """
    if use_b_prefix:
        scope = text
        head = re.compile(r'(?m)^\s*B\s*(\d{1,2})\.\s+([A-E])\b([^\n]*)')
    else:
        # in modern PDFs the *Sprendimai* (solutions) section is preceded by
        # the heading "Užduočių sprendimai" — we anchor scope from there.
        m = re.search(r'Užduočių\s+sprendimai\s*\d*\s*\n', text, re.I)
        if not m:
            scope = text
        else:
            scope = text[m.end():]
        head = re.compile(r'(?m)^\s*(\d{1,2})\.\s+([A-E])\b([^\n]*)')

    matches = list(head.finditer(scope))
    out = {}
    for i, m in enumerate(matches):
        n = int(m.group(1))
        letter = m.group(2)
        head_tail = m.group(3).strip()
        # body extends until the next match (or up to 1200 chars)
        body_start = m.end()
        body_end = matches[i+1].start() if i+1 < len(matches) else min(body_start + 1500, len(scope))
        body = scope[body_start:body_end]
        body = re.sub(r'\s+', ' ', (head_tail + ' ' + body)).strip()
        # Strip footers / page artifacts
        body = re.sub(r'\d+\s*$', '', body).strip()
        # Trim extremely long bodies
        if len(body) > 900:
            body = body[:900].rstrip() + ' …'
        if 1 <= n <= 30 and n not in out and len(body) >= 4:
            out[n] = {"correct": letter, "solution": body}
    return out


def extract_one(path, year):
    try:
        with pdfplumber.open(path) as d:
            full = "\n".join(E.clean(p.extract_text() or "") for p in d.pages)
    except Exception as exc:
        print(f"!! {path}: {exc}", file=sys.stderr)
        return None
    table = parse_table(full)
    # try both prefixes; pick whichever yields more matches
    blocks_b = parse_per_q(full, use_b_prefix=True)
    blocks_p = parse_per_q(full, use_b_prefix=False)
    blocks = blocks_b if len(blocks_b) >= len(blocks_p) else blocks_p

    answers = {}
    for n in range(1, 31):
        rec = {}
        if n in table:
            rec["correct"] = table[n]
        if n in blocks:
            if "correct" not in rec:
                rec["correct"] = blocks[n]["correct"]
            rec["solution"] = blocks[n]["solution"]
        if rec:
            answers[str(n)] = rec
    return answers


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for fname, year in SOLUTION_FILES.items():
        path = os.path.join(here, fname)
        if not os.path.exists(path):
            continue
        ans = extract_one(path, year)
        if not ans:
            print(f"-- {year} ({fname}): no answers extracted", file=sys.stderr)
            continue
        out[year] = {"file": fname, "answers": ans}
        n_ans = sum(1 for v in ans.values() if "correct" in v)
        n_sol = sum(1 for v in ans.values() if "solution" in v)
        print(f"OK {year:>4s}  src={fname:<22s}  answers={n_ans:2d}  solutions={n_sol:2d}", file=sys.stderr)

    out_path = os.path.join(here, "kengura-keys.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    total_ans = sum(sum(1 for v in y["answers"].values() if "correct" in v) for y in out.values())
    total_sol = sum(sum(1 for v in y["answers"].values() if "solution" in v) for y in out.values())
    print(f"\nSaved {out_path}\nYears={len(out)}  total answers={total_ans}  total solutions={total_sol}", file=sys.stderr)


if __name__ == "__main__":
    main()
