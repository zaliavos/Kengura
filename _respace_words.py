"""Heuristic Lithuanian word-spacer for PDF-extracted text where spaces
were dropped between words.

Examples:
  "Sąlygojepasakyta, jogAdelėatbėgotrečia, oBarb"
  → "Sąlygoje pasakyta, jog Adelė atbėgo trečia, o Bar..."

Rules (conservative, only insert a space when confident):

  1. lowercase letter directly followed by UPPERCASE letter
     ("jogAdelė" → "jog Adelė") — almost always a word break.

  2. Common short Lithuanian function words (o, ir, iš, į, su, jog, tai,
     kad, bet, tad, ar) when they appear merged onto a following word.

  3. Common Lithuanian word-ending suffixes followed by a lowercase letter
     that starts a likely new word. We only fire on a curated whitelist
     of (suffix, next-word-start) pairs to avoid breaking real words.

  4. Digit-letter boundary: "29mokiniai" → "29 mokiniai"; "16cm" leaves alone
     (we keep digit-unit pairs untouched via a unit whitelist).

We DO NOT split arbitrary letter-letter pairs because Lithuanian compound
words and inflected forms make false-positives common. The CamelCase rule
(#1) is by far the most reliable; rules #2 and #4 catch the rest of the
common patterns.
"""
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

# Lithuanian alphabet for word-character class
LT_LOWER = "a-zA-ZąčęėįšųūžĄČĘĖĮŠŲŪŽ"
LT_LO    = "ąčęėįšųūža-z"
LT_UP    = "ĄČĘĖĮŠŲŪŽA-Z"

# Function words that frequently get glued to the next word.
# Conservative list: only words that are NEVER also Lithuanian verb/noun
# prefixes inside a word. ("pas", "iš", "į", "su", "pa", "nuo", "ant"
# etc. are excluded — they can be inside legitimate words like
# "pasakyta", "išėjo", "įdėti", "sumokėti".)
FUNCTION_WORDS = [
    "o", "ir", "ar", "jog", "tai", "kad", "bet", "tad",
]

# Common Lithuanian word endings — these appear at word-end
ENDINGS = [
    "oje", "ose", "ame", "ome", "ate", "ete", "iams", "iems", "ams", "oms",
    "ėms", "yms", "umus", "imus", "atės", "imas", "ąją", "ėjimas", "ėjimo",
    "tojo", "ūsis", "imas", "imai", "imą", "iuose", "iuosiuose",
    "ojoje", "umos", "umoms", "ojo", "iniai", "inio", "iniai",
    "amą", "iamą", "uose", "ėje", "asis", "esis", "isi",
]

# Units we should NOT space out (digit then unit)
UNITS = {"cm", "m", "mm", "km", "kg", "g", "min", "s", "h", "l", "ml", "°", "EUR", "Lt", "Eur"}


