"""Clean up the auto-extracted `solution` field on every 5-point archive
question. The official Kangaroo solution PDFs use the symbols ? and !
as decorative bullets ("?" = spėjimu, "!" = sprendimu), and the PDF text
extractor leaves those + spacing artifacts in the JSON.

Cleanup pass:
  - Strip leading "<answer>" + "?"/"!" / bullet decorations.
  - Collapse broken fractions like "1 6" → "1/6" (when context is a
    fraction expression).
  - Tighten whitespace.
  - Reflow paragraphs separated by stray bullet markers.

We keep the original content; we just make it readable. For questions
where the cleanup leaves something obviously wrong, the next pass
(_solutions_5pt_overrides.py) supplies a hand-written replacement.
"""
import json, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')


def clean_one(prompt, sol, correct, options):
    if not sol:
        return sol
    s = sol

    # 1) Strip leading "answer-value" if present (the field redundantly
    #    starts with the correct option's text or letter). We keep just
    #    the explanation.
    if correct and options and options.get(correct):
        opt_text = str(options[correct]).strip()
        # only strip if the prefix matches verbatim
        if opt_text and s.startswith(opt_text):
            s = s[len(opt_text):].lstrip(' .,;')

    # 2) Drop leading decorative bullets and any "?"/"!" run at the start.
    s = re.sub(r'^[\?\!\s]+', '', s)

    # 3) Collapse internal "?" / "!" used as decorative paragraph bullets
    #    → newline-style separators, then collapse runs.
    s = re.sub(r'\s+[\?\!]+\s+', ' — ', s)
    s = re.sub(r'^\s*[\?\!]\s*', '', s)

    # 4) Fix common broken fractions and minus signs.
    #    Pattern: digit space digit space (— bullets) — happens when fraction
    #    bar got lost between numerator and denominator on different lines.
    #    We only fix obvious cases like "1 6 — Pažiūrėkime" → "1/6 —"
    s = re.sub(r'\b([0-9]+) ([0-9]+)\b(?=\s+[—–-])', r'\1/\2', s, count=1)

    # 5) Tighten whitespace and stray spaces around punctuation.
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s+([.,;:])', r'\1', s)
    s = s.strip(' —–-,.;')

    # 6) Some solutions end with "Renkamės atsakymą X." or similar
    #    redundant tail; trim it.
    s = re.sub(r'\s*Renkamės\s+atsakymą\s+[A-E]\.?\s*$', '', s)
    s = re.sub(r'\s*Teisingas\s+atsakymas\s+[–-]?\s*[A-E]\.?\s*$', '', s)

    # 7) Re-add a clean prefix: "<correct option text>. <explanation>"
    if correct and options and options.get(correct):
        opt_text = str(options[correct]).strip()
        if opt_text and not s.lower().startswith(opt_text.lower()):
            s = f"{opt_text}. {s}"

    return s.strip()


def main():
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)
    n_changed = 0
    for y in data['archive']:
        for q in y['questions']:
            if q.get('points') != 5:
                continue
            old = q.get('solution', '')
            new = clean_one(q['prompt'], old, q.get('correct'), q.get('options'))
            if new != old:
                q['solution'] = new
                n_changed += 1

    with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
        f.write('window.KENGURA_ARCHIVE = ')
        json.dump(data, f, ensure_ascii=False)
        f.write(';\n')
    print(f"Cleaned {n_changed} 5-point solutions")


if __name__ == '__main__':
    main()
