"""Comprehensive typo fix for the Bičiulis archive.

Targets the surviving artifacts from PDF extraction + earlier passes:

  1. Ogonek combining char `˛i` → `į` (and `˛I` → `Į`). This single
     substitution accounts for ~480 visible glitches.

  2. Specific over-split prefixes — words where an earlier respacer
     wrongly split a real Lithuanian verb/noun into a prefix + tail
     ("be rniukų", "pas tebėti", "su skirstyti", "iš klotinė").
     Curated whitelist only — never a generic prefix-peel.

  3. Missing space after sentence punctuation when followed by a
     letter (",vėl" → ", vėl"). Numeric decimals like "2,5" are
     preserved by requiring an alphabetic char *both* sides.

  4. Digit-letter boundary ("29mokinių" → "29 mokinių") with a units
     whitelist (cm, kg, m, m², °, %, Lt, EUR…).

  5. Run-together word-pair joins that are *certainly correct*
     ("kvadratąir" → "kvadratą ir") via a function-word peeler that
     ONLY fires on `ir`, `o`, `jog`, `tai`, `kad`, `bet`, `tad`, `ar`
     when the preceding word ends in a vowel and the following part
     is ≥ 4 chars.

We treat the run for idempotency: applying twice produces the same
output as applying once.
"""
import json, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

LT_LO = "ąčęėįšųūža-z"
LT_UP = "ĄČĘĖĮŠŲŪŽA-Z"
LT_ALL = LT_LO + LT_UP
VOWELS = "aąeęėiįyouųūAĄEĘĖIĮYOUŲŪ"

# ---------------------------------------------------------------- 1. ogonek
def fix_ogonek(s):
    if not s: return s
    s = s.replace('˛i', 'į').replace('˛I', 'Į')
    # rare: the ogonek standing alone before/after a letter
    s = re.sub(r' ˛ ', ' ', s)
    return s

# ---------------------------------------------------------------- 2. over-splits
# Each rule: (regex, replacement). All conservative — these match real
# Lithuanian word forms that the previous respacer wrongly broke apart.

