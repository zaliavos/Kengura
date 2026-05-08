"""Extract answer keys from the Solutions/ folder PDFs and apply them to the archive.

PDF -> year mapping (verified by year-frequency probe):
    Solutions/2006kengura.pdf  -> 2006 (multi-grade table; Bičiulis = column B, 2nd of 5)
    Solutions/spGDPRB (1).pdf  -> 2014 (Bičiulis-only single-column key on last page)
    Solutions/spGDPRB (2).pdf  -> 2015 (same format)
    Solutions/spGDPRB.pdf      -> 2016 (same format)
    Solutions/spGDPRB (3).pdf  -> 2017 (same format)

For 2006 the answer table looks like:
    M B K (C) J S
    1 D B B D A
    ...
    24 B B D C C
    25 E E C C        <- Mažylis ends at Q24, so column M is blank for rows 25-30
    ...
The Bičiulis letter is the FIRST letter after the row number for rows 1-24,
and still the FIRST letter for rows 25-30 (because M is missing).
"""
import os, re, json, pdfplumber

SINGLE_COL_PDFS = {
    'Solutions/spGDPRB (1).pdf': '2014',
    'Solutions/spGDPRB (2).pdf': '2015',
    'Solutions/spGDPRB.pdf':     '2016',
    'Solutions/spGDPRB (3).pdf': '2017',
}

def extract_single_col(path):
    """Extract {q# -> letter} from a Bičiulis-only solution PDF."""
    with pdfplumber.open(path) as d:
        for p in d.pages:
            t = p.extract_text() or ''
            if 'Atsakymai' in t:
                # rows look like: "1 D" / "30 E"
                out = {}
                for q, letter in re.findall(r'(?m)^\s*(\d{1,2})\s+([A-E])\s*$', t):
                    n = int(q)
                    if 1 <= n <= 30 and n not in out:
                        out[n] = letter
                if out:
                    return out
    return {}

def extract_2006(path):
    """Extract Bičiulis column from the multi-grade 2006 table.

    Rows 1-24:  '<n> M B K J S'   (5 letters; B is the 2nd)
    Rows 25-30: '<n> B K J S'     (4 letters; M missing because Mažylis
                                   has only 24 problems)
    Bičiulis is in both cases the FIRST letter after the row number.
    """
    with pdfplumber.open(path) as d:
        for p in d.pages:
            t = p.extract_text() or ''
            if 'Atsakymai' in t and 'Klausimo' in t:
                # find table body
                m = re.search(r'M\s+B\s+K[^\n]*\n(.+)', t, re.S)
                if not m:
                    continue
                body = m.group(1)
                out = {}
                for line in body.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if not parts or not parts[0].isdigit():
                        continue
                    n = int(parts[0])
                    if not (1 <= n <= 30):
                        continue
                    letters = [x for x in parts[1:] if x in 'ABCDE']
                    if not letters:
                        continue
                    if n <= 24:
                        # M B K J S — Bičiulis is index 1
                        if len(letters) >= 2:
                            out[n] = letters[1]
                    else:
                        # B K J S (M missing) — Bičiulis is index 0
                        out[n] = letters[0]
                return out
    return {}


keys = {}
for path, year in SINGLE_COL_PDFS.items():
    k = extract_single_col(path)
    print(f'{year} ({path}): {len(k)} keys -> {k}')
    keys[year] = k

k06 = extract_2006('Solutions/2006kengura.pdf')
print(f'2006: {len(k06)} keys -> {k06}')
keys['2006'] = k06

# Apply to archive
PATH = 'kengura-archive.json'
with open(PATH, encoding='utf-8') as f:
    data = json.load(f)

filled = 0
for tier in data['archive']:
    y = tier['year']
    if y not in keys:
        continue
    for q in tier['questions']:
        if q['num'] in keys[y] and not q.get('correct'):
            q['correct'] = keys[y][q['num']]
            filled += 1

print(f'\nFilled {filled} keys.')
with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
