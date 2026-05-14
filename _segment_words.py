"""Bootstrapped Lithuanian word segmenter for PDF-extraction artifacts.

Targets the deeply-merged multi-word strings the prefix-based fixer
can't handle ("Čiavarguarkąatspėsi", "peliukųnelaikysime",
"taivertadaugintiiš") by:

  1. Building a vocabulary + word frequencies from all currently
     well-spaced text in the archive (and in the source PDF text
     where the archive itself is unreliable — not implemented here
     because the PDFs are the same source the archive came from).

  2. For every word in the archive ≥12 chars long with no space,
     running a Viterbi DP over the string: find the split that
     maximises product of word probabilities, accepting only splits
     in which ALL resulting tokens are in the vocabulary (or are
     one of the closed-class single-character LT words `o`/`į`).

  3. Only applying the split when (a) all parts are in-vocab, and
     (b) the resulting segmentation has ≥ 2 segments. Otherwise leave
     the word alone — better to under-fix than to introduce wrong
     splits.

Designed to be re-runnable; idempotent on already-correct text.
"""
import json, re, os, sys, io, math
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

LT_LO = "ąčęėįšųūža-z"

# Single-character LT tokens that are real words; the segmenter is
# allowed to leave these as 1-char segments.
SINGLE_CHAR_WORDS = {'o', 'į', 'š'}  # š sometimes appears as iš artifact

# Real two-letter LT tokens. Anything 2-char NOT on this list is
# rejected from the vocab, even if it appears in the bootstrap —
# otherwise extraction fragments like "ma", "vi", "la" become free
# split points and break real words like "reikalaujama".
LT_2CHAR_OK = {
    'ir', 'iš', 'su', 'po', 'už', 'du', 'jų', 'ji', 'ne',
    'jo', 'ar', 'jį', 'ją', 'tą', 'tų', 'aš', 'ką', 'šį', 'tu',
    'be', 'pa', 'nu', 'to', 'ta', 'tę', 'nė', 'kę', 'aš',
    'gi', 'ja', 'ko', 'kas',  # emphatic particles and inflected forms
    # units (the PDF extraction kept these as standalone words)
    'cm', 'km', 'kg', 'mm', 'dm', 'lt', 'ml', 'eu',
    # geometry labels
    'ab', 'bc', 'cd', 'ac', 'bd', 'ad',
    # roman numerals seen in option labels
    'ii', 'iv',
}