OVERSPLIT_RULES = [
    # "be rniuk*" → "berniuk*"  (boy[s] in Lithuanian)
    (re.compile(r'\b([Bb])e (rniuk\w*)\b'), r'\1e\2'),
    (re.compile(r'\bbe (rniuk\w*)\b'), r'be\1'),  # extra safety lowercase
    (re.compile(r'\bBe (rniuk\w*)\b'), r'Be\1'),

    # "pas X" — common pas-prefixed verbs/nouns split apart.
    # In Lithuanian "pas" + a lowercase verb stem is almost always a
    # mis-split single word; "pas" as a preposition takes a pronoun or
    # capitalised name ("pas mane", "pas Joną") which our lowercase
    # match below does not touch.
    (re.compile(r'\b([Pp])as ('
                # speech / saying — pasakyti
                r'akyt\w*|akymas|akoj\w*|akomės|akymais|akotin\w*'
                # appearance — pasirodyti, pasižymėti, pasižiūrėti, pasiūlyti
                r'|ižymėk\w*|ižymėt\w*|ižiūr\w*|iūl\w*|iūly\w*'
                # reflexives — pasi-
                r'|isi[a-ząčęėįšųūž]*|isiek\w*|isek\w*|iėm\w*'
                # other pas- verbs: pastebėti, pasirinkti, pasitelkti...
                r'|itik\w*|ielg\w*|ielgti|elgia\w*|ielgia\w*'
                r'|ekm\w*|tov\w*|tab\w*|kut\w*|kelb\w*|truk\w*|tat\w*'
                r'|tebė\w*|tebim\w*|tebėjim\w*|tebėdam\w*'
                r'|ikart\w*|ikartoj\w*|ikartos|ikartotų'
                r'|irod\w*|irody\w*'
                r'|tumti|tumė|tumtų|tumti\w*'
                r'|islink\w*|islėp\w*'
                # pasiekti / pasiekiamas
                r'|iek\w*|iekt\w*'
                # pasidaryti
                r'|idar\w*|idary\w*'
                # pasvirti / pasvirusiojo
                r'|virus\w*|virę|virus[uioae]\w*'
                # pasibaigti
                r'|ibaig\w*'
                # pasirinkti
                r'|irink\w*'
                # pasinaudoti
                r'|inaud\w*'
                # pasivaikščioti
                r'|ivaikšč\w*'
                # pasiuntinys
                r'|iuntin\w*'
                # pasukti
                r'|ukt\w*|uktum\w*|uktas|uktume'
                # pasikeisti
                r'|ikeis\w*|ikeič\w*|ikeiči\w*'
                # paskirstymas
                r'|kirstym\w*|kirsty\w*'
                # paskaičiuoti
                r'|kaičiuo\w*|kaiči\w*'
                # paspausti / paspaudimas
                r'|paud\w*|paudim\w*'
                # pasiruoš / pasireng
                r'|ireng\w*|iruoš\w*'
                # one-char tail
                r'|ė'
                r')\b'),
     r'\1as\2'),

    # "su X" — verb-prefix su- merged into the verb stem.
    # NOTE: must NOT match "su skaičiumi/skaičiais/skaičiavime" (prep+noun),
    # "su vienu/dviem/trimis" (with one/two/three), "su liekana"
    # (with remainder), "su apskritimu" (with the circle).
    (re.compile(r'\b([Ss])u ('
                # sumaišyti
                r'maišei|maišy\w*|maišom\w*'
                # sudaryti / sudaryta / sudėti
                r'|daryti|darytas|daryta|darytų|darytus|darys|darom\w*'
                r'|dėsime|deda|dedam\w*|dėtas|dėjus|dėlioti|dėliotų|dėtų'
                r'|dėk\w*|dėjom\w*|dėjusi\w*|dėties|dėtyne|dėtis'
                # suvalgyti
                r'|valgė|valgyti|valgo|valgom\w*|valgant'
                # sutapti
                r'|tampa|tapti|taptų|tapę'
                # sujungti
                r'|jungti|jungimas|jungimo|jungia|jungę|jungus|jungtas'
                r'|junkim\w*|jungtos|jungtų'
                # susikirtimas — reflexive
                r'|sikirtim\w*'
                # suskaičiuoti
                r'|skaičiuoti|skaičiuokim\w*|skaičiuojam\w*|skaičiuoja'
                r'|skaičiav\w*'
                # suskirstyti
                r'|skirstyti|skirstyk\w*|skirstom\w*|skirstyt\w*'
                # surašyti
                r'|rašyti|rašykim\w*|rašyk\w*|rašom\w*|rašytą'
                # surinkti
                r'|rinko|rinkti|rink\w*'
                # sukarpyti
                r'|karpė|karpyti|karpom\w*|karpė'
                # reflexive su-si-...
                r'|sirink\w*|silanksto|silanksty\w*|sideda|sitik\w*'
                r'|sikibę|sikibim\w*|sidaryt\w*|sidaro|sidūr\w*'
                # suvokti
                r'|vokti|voktas'
                # suklijuoti
                r'|klijuoti|klijuoja|klijuotas|klijuota|klijuotos|klijuotų|klijav\w*'
                # sugraužti
                r'|graužė|graužti'
                # sulyginti
                r'|lygino|lyginom\w*|lyginus|lyginimo'
                # surikiuoti
                r'|rikiuokim\w*|rikiuotas|rikiuotos|rikiav\w*|rikiuoja'
                # sukioti (turn)
                r'|kioti|nkiau|nkiausi\w*'
                # sustatė
                r'|statė|stato|statome'
                # suprasti
                r'|prasti|prata|pranta|prantam\w*|pratom\w*|pratais'
                # sukakti / sukaupti
                r'|kakti|kanka|kaupia|kaupimas|kaupiama'
                # sulankstyti
                r'|lankstyti|lankstom\w*|lankstom|lankst\w*|lanksčius'
                # sujudėti
                r'|judo|judėjo|judėjimas|jungę'
                # sunkus, sunkiau, sunkesnis (heavy/harder/heavier)
                r'|nkum\w*|nkesni\w*|nkesn\w*|nkesnė|nkų|nkų\w*'
                # sužymėti
                r'|žymėk\w*|žymėt\w*|žymim\w*'
                # sunumeruoti
                r'|numeruot\w*|numeruoti|numeruoja\w*|numerav\w*|numerai|numerui'
                # sukeisti / pasikeisti
                r'|keisti|keiči\w*|keičiu\w*|keisdav\w*|keičiamas'
                # sutikti / sutinka
                r'|tinka|tinkam\w*|tikim\w*|tinkt\w*|tinkti|tiks\w*'
                # sugalvoti
                r'|galvot\w*|galvoj\w*'
                # sumažėti / sumažinti
                r'|mažėj\w*|mažės|mažėjo|mažin\w*|mažint\w*'
                # sumeluoti
                r'|melav\w*|melu\w*'
                # sudalinti / sudalyti
                r'|dalint\w*|daly\w*|dalink\w*|dalin\w*|daliję'
                # sušaukti / sušauk
                r'|šauk\w*'
                # sušaldyti / sušald
                r'|šald\w*'
                # sušnabždėti / sušnek
                r'|šnek\w*|šuk\w*'
                # sudėjusi / sudėjo
                r'|laikė|laikyti|laiko'
                # sušukti
                r'|šukt\w*|šukim\w*|šuk\w*'
                # sumokėti
                r'|mokė\w*|moka|moker\w*'
                # sukurti
                r'|kurti|kūrė|kūrim\w*'
                # sustoti
                r'|stoti|stojo|stoja|stoję'
                r')\b'),
     r'\1u\2'),

    # "iš X" — ONLY very-high-confidence merges.
    # Most "iš X" pairs in the archive are correct two-word phrases
    # ("iš viso", "iš eilės", "iš karto", "iš pradžių", "iš atlikusio",
    # "iš likusių", "iš skirtumo"...). We only merge:
    #   a) `iš si...`  — reflexive verb pattern (`išsirinko`, `išsirūpino`),
    #      EXCEPT when the trailing word is a Greek-origin si- noun
    #      (`simetrija`, `sistema`, `simbolis`, ...).
    #   b) `iš klotinė...` — specific geometry-net compound
    (re.compile(r'\b([Ii])š (klotin\w*)\b'), r'\1š\2'),

    # "nu X" — rare but valid
    (re.compile(r'\b([Nn])u (skritimo|kris\w*|kritęs|kelta|keltas|spaudė|spaud\w*'
                r'|tarė|tarti|tarus|sprend\w*|tildė|spręsta|tildy\w*)\b'),
     r'\1u\2'),

    # "už X" — verb prefix
    (re.compile(r'\b(Už|už) (rašyti|rašyta\w*|rašyk\w*|rašom\w*|rašymas'
                r'|davinys|davinio|davinį|daviniai|daviniuose'
                r'|degė|degti|tenka|tenkam\w*|tekos|tekam\w*'
                r'|baigė|baigti|baigus|baigia\w*|baigtas'
                r'|davinį|daviniui)\b'),
     r'\1\2'),

    # "po X" — already handled in fix_oversplit, expand slightly
    (re.compile(r'\b([Pp])o (žymėk\w*|žymėt\w*|spaust\w*|spaudim\w*'
                r'|kalbėk\w*|kalbant|kalbėt\w*'
                r'|veikt\w*|veikim\w*|žiūr\w*)\b'),
     r'\1o\2'),

    # Standalone "iš " followed by a clear verb prefix — usually wrong
    # Handled by the iš dictionary above; nothing to add here.
]

