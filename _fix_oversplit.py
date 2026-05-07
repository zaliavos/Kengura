"""One-shot: reverse the over-splits introduced by an earlier overly
aggressive function-word respacer.

The previous pass split "pasakyta" → "pas akyta", "pasižymėki" →
"pas ižymėki", and similar. Re-join these by detecting the pattern
"pas + lowercase-suffix" where the joined form is a plausible Lithuanian
word (we use a curated list of common pas-prefixed words).

Same for any other over-split prefix that snuck in.
"""
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

# Common Lithuanian word starts that end in "-akyta", "-akytame", "-ižymėk*"
# and similar — the bits that the over-split left as standalone tokens.
# Pattern: prefix " " + suffix → join.
REJOIN_RULES = [
    # "pas X" — the previous splitter peeled "pas" off many pas-prefixed words.
    (re.compile(r'\bpas\s+(akyt[aue]?|akymas|akoja|akomės|ižymėk\w*|ižiūr\w*|iūl\w*|isi\w*|itik\w*|ielg\w*|isiek\w*|isi\w+|ekm\w*|tov\w*|tab\w*|kut\w*|kelb\w*|truk\w*|ižiūr\w*|tat\w*|akymas)\b', re.UNICODE),
     r'pas\1'),
    # Same for capitalised forms (start of sentence)
    (re.compile(r'\bPas\s+(akyt[aue]?|akymas|akoja|akomės|ižymėk\w*|ižiūr\w*|iūl\w*|isi\w*|itik\w*|ielg\w*|isiek\w*|isi\w+|ekm\w*|tov\w*|tab\w*|kut\w*|kelb\w*|truk\w*|ižiūr\w*|tat\w*|akymas)\b', re.UNICODE),
     r'Pas\1'),
    # "Po X" common cases — Po + lowercase that looks like part of "po"-noun
    (re.compile(r'\bPo\s+(žymėk\w*|spaust\w*|kalbėk\w*|kalb\w*|veikt\w*|žiūr\w*)\b'),
     r'Po\1'),
    # Jūsų noted: "iš karto" is correct; we don't want to glue "iš"+"karto".
    # No general rejoin for "iš ".
]


def fix(text):
    if not text:
        return text
    out = text
    for pat, repl in REJOIN_RULES:
        out = pat.sub(repl, out)
    return out


def main():
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)
    n = 0
    for y in data['archive']:
        for q in y['questions']:
            for field in ('prompt', 'solution', 'solutionKid'):
                if field in q and q[field]:
                    new = fix(q[field])
                    if new != q[field]:
                        q[field] = new; n += 1
            if 'options' in q:
                for letter, val in list(q['options'].items()):
                    if val and isinstance(val, str):
                        nv = fix(val)
                        if nv != val:
                            q['options'][letter] = nv; n += 1
            if 'misconceptions' in q:
                for letter, txt in list(q['misconceptions'].items()):
                    if txt and isinstance(txt, str):
                        nt = fix(txt)
                        if nt != txt:
                            q['misconceptions'][letter] = nt; n += 1

    with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
        f.write('window.KENGURA_ARCHIVE = ')
        json.dump(data, f, ensure_ascii=False)
        f.write(';\n')
    print(f"Re-joined {n} over-splits.")


if __name__ == '__main__':
    print('=== Self-test ===')
    samples = [
        "Sąlygoje pas akyta, jog Adelė atbėgo trečia",
        "Pas akyta, jog Diana aplenkė",
        "Pas ižymėkime: 1 2 3",
    ]
    for s in samples:
        print(f"  in:  {s}")
        print(f"  out: {fix(s)}")
        print()
    main()