# Curated supplement: common Lithuanian words / inflected forms that
# don't appear in the bootstrap vocab (because they're rare in the
# archive even though they're frequent in general LT). Adding these
# enables the segmenter to recover splits that would otherwise fail
# because of one missing token at the end of the run.
EXTRA_VOCAB = [
    # spėti family (to guess / to be able)
    'atspėti','atspėjo','atspėsi','atspėtumėm','atspėtumėt','atspėjau','atspės',
    'spėti','spėjo','spėjau','spėjome','spėju','spėjant','spėjamai','spėjome',
    'spėjome','spėjote','spėjai','spės','spėsi','spėsim','spėsime',
    # kreipti family (to direct/turn)
    'atkreipti','atkreipė','atkreipia','atkreipdami','atkreipkim','atkreipkime',
    'atkreipkite','atkreipiame','atkreipdamas','atkreiptas','atkreiptina',
    'kreipti','kreipė','kreipia','kreipiamės','kreipiamasi',
    # tikrinti family
    'tikrinti','tikrina','tikrino','tikrinkim','tikrinkime','tikrinkite',
    'tikrindami','tikrinant','tikrinamas','patikrinti','patikrino','patikrinkime',
    # rūpinti
    'rūpinti','rūpinasi','rūpinasi','rūpinasi','pasirūpinti','pasirūpino',
    # adverbs
    'vargu','tikrai','žinoma','beje','štai','gerai','blogai','dažnai','retai',
    'kasdien','kasryt','kasvakar','greitai','lėtai','ūmai','vos','vis','viskas',
    'nieko','niekas','niekada','niekur','niekuomet','niekuo','niekam',
    'kažkas','kažką','kažkur','kažkada','kažkoks','kažkokia',
    'taip','ne','jau','dar','vis','net','tik','tikriausiai','tikslios',
    # common verbs / participles
    'sako','sakė','sakydavo','sakys','sakytume','sakytum','sakysite',
    'pasakė','pasakys','pasakytum','pasakytu','pasakomos','pasakomai',
    'galima','galimas','galimi','galimu','galimose','galimumas','galimybė',
    'reikia','reikės','reikėjo','reikėjau','reikią','reikalauja','reikalavo',
    'gauname','gavome','gausime','gautume','gautumėme','gausi','gaus',
    'mato','mato','matėme','matome','matytume','matydavo','matę',
    'pamatė','pamatys','pamatysite','pamatytume','pamatytume',
    'imti','ima','ėmė','imdamas','imdami','imkim','imkime','imkite',
    'paimti','paėmė','paima','paimti','paimkim','paimkime','paimkite',
    'duoti','duoda','davė','duos','duotume','duotumėme',
    'gali','galite','galiu','galim','galime','galės','galėjo','galėjau',
    # number words
    'vienas','viena','vienam','vienai','viename','vienoje','vienu','vienais',
    'du','dvi','dviese','dviejų','dviem','dviese','abu','abi','abiems',
    'trys','trijų','trim','trimis','triese',
    'keturi','keturios','keturių','keturis','keturių','keturiese',
    'penki','penkios','penkių','penkis','penkias','penkiese',
    'šeši','šešios','šešių','šešis','šešias','šešiese',
    'septyni','septynios','septynių',
    'aštuoni','aštuonios','aštuonių',
    'devyni','devynios','devynių',
    'dešimt','dešimties','dešimtyje',
    # adjectives
    'didelis','didelė','dideli','didelės','didžioji','didžiausias','didžiausia',
    'mažas','maža','maži','mažos','mažąjį','mažoji','mažiausias','mažiausia',
    'geras','gera','geri','geros','gerai','geriausias','geriausia',
    'blogas','bloga','blogi','blogos','blogiau','blogiausias',
    'naujas','nauja','nauji','naujos','naujesnis','naujesnė',
    'senas','sena','seni','senos','senesnis','senesnė',
    # geometry/math terms
    'kvadratas','kvadratai','kvadrato','kvadratui','kvadratą','kvadratu',
    'kvadratukas','kvadratukai','kvadratuko','kvadratukus','kvadratuką','kvadratuke',
    'trikampis','trikampiai','trikampio','trikampį','trikampiu',
    'trikampiukas','trikampiukai','trikampiuko','trikampiukus','trikampiukais','trikampiuką',
    'skrituliukas','skrituliukai','skrituliuko','skrituliukus','skrituliukais','skrituliuką',
    'stačiakampiukas','stačiakampiukai','stačiakampiuko','stačiakampiukus','stačiakampiuką',
    'apskritimukas','apskritimukai','apskritimuko','apskritimukus','apskritimuką',
    'stačiakampis','stačiakampiai','stačiakampio','stačiakampį','stačiakampiu',
    'apskritimas','apskritimai','apskritimo','apskritimą','apskritimu',
    'kraštinė','kraštinės','kraštinei','kraštinę','kraštine','kraštinių',
    'kampas','kampai','kampo','kampui','kampą','kampu','kampe','kampų',
    'taškas','taškai','taško','tašką','tašku','taške','taškų','taškas',
    'tiesė','tiesės','tiesei','tiesę','tiese','tiesių','tiesėse',
    'plotas','plotai','ploto','plotą','plotu','plote','plotų',
    'tūris','tūriai','tūrio','tūrį','tūriu','tūryje','tūrių',
    'ilgis','ilgiai','ilgio','ilgį','ilgiu','ilgyje','ilgių',
    'plotis','pločio','plotį','pločiu','plotyje',
    'aukštis','aukščio','aukštį','aukščiu','aukštyje',
    # common adverbs/connectives that didn't make it
    'tai','taigi','todėl','kadangi','nors','tačiau','jog','jeigu',
    'atrodo','atrodė','atrodyti','panašu','panašiai','greta','šalia',
    'priešais','prieš','priešingu','priešingais','priešais',
    # pasakų / fairy-tale words common in math problems
    'kengūra','kengūros','kengūrai','kengūrą','kengūra','kengūrų',
    'pelytė','pelytės','pelytei','pelytę','pelyte','peliukas','peliukai',
    'vaikai','vaikų','vaikui','vaiką','vaiku','vaikas','vaikams',
    'mokinys','mokiniai','mokinio','mokinį','mokiniu','mokinių',
    'mergina','mergaitė','mergaitės','mergaičių','mergaičius','mergaite',
    'berniukas','berniukai','berniuko','berniukui','berniukus','berniukų',
    # time
    'diena','dienos','dienai','dieną','diena','dienomis','dienose','dienų',
    'valanda','valandos','valandai','valandą','valanda','valandų','valandomis',
    'minutė','minutės','minutei','minutę','minute','minučių','minutėmis',
    'sekundė','sekundės','sekundei','sekundę','sekunde','sekundžių',
    'savaitė','savaitės','savaitei','savaitę','savaite','savaičių',
    'mėnuo','mėnesio','mėnesį','mėnesiu','mėnesyje','mėnesių','mėnesiai',
    'metai','metų','metais','metuose','metams','metus',
    # color / quantity
    'spalva','spalvos','spalvai','spalvą','spalva','spalvų','spalvomis',
    'spalvos','spalvotas','spalvotos','spalvotam','spalvotą','spalvoti',
    'raudonas','raudoni','raudonos','raudoną','raudoną','raudonų',
    'mėlynas','mėlyni','mėlynos','mėlyną','mėlyną','mėlynų',
    'žalias','žali','žalios','žalią','žalią','žalių',
    'geltonas','geltoni','geltonos','geltoną','geltoną','geltonų',
    'baltas','balti','baltos','baltą','baltą','baltų','baltai',
    'juodas','juodi','juodos','juodą','juodą','juodų','juodai',
    'pilkas','pilki','pilkos','pilką','pilką','pilkų','pilkai',
]
EXTRA_VOCAB_SET = set(EXTRA_VOCAB)