# Greek/Latin-origin si- nouns that genuinely follow "iš" as a preposition:
# "iš simetrijos" / "iš sistemos" / "iš simbolio" — these must NOT be merged.
SI_NOUN_PREFIXES = ('simetr', 'simbol', 'sistem', 'silogizm', 'sirop',
                    'sien', 'sij',  # siena (wall), sija (beam)
                    'sirg',          # sirgti (to be ill) — never iš-prefixed
                    'siekt', 'siek', # siekti — see comment below
                    'siūl')

def fix_is_si(s):
    """Merge `iš si<reflexive>` → `iššsi<reflexive>`, but only when the
    second token looks like a reflexive verb form, not a Greek-origin noun
    that begins with si- (simetrija, sistema, ...)."""
    pat = re.compile(r'\b([Ii])š (si\w{2,15})\b')
    def repl(m):
        word2 = m.group(2)
        for blk in SI_NOUN_PREFIXES:
            if word2.startswith(blk):
                return m.group(0)
        return m.group(1) + 'š' + word2
    return pat.sub(repl, s)


def fix_oversplits(s):
    if not s: return s
    out = s
    for pat, repl in OVERSPLIT_RULES:
        out = pat.sub(repl, out)
    out = fix_is_si(out)
    return out

# ---------------------------------------------------------------- 3. space after punct
def fix_punct_space(s):
    if not s: return s
    # Add space after , . ! ? : when followed by a letter, but NOT in numbers
    # (we require the LEFT side to also be a letter, or a closing bracket/quote).
    s = re.sub(rf'([{LT_ALL}\)\]\}}\"\'»])([,.!?:;])([{LT_ALL}])', r'\1\2 \3', s)
    # collapse doubled space we may have produced
    s = re.sub(r' {2,}', ' ', s)
    return s

# ---------------------------------------------------------------- 4. digit-letter
UNITS = {'cm','mm','m','km','kg','g','min','s','h','val','l','ml','t',
         'EUR','Lt','Eur','m²','m³','cm²','cm³','km²','km³','sek','d','mėn'}

def fix_digit_letter(s):
    if not s: return s
    def repl(m):
        d, letters = m.group(1), m.group(2)
        head = re.match(rf'^([{LT_ALL}]{{1,5}})', letters)
        if head and head.group(1) in UNITS:
            return f'{d}{letters}'
        return f'{d} {letters}'
    s = re.sub(rf'(\d)([{LT_LO}][{LT_ALL}]+)', repl, s)
    return s

