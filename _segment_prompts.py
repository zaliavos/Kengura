"""Second-pass segmenter, RESTRICTED to prompts only (and option text
that the kid sees on buttons). Drops the function-word requirement
from `_segment_words.py` because many residual prompt corruptions are
glued-content-words ("Stačiakampioplotaslygus" = stačiakampio +
plotas + lygus, no function word in the result).

Still safe-by-construction:
  * Uses the same vocab + blacklist + long-word protection set.
  * Requires ALL segments ≥3 chars (no short fragments).
  * Requires ALL segments ≥ freq 3 in vocab (no rare-fragment noise).
  * Only touches prompts and option text — leaves solutions alone.
"""
import json, re, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(HERE, 'kengura-archive.json')
ARCHIVE_JS   = os.path.join(HERE, 'kengura-archive.js')

# Reuse the building blocks from _segment_words
sys.path.insert(0, HERE)
from _segment_words import (
    build_vocab, LT_LO, SINGLE_CHAR_WORDS, LT_2CHAR_OK,
    MIN_LEN_TO_SEGMENT, MIN_SEGMENT_LEN,
)
sys.stdout.reconfigure(encoding='utf-8')


SHORT_3CHAR_OK = {
    # Prepositions/conjunctions/short content words that legitimately
    # appear as 3-char segments in a split.
    'per','nuo','ant','tam','šių','tai','arba','jei','iki','čia',
    'šio','šias','tas','tos','tos','dvi','jam','jos','jau','net','vis','tūr',
    'jis','šis','vos','šią','šio','dar','o', 'pat','dėl','ten','net',
}
# 3-char segments that look like real LT words but are actually PDF
# fragments from words such as `Juodosios → Juodos + ios + juo`.
SHORT_3CHAR_BLACKLIST = {'ios', 'juo', 'eis', 'ies', 'ius', 'tie', 'tų', 'rio'}

# 4+ char fragments that recur in the corpus (so they pass the freq ≥ 3
# bar) but are PDF extraction artifacts, not standalone LT words.
# Adding them here prevents the segmenter from using them as split candidates.
LONG_FRAGMENT_BLACKLIST = {
    'kvadra',   # `kvadratinės` → `kvadra tinės`
    'tinės',    # paired with kvadra above (genitive suffix, never standalone)
    'pavaiz',   # `pavaizduotos` → `pavaiz duotos`
    'duoto',    # corresponding tail
    'kraš',     # `kraštinė` fragments
    'stelėsyra','steliųyra',  # juo + stelės/stelių fragments
}


def make_strict_segmenter(vocab):
    """Like `_segment_words.make_segmenter` but no function-word
    requirement. Compensates by demanding stronger evidence per segment:
      * each segment ≥ 4 chars (or one of the whitelisted 3-char words)
      * each segment freq ≥ 3 in vocab
    """
    total = sum(vocab.values()) + 1
    def logprob(w):
        c = vocab.get(w, 0)
        if c == 0: return -math.inf
        return math.log(c / total)

    def segment(word):
        w = word.lower()
        n = len(w)
        NEG = -1e18
        dp = [(NEG, -1, None)] * (n + 1)
        dp[0] = (0.0, -1, None)
        for i in range(1, n + 1):
            for j in range(0, i):
                seg = w[j:i]
                if len(seg) < 3:
                    continue
                if len(seg) == 3 and seg not in SHORT_3CHAR_OK:
                    continue
                if seg in SHORT_3CHAR_BLACKLIST or seg in LONG_FRAGMENT_BLACKLIST:
                    continue
                if seg not in vocab:
                    continue
                if vocab[seg] < 3:
                    continue
                cand = dp[j][0] + logprob(seg)
                if cand > dp[i][0]:
                    dp[i] = (cand, j, seg)
        if dp[n][0] == NEG:
            return None
        segs = []
        i = n
        while i > 0:
            score, j, seg = dp[i]
            segs.append(seg); i = j
        segs.reverse()
        if len(segs) < 2:
            return None
        return segs
    return segment


def segment_text(text, segment, long_real_words):
    out = []
    pos = 0
    pat = re.compile(rf'[A-ZĄČĘĖĮŠŲŪŽ]?[{LT_LO}]{{{MIN_LEN_TO_SEGMENT - 1},}}')
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


def main():
    mode = 'apply' if '--apply' in sys.argv else 'dry'
    with open(ARCHIVE_JSON, encoding='utf-8') as f:
        data = json.load(f)
    vocab, long_real_words = build_vocab(data)
    print(f'Vocabulary: {len(vocab)} words, protected long: {len(long_real_words)}')
    segment = make_strict_segmenter(vocab)

    n_changed = 0
    diffs = []
    for y in data['archive']:
        for q in y['questions']:
            # Prompts
            if q.get('prompt'):
                new = segment_text(q['prompt'], segment, long_real_words)
                if new != q['prompt']:
                    diffs.append((y['year'], q['num'], 'prompt', q['prompt'], new))
                    if mode == 'apply':
                        q['prompt'] = new
                    n_changed += 1
            # Option text (kid sees buttons)
            for letter, val in list((q.get('options') or {}).items()):
                if val and isinstance(val, str):
                    new = segment_text(val, segment, long_real_words)
                    if new != val:
                        diffs.append((y['year'], q['num'], f'opt-{letter}', val, new))
                        if mode == 'apply':
                            q['options'][letter] = new
                        n_changed += 1

    print(f'=== {mode.upper()}: {n_changed} fields ===')
    log = os.path.join(HERE, '_segment2_diffs.txt')
    with open(log, 'w', encoding='utf-8') as f:
        for y, num, field, b, a in diffs:
            f.write(f'[{y}-Q{num} {field}]\n  BEFORE: {b}\n  AFTER:  {a}\n\n')
    print(f'Diffs: {log}')

    if mode == 'apply':
        with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        with open(ARCHIVE_JS, 'w', encoding='utf-8') as f:
            f.write('window.KENGURA_ARCHIVE = '); json.dump(data, f, ensure_ascii=False); f.write(';\n')
        print('Wrote archive.')


if __name__ == '__main__':
    main()