# Vocab fragments to BLACKLIST — patterns that look like merged
# extraction artifacts, never real Lithuanian standalone words.
VOCAB_BLACKLIST_PATTERNS = [
    re.compile(r'^cm[a-ząčęėįšųūž]'),     # cmplotų, cmpločio, cmkampas
    re.compile(r'^km[a-ząčęėįšųūž]'),
    re.compile(r'^kg[a-ząčęėįšųūž]'),
    re.compile(r'^[a-ząčęėįšųūž]+cm$'),  # ...cm, like ploto5cm
    re.compile(r'^ks[a-ząčęėįšųūž]{4,}'), # ksskaičius
    re.compile(r'^pskritim'),             # pskritimų — fragment of apskritimų
    re.compile(r'^škai'),                 # škaibe — fragment
]
# Exact-match blacklist for known fragments that recur as standalone
# tokens (because the PDF emitted them across column breaks):
VOCAB_BLACKLIST_EXACT = {
    'pavaiz', 'vaiz', 'duoto',                # pavaiz/duo/tose
    'kraš', 'kraščia', 'kraštin',             # kraš/tinė
    'tose', 'siuose', 'iuose',                # locative-plural suffix fragments
    'rau', 'tein', 'aiz', 'iek', 'duo', 'duotos',
    'syklę', 'syklės', 'syklei', 'syklių',    # taisyklės root broken from tai-
    'taiteis', 'taisyk',                       # taiteisingas, taisyklių fragments
    'len', 'kiama', 'kiamas', 'kiame',         # užlenkiama → už len kiama
    'lpa', 'kpa', 'gpa',                       # rare 3-char fragments
}