# ---------------------------------------------------------------- 5. function-word peel
# When a word like "kvadratąir" appears, peel off the ir.
# Strict: only ir / jog / kad / bet — these never appear as suffixes in
# real Lithuanian words. We deliberately EXCLUDE `tai` and `tad` because
# they false-positive on "kvadratai" → "kvadra tai", "penketai" → "penke tai".
# We also exclude `o` and `ar` (too short / too ambiguous as suffixes).
FUNCTION_WORDS_TRAIL = ['jog', 'kad', 'bet', 'ir']

def fix_glued_function(s):
    if not s: return s
    # Peel function word OFF THE END of a long word: "kvadratąir" → "kvadratą ir"
    # Requires the preceding character (before the function-word) to be a vowel
    # and the head before the function word to be ≥ 4 chars.
    def split_trailing(m):
        word = m.group(0)
        for fw in sorted(FUNCTION_WORDS_TRAIL, key=len, reverse=True):
            if len(word) > len(fw) + 3 and word.endswith(fw):
                head = word[:-len(fw)]
                if head[-1] in VOWELS and len(head) >= 4:
                    return f'{head} {fw}'
        return word
    s = re.sub(rf'\b[{LT_LO}]{{6,}}\b', split_trailing, s)
    # Also handle the "letter+ir+digit" boundary that the \b regex
    # above can't reach (since both letter and digit are \w characters).
    # "šokoladukąir4" → "šokoladuką ir 4"
    s = re.sub(rf'([{LT_LO}]{{4,}}[{VOWELS}])(ir|jog|kad|bet)(\d)',
               r'\1 \2 \3', s)
    return s

# ---------------------------------------------------------------- 6. letter-digit boundary
# "Karoliui1 šokoladuką" → "Karoliui 1 šokoladuką"
# Restrict to ≥4 lowercase letters so we don't break "cm2", "m3", "km2"
# (which are how cm², m³, km² were extracted from the PDF) or short labels.
def fix_letter_digit(s):
    if not s: return s
    return re.sub(rf'([{LT_LO}]{{4,}})(\d)', r'\1 \2', s)

# ---------------------------------------------------------------- pipeline
def fix_all(text):
    if not text: return text
    out = fix_ogonek(text)
    out = fix_oversplits(out)
    out = fix_punct_space(out)
    out = fix_digit_letter(out)
    out = fix_letter_digit(out)
    out = fix_glued_function(out)
    out = re.sub(r' {2,}', ' ', out)
    return out

# ---------------------------------------------------------------- driver
def walk(data, mode='dry'):
    n_changed = 0
    diffs = []
    for y in data['archive']:
        for q in y['questions']:
            for field in ('prompt', 'solution', 'solutionKid'):
                if field in q and q[field]:
                    new = fix_all(q[field])
                    if new != q[field]:
                        diffs.append((y['year'], q['num'], field,
                                      q[field], new))
                        if mode == 'apply':
                            q[field] = new
                        n_changed += 1
            if 'options' in q:
                for letter, val in list(q['options'].items()):
                    if val and isinstance(val, str):
                        nv = fix_all(val)
                        if nv != val:
                            diffs.append((y['year'], q['num'],
                                          f'opt-{letter}', val, nv))
                            if mode == 'apply':
                                q['options'][letter] = nv
                            n_changed += 1
            if 'misconceptions' in q:
                for letter, txt in list(q['misconceptions'].items()):
                    if txt and isinstance(txt, str):
                        nt = fix_all(txt)
                        if nt != txt:
                            diffs.append((y['year'], q['num'],
                                          f'mis-{letter}', txt, nt))
                            if mode == 'apply':
                                q['misconceptions'][letter] = nt
                            n_changed += 1
    return n_changed, diffs


def main():
    mode = 'apply' if '--apply' in sys.argv else 'dry'
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)

    n, diffs = walk(data, mode=mode)

    # Show a sample of diffs
    print(f'=== {mode.upper()}: {n} fields would change ===')
    sample = diffs[:30]
    for y, num, field, before, after in sample:
        b = before[:200]
        a = after[:200]
        print(f'\n[{y}-Q{num} {field}]')
        print(f'  BEFORE: {b}')
        print(f'  AFTER:  {a}')

    # Dump all diffs to a side file for review
    log_path = os.path.join(HERE, '_typo_diffs.txt')
    with open(log_path, 'w', encoding='utf-8') as f:
        for y, num, field, before, after in diffs:
            f.write(f'[{y}-Q{num} {field}]\n')
            f.write(f'  BEFORE: {before}\n')
            f.write(f'  AFTER:  {after}\n\n')
    print(f'\nFull diff log: {log_path}  ({len(diffs)} entries)')

    if mode == 'apply':
        with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
            f.write('window.KENGURA_ARCHIVE = ')
            json.dump(data, f, ensure_ascii=False)
            f.write(';\n')
        print(f'Wrote {ARCHIVE_JSON} and {ARCHIVE_JS}')


if __name__ == '__main__':
    main()