def respace(text):
    if not text:
        return text
    s = text

    # Rule 1: lowercase + UPPERCASE → insert space
    # ("jogAdelė" → "jog Adelė")
    s = re.sub(rf'([{LT_LO}])([{LT_UP}])', r'\1 \2', s)

    # Rule 4: digit-letter boundary, except known units
    def digit_letter(m):
        digits, letters = m.group(1), m.group(2)
        # find first 1-3 letters; if they form a unit, leave alone
        head = re.match(rf'([{LT_LOWER}]{{1,3}})', letters).group(1)
        if head in UNITS:
            return f'{digits}{letters}'
        return f'{digits} {letters}'
    s = re.sub(rf'(\d+)([{LT_LO}][{LT_LOWER}]*)', digit_letter, s)

    # Rule 2: function-word at start of a glued long word
    # Only fire if the letter immediately after the function word is also
    # a lowercase letter (otherwise rule 1 already split it).
    # We work on word level: find words where the prefix is a function word
    # and what follows looks like another full word (≥4 chars).
    def split_function_prefix(word):
        for fw in sorted(FUNCTION_WORDS, key=len, reverse=True):
            if len(word) > len(fw) + 4 and word.lower().startswith(fw):
                rest = word[len(fw):]
                if rest and rest[0].islower() and len(rest) >= 4:
                    return f'{word[:len(fw)]} {rest}'
        return word
    s = re.sub(rf'\b([{LT_LOWER}]+)\b',
               lambda m: split_function_prefix(m.group(1)), s)

    # Rule 3: common ending then lowercase starting word
    # Only fire on whitelisted suffix list and only if the next word is ≥ 5 chars
    def split_ending(word):
        for end in sorted(ENDINGS, key=len, reverse=True):
            # Must end ...{end}{lowercase chunk ≥ 5}
            if len(word) > len(end) + 5:
                # find an inner break point: word = X + end + Y where Y is ≥5 chars
                for i in range(3, len(word) - len(end) - 4):
                    if word[i:i+len(end)] == end:
                        before = word[:i+len(end)]
                        after = word[i+len(end):]
                        if after and after[0].islower() and len(after) >= 5:
                            return f'{before} {after}'
        return word
    s = re.sub(rf'\b([{LT_LOWER}]{{12,}})\b',
               lambda m: split_ending(m.group(1)), s)

    # Rule 5: vowel-end + consonant-cluster start
    # Inside a long word, if we see a vowel followed by a known consonant
    # cluster that typically starts Lithuanian words, that's likely a
    # word break. Examples:
    #   "atbėgotrečia" → "atbėgo trečia"   (o + tr)
    #   "sumokėtukad"  → "sumokėtu kad"    (u + ka — single consonant; skip)
    # We only fire on multi-consonant clusters where the second consonant
    # makes the cluster word-start-likely.
    WORD_START_CLUSTERS = [
        "tr","kr","br","pr","gr","dr","fr","sk","st","sp","sl","sm","sn","sv",
        "kn","gn","kl","gl","bl","pl","fl","ml","tv","kv","dv","žv","šv","sr",
        "kt","pt","ks","ps","ks","kž","kš","gž","dž","tk","mn",
    ]
    def split_vowel_cluster(word):
        if len(word) < 10: return word
        for i in range(4, len(word) - 5):
            ch = word[i]
            if ch in "aąeęėiįyouųū":
                ng = word[i+1:i+3]
                if ng in WORD_START_CLUSTERS:
                    before = word[:i+1]
                    after = word[i+1:]
                    if len(before) >= 4 and len(after) >= 5:
                        return f'{before} {after}'
        return word
    s = re.sub(rf'\b([{LT_LOWER}]{{10,}})\b',
               lambda m: split_vowel_cluster(m.group(1)), s)

    # Rule 6: name/noun-ending vowel + verb-prefix boundary
    # Examples: "Adelėatbėgo" → "Adelė atbėgo"  (ė + at)
    #           "Andriusparašė" → "Andrius parašė" (us + par)
    # We split at ENDING_VOWEL + KNOWN_VERB_PREFIX for words ≥ 10 chars.
    VERB_PREFIXES = ["atbėgo","atbėg","atėjo","atėj","atneša","atėmė","atvyko",
                     "padarė","padaro","padaryti","parašė","pradeda","pradėjo",
                     "perėjo","perskaitė","priėjo","priešais",
                     "išleido","išėjo","išvyko","ištraukė",
                     "užtenka","užbaigė","užrašė",
                     "sumokėjo","sukūrė","susitiko","sudėjo","suprato",
                     "padalino","padaryta","pamatė","palygino"]
    # Common short verbs/words that follow a noun without space
    GLUE_WORDS = VERB_PREFIXES + [
        "trečia","ketvirta","penkta","šešta","septinta","aštunta","devinta","dešimta",
        "pirma","antra","yra","buvo","sako","sakė","klausia","klausė","atsako","atsakė",
        "pasakyta","duota","gauta","gavo","tikrai","greitai","atsitiktinai",
        "padaro","padarė","liko","pasilikta","pasiliko","tikrai","žinoma",
    ]
    GLUE_WORDS_SORTED = sorted(set(GLUE_WORDS), key=len, reverse=True)
    def split_glue(word):
        if len(word) < 10: return word
        for gw in GLUE_WORDS_SORTED:
            # find gw inside word as a suffix to be peeled off
            idx = word.find(gw)
            if idx > 4 and idx + len(gw) == len(word):
                # confirm preceding char is a vowel ending common to LT names
                if word[idx-1] in "aąeęėiįyouųū":
                    return f'{word[:idx]} {gw}'
        # also try gw appearing in the middle (one peel max)
        for gw in GLUE_WORDS_SORTED:
            idx = word.find(gw)
            if idx > 4 and idx + len(gw) < len(word):
                if word[idx-1] in "aąeęėiįyouųū" and len(word) - idx - len(gw) >= 4:
                    rest = word[idx+len(gw):]
                    return f'{word[:idx]} {gw} {rest}' if rest[0].islower() else word
        return word
    s = re.sub(rf'\b([{LT_LOWER}]{{10,}})\b',
               lambda m: split_glue(m.group(1)), s)

    # Tidy double spaces
    s = re.sub(r' {2,}', ' ', s)
    return s


# ----------------------------------------------------------------
# Apply
# ----------------------------------------------------------------
def main():
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)
    n_changed = 0
    for y in data['archive']:
        for q in y['questions']:
            for field in ('prompt', 'solution', 'solutionKid'):
                if field in q and q[field]:
                    new = respace(q[field])
                    if new != q[field]:
                        q[field] = new
                        n_changed += 1
            # also clean option values (text fields)
            if 'options' in q:
                for letter, val in list(q['options'].items()):
                    if val and isinstance(val, str):
                        nv = respace(val)
                        if nv != val:
                            q['options'][letter] = nv
                            n_changed += 1
            # misconceptions too
            if 'misconceptions' in q:
                for letter, txt in list(q['misconceptions'].items()):
                    if txt and isinstance(txt, str):
                        nt = respace(txt)
                        if nt != txt:
                            q['misconceptions'][letter] = nt
                            n_changed += 1

    with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
        f.write('window.KENGURA_ARCHIVE = ')
        json.dump(data, f, ensure_ascii=False)
        f.write(';\n')
    print(f"Re-spaced {n_changed} fields")


if __name__ == '__main__':
    # Self-test
    samples = [
        "Diana ! Sąlygojepasakyta, jogAdelėatbėgotrečia, oBarbora",
        "29mokinių klasėje",
        "16cm aukštis",
        "Sudaro kvadratą, įrašo skaičius",
    ]
    print("=== Self-test ===")
    for s in samples:
        print(f"  in:  {s}")
        print(f"  out: {respace(s)}")
        print()
    main()