def vocab_blacklisted(word):
    if word in VOCAB_BLACKLIST_EXACT:
        return True
    for pat in VOCAB_BLACKLIST_PATTERNS:
        if pat.search(word):
            return True
    return False

# Minimum run length to attempt segmentation. Real Lithuanian words can
# be quite long (compound nouns, inflected verbs), so we don't want to
# touch words just because they're long — only when they're SO long
# that they're almost certainly multi-word.
MIN_LEN_TO_SEGMENT = 12

# Per-segment minimum length, except for single-char whitelist.
MIN_SEGMENT_LEN = 2


def build_vocab(data):
    """Build word frequency dictionary from cleanly-spaced text in the archive.

    Returns (vocab, long_real_words) where:
      * vocab — frequency table of short words (2..11 chars) used by
        the Viterbi splitter as segmentation candidates.
      * long_real_words — set of tokens ≥12 chars that appear ≥2 times
        in the archive. These are presumed real Lithuanian words (or
        consistently-recurring proper names) and the splitter MUST
        NOT touch them, even if a valid all-in-vocab split exists.
    """
    vocab = Counter()
    long_counts = Counter()
    for y in data['archive']:
        for q in y['questions']:
            fields = []
            for f in ('prompt', 'solution', 'solutionKid'):
                if q.get(f): fields.append(q[f])
            for letter, v in (q.get('options') or {}).items():
                if v: fields.append(v)
            for t in fields:
                for w in re.findall(rf'[{LT_LO}A-ZĄČĘĖĮŠŲŪŽ]+', t):
                    lw = w.lower()
                    if 2 <= len(w) <= 11:
                        if len(lw) == 2 and lw not in LT_2CHAR_OK:
                            continue
                        if vocab_blacklisted(lw):
                            continue
                        vocab[lw] += 1
                    elif len(w) >= 12:
                        long_counts[lw] += 1
    for w in EXTRA_VOCAB_SET:
        if w not in vocab:
            vocab[w] = 5  # moderate weight — not too dominant, not zero

    # Identify long tokens that are likely REAL Lithuanian words.
    # Tiered heuristic:
    #   * freq ≥ 5 → real word, protect unconditionally (catches
    #     `skrituliukas` (9), `stačiakampių` (8), `ketvirtadienis` (5)
    #     — words long enough that they could in theory be sliced into
    #     short-word pieces but appear consistently across the corpus).
    #   * freq 2-4 → real only if NOT splittable into short-word pieces.
    #     This filters out merged strings that recur a couple of times
    #     (like `kvadratėliųsudėtos` (2), `mažiausiaivienasiš` (2)).
    #   * freq 1 → treat as a one-off merged string; do not protect.
    long_real_words = set()
    tmp_seg = make_segmenter(vocab)
    for w, c in long_counts.items():
        if c >= 5:
            long_real_words.add(w)
        elif c >= 2 and tmp_seg(w) is None:
            long_real_words.add(w)
    for w in long_real_words:
        vocab[w] = long_counts[w]
    return vocab, long_real_words


