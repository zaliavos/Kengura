"""Clean up extraction artifacts in option values.

Two failure modes:
  1. All-placeholder: every option is "(A)", "(B)", … — the question is
     image-only (5 picture choices). Kid must see the figure.
  2. Mixed/garbage: a few options have legitimate text but others contain
     fragments from neighbouring questions ("Kam lygi šių 7 atkarpų...").

For both cases we want the displayed option to be just the LETTER circle
when the value is bogus. We replace bogus values with the sentinel "" (empty)
and let the UI fall back to "no text — see picture".

A value is treated as bogus if:
  - It matches the placeholder pattern ((A), B, C), etc.
  - It's longer than 80 chars (real Kangaroo options are ≤ 50 chars)
  - It's a fragment that looks like a *question* (starts with Kuris/Koks/
    Kam/Kiek/Atkarpos/etc. and ends with ? or mid-word)
  - It's clearly broken Lithuanian (ends in hyphen, fragment word)
"""
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

PLACEHOLDER_RE = re.compile(r'^\s*\(?[A-E]\)?\s*$')
QUESTION_LIKE_RE = re.compile(
    r'^(Kam|Kuri|Kuris|Koks|Kokia|Kokie|Kiek|Atkarpos|Tarp|Tada|Jeigu|Jei|Šešiakampė|Kvadrato)\b',
    re.IGNORECASE,
)


def is_bogus(v):
    if v is None:
        return True
    s = str(v).strip()
    if not s:
        return True
    # Placeholder-like
    if PLACEHOLDER_RE.match(s):
        return True
    # Way too long for an option
    if len(s) > 80:
        return True
    # Looks like a question fragment
    if QUESTION_LIKE_RE.match(s):
        return True
    # Ends in a hyphen mid-word (extraction broke at line wrap)
    if re.search(r'[-–]\s*$', s):
        return True
    # Is a single Lithuanian word fragment (3-7 chars ending in dash earlier
    # we caught; here look for trailing ":" or "," with nothing after)
    if len(s) > 3 and s.endswith(','):
        return True
    return False


def main():
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)

    n_cleaned = 0
    n_image_only = 0  # questions where all 5 options become empty
    affected_years = {}
    for y in data['archive']:
        for q in y['questions']:
            opts = q.get('options', {}) or {}
            new_opts = dict(opts)
            for letter in ('A','B','C','D','E'):
                v = opts.get(letter)
                if is_bogus(v):
                    new_opts[letter] = ""
                    n_cleaned += 1
            empties = sum(1 for l in 'ABCDE' if not new_opts.get(l, "").strip())
            if empties == 5:
                # Mark question as image-only — UI will render letter-only buttons
                q['imageOnlyOptions'] = True
                n_image_only += 1
            elif empties:
                # Mixed: mark and let UI show empty options as "?"
                q['hasMissingOptionText'] = True
            q['options'] = new_opts
            if empties:
                affected_years[y['year']] = affected_years.get(y['year'], 0) + 1

    with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
        f.write('window.KENGURA_ARCHIVE = ')
        json.dump(data, f, ensure_ascii=False)
        f.write(';\n')

    print(f"Cleaned {n_cleaned} bogus option values")
    print(f"Image-only (all 5 empty after cleanup): {n_image_only}")
    print("\nAffected questions per year:")
    for yr in sorted(affected_years):
        print(f"  {yr}: {affected_years[yr]}")


if __name__ == '__main__':
    main()
