import fitz, re, collections

SMALL_TOKEN = re.compile(r'^[0-9a-zA-Z+−\-,.·()]{1,7}$')

def page_text(page):
    """page.get_text() with stacked fractions joined as "a/b" and a small
    raised 2/3 after a unit turned into ²/³. Works on spans across the whole
    page (numerator and denominator can sit in different lines or blocks)
    and keeps get_text()'s block/line order."""
    d = page.get_text('dict')
    sizes = collections.Counter()
    for b in d['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if s['text'].strip(): sizes[round(s['size'], 1)] += len(s['text'])
    if not sizes: return page.get_text()
    body = sizes.most_common(1)[0][0]
    blocks, smalls = [], []
    for b in d['blocks']:
        if b['type'] != 0: continue
        lines = []
        for l in b['lines']:
            L = dict(bbox=fitz.Rect(l['bbox']), items=[], has_body=False)
            for s in l['spans']:
                t = s['text']
                if t.strip() and s['size'] < body * 0.85 and SMALL_TOKEN.match(t.strip()):
                    smalls.append(dict(L=L, r=fitz.Rect(s['bbox']), t=t.strip(), used=False))
                else:
                    L['items'].append((s['bbox'][0], t))
                    if t.strip(): L['has_body'] = True
            lines.append(L)
        blocks.append(lines)
    hosts = [L for lines in blocks for L in lines if L['has_body']]
    def host_for(y, x):
        c = [L for L in hosts if L['bbox'].y0 - 1 <= y <= L['bbox'].y1 + 1]
        if not c: return None
        return min(c, key=lambda L: 0 if L['bbox'].x0 - 3 <= x <= L['bbox'].x1 + 3
                   else min(abs(x - L['bbox'].x0), abs(x - L['bbox'].x1)))
    for u in smalls:                           # numerator above denominator
        if u['used']: continue
        for lo in smalls:
            if lo is u or lo['used']: continue
            ur, lr = u['r'], lo['r']
            if abs((ur.x0 + ur.x1) / 2 - (lr.x0 + lr.x1) / 2) <= max(ur.width, lr.width) / 2 + 1.5 \
                    and 2 < lr.y0 - ur.y0 < 12:
                x = min(ur.x0, lr.x0)
                h = host_for((ur.y1 + lr.y0) / 2, x)
                if h is None: continue
                h['items'].append((x, ' ' + u['t'] + '/' + lo['t'] + ' '))
                u['used'] = lo['used'] = True
                break
    for u in smalls:                           # raised 2 / 3 after a unit → ² / ³
        if u['used']: continue
        h = host_for(u['r'].y1 - 1, u['r'].x0)
        if h is not None and u['t'] in ('2', '3') and u['r'].y1 < h['bbox'].y1 - 2:
            prev = [t for x, t in h['items'] if x < u['r'].x0 and t.strip()]
            if prev and re.search(r'(cm|m|dm|mm|km)\s*$', prev[-1]):
                h['items'].append((u['r'].x0, '²' if u['t'] == '2' else '³')); u['used'] = True; continue
        u['L']['items'].append((u['r'].x0, (' ' if u['L']['items'] else '') + u['t']))
    out = []
    for lines in blocks:
        texts = []
        for L in lines:
            t = ''.join(x for _, x in sorted(L['items'], key=lambda it: it[0]))
            t = re.sub(r'  +', ' ', t)
            if t.strip(): texts.append(t)
        if texts: out.append('\n'.join(texts))
    return '\n'.join(out) + '\n'