# Function words / short connectors. A split is accepted only if at
# least one of its segments is in this set — that's the signal that
# the merged string is a multi-word phrase, not a single inflected word.
# Without this gate, the splitter happily breaks real compound forms
# (`trikampiukas` → `trikampiu kas`, `pavaizduotoje` → `pavaiz duotoje`).
SPLIT_REQUIRES_FUNCWORD = {
    # Pure prepositions / conjunctions — these only ever stand alone,
    # they never appear as word suffixes in real Lithuanian. A split
    # containing one of these is high-confidence multi-word.
    'ir', 'iš', 'su', 'po', 'už', 'į', 'ne', 'o', 'š',
    'kad', 'jog', 'ar', 'arba', 'nors', 'jei', 'jeigu',
    'kai', 'kaip', 'be',
    'tačiau', 'todėl', 'kadangi', 'taigi', 'tikrai',
    # Pronouns like `jo`, `ji`, `ja`, `tu`, `kas`, `tai`, `ta`, `to`,
    # `tų`, `gi` are NOT here — they're real LT words but they also
    # appear as common word suffixes (-ojo, -ji, -tai, ...), so
    # admitting them as fwd evidence false-splits real compound
    # words (`didžiausiojo` → `didžiausio jo`, `kvadratai` etc.).
}


def make_segmenter(vocab, require_funcword=True):
    total = sum(vocab.values()) + 1
    # Log-prob of a word; unknown words get a very negative penalty.
    def logprob(w):
        c = vocab.get(w, 0)
        if c == 0:
            return -math.inf
        return math.log(c / total)

    def segment(word):
        """Return the most likely segmentation, or None if no valid
        all-in-vocab split exists."""
        w = word.lower()
        n = len(w)
        # dp[i] = (best_score, parent_index, segment_used) for w[0:i]
        NEG = -1e18
        dp = [(NEG, -1, None)] * (n + 1)
        dp[0] = (0.0, -1, None)
        for i in range(1, n + 1):
            for j in range(0, i):
                seg = w[j:i]
                if len(seg) < MIN_SEGMENT_LEN and seg not in SINGLE_CHAR_WORDS:
                    continue
                if seg not in vocab and seg not in SINGLE_CHAR_WORDS:
                    continue
                lp = logprob(seg) if seg in vocab else math.log(1 / total) - 2
                cand = dp[j][0] + lp
                if cand > dp[i][0]:
                    dp[i] = (cand, j, seg)
        # Reconstruct
        if dp[n][0] == NEG:
            return None
        segs = []
        i = n
        while i > 0:
            score, j, seg = dp[i]
            segs.append(seg)
            i = j
        segs.reverse()
        # Reject single-segment "splits" — those are no-ops
        if len(segs) < 2:
            return None
        # Accept the split only if we have signal that the merged form
        # is genuinely a multi-word phrase, not a single inflected word.
        # Either:
        #   (a) some segment is a high-confidence function word, OR
        #   (b) the run is very long (≥ 20 chars) AND every segment is
        #       a moderately-frequent content word (≥ 3 occurrences).
        if require_funcword:
            has_fw = any(s in SPLIT_REQUIRES_FUNCWORD for s in segs)
            if not has_fw:
                if n < 20:
                    return None
                # Long-run no-fw path: all segs must be solid content words
                if not all(vocab.get(s, 0) >= 3 for s in segs):
                    return None
        return segs
    return segment


# ----------------------------------------------------------------
# Whole-string driver
# ----------------------------------------------------------------
def segment_text(text, segment, long_real_words):
    """Walk through `text`, look for runs of letters that are too long
    to be a single Lithuanian word, and attempt to segment them.

    Preserves the original casing of the first letter of each segment
    by treating the first character of the merged run as a hint: if
    the run started with uppercase, capitalise the first segment.

    Skips any run whose lowercase form is in `long_real_words` —
    those are presumed real Lithuanian inflected/compound words and
    must not be touched.
    """
    out = []
    pos = 0
    # Match runs of letters that look like a single (possibly capitalised)
    # Lithuanian word: optional leading uppercase, then lowercase only.
    # This avoids matching geometry labels like "ABCD" embedded in
    # "ABCDpadalytas" (where the run has multiple uppercase letters).
    pat = re.compile(
        rf'[A-ZĄČĘĖĮŠŲŪŽ]?[{LT_LO}]{{{MIN_LEN_TO_SEGMENT - 1},}}'
    )
    for m in pat.finditer(text):
        run = m.group(0)
        out.append(text[pos:m.start()])
        if run.lower() in long_real_words:
            out.append(run)
        else:
            segs = segment(run)
            if segs is None:
                out.append(run)
            else:
                if run[0].isupper():
                    segs = [segs[0][:1].upper() + segs[0][1:]] + segs[1:]
                out.append(' '.join(segs))
        pos = m.end()
    out.append(text[pos:])
    return ''.join(out)


def walk(data, segment, long_real_words, mode='dry'):
    n_changed = 0
    diffs = []
    for y in data['archive']:
        for q in y['questions']:
            for field in ('prompt', 'solution', 'solutionKid'):
                if field in q and q[field]:
                    new = segment_text(q[field], segment, long_real_words)
                    if new != q[field]:
                        diffs.append((y['year'], q['num'], field, q[field], new))
                        if mode == 'apply':
                            q[field] = new
                        n_changed += 1
            if 'options' in q:
                for letter, val in list(q['options'].items()):
                    if val and isinstance(val, str):
                        nv = segment_text(val, segment, long_real_words)
                        if nv != val:
                            diffs.append((y['year'], q['num'], f'opt-{letter}', val, nv))
                            if mode == 'apply':
                                q['options'][letter] = nv
                            n_changed += 1
            if 'misconceptions' in q:
                for letter, txt in list(q['misconceptions'].items()):
                    if txt and isinstance(txt, str):
                        nt = segment_text(txt, segment, long_real_words)
                        if nt != txt:
                            diffs.append((y['year'], q['num'], f'mis-{letter}', txt, nt))
                            if mode == 'apply':
                                q['misconceptions'][letter] = nt
                            n_changed += 1
    return n_changed, diffs


def main():
    mode = 'apply' if '--apply' in sys.argv else 'dry'
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)

    vocab, long_real_words = build_vocab(data)
    print(f'Vocabulary size: {len(vocab)} unique words')
    print(f'Protected long words (≥12 chars, ≥2 occurrences): {len(long_real_words)}')
    segment = make_segmenter(vocab)

    # Self-test
    print()
    print('=== Self-test ===')
    for word in ['Čiavarguarkąatspėsi', 'peliukųnelaikysime',
                 'taivertadaugintiiš', 'Mažiausiaivienasiš',
                 'kvadratėliųsudėtos', 'apelsinųsulčiųdaugiau',
                 'Atkreipkitedėmesįįtai', 'kartotiniaikartojasikas']:
        segs = segment(word)
        if segs:
            print(f'  {word}  →  {" ".join(segs)}')
        else:
            print(f'  {word}  →  (NO SPLIT — keeping)')

    print()
    n, diffs = walk(data, segment, long_real_words, mode=mode)
    print(f'=== {mode.upper()}: {n} fields would change ===')

    log_path = os.path.join(HERE, '_segment_diffs.txt')
    with open(log_path, 'w', encoding='utf-8') as f:
        for y, num, field, before, after in diffs:
            f.write(f'[{y}-Q{num} {field}]\n')
            f.write(f'  BEFORE: {before}\n')
            f.write(f'  AFTER:  {after}\n\n')
    print(f'Full diff log: {log_path}')

    # Print a sample
    print()
    print('Sample of 20 diffs:')
    for y, num, field, before, after in diffs[:20]:
        print(f'\n[{y}-Q{num} {field}]')
        print(f'  BEFORE: {before[:280]}')
        print(f'  AFTER:  {after[:280]}')

    if mode == 'apply':
        with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
            f.write('window.KENGURA_ARCHIVE = ')
            json.dump(data, f, ensure_ascii=False)
            f.write(';\n')
        print(f'\nWrote {ARCHIVE_JSON} and {ARCHIVE_JS}')


if __name__ == '__main__':
    main()
