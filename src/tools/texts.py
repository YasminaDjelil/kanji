# Checks every text and writes texts.json. Fails on: a kanji outside {..|..}, a kanji from a later group, a word/reading the dictionary does not have.
import json, re, sys, fugashi
A = json.load(open('kanji_all.json', encoding='utf-8'))
groups = A['groups']; order = [x['k'] for x in A['K']]
gi = {}
for i, (g, ks) in enumerate(groups):
    for k in ks: gi[k] = i
first = {ks[0]: i for i, (g, ks) in enumerate(groups)}
DICT = set(); 
for line in open('allwords.tsv', encoding='utf-8'):
    w, _, r = line.rstrip('\n').partition('\t'); DICT.add((w, r))
C = json.load(open('common.json', encoding='utf-8'))
GL = {}
for e in C:
    for w in e['w']: GL.setdefault((w, e['r']), e)
def gloss(e):
    gl = [re.sub(r'\s*\((?:e\.g\.|esp\.|i\.e\.)[^)]*\)', '', x) for x in e['s'][0]['g'][:3]]
    m = '; '.join(gl)
    if len(m) > 60: m = '; '.join(gl[:2])
    if len(m) > 60: m = gl[0]
    return m
NAMES = {('山田', 'やまだ'): 'Yamada (a family name)'}
IRR = {('来', 'き'): ('来る', 'くる'), ('来', 'こ'): ('来る', 'くる')}
NUM = set('一二三四五六七八九十百千万')
def iskanji(c): return '一' <= c <= '鿿' or c == '々'
def iskana(c): return '぀' <= c <= 'ヿ'
def hira(t): return ''.join(chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c for c in t)
AG = json.load(open('allgloss.json', encoding='utf-8'))
def gl2(w, r):
    if (w, r) in GL: return gloss(GL[(w, r)])
    g = AG.get(w + '\t' + r)
    if not g: return None
    g = [re.sub(r'\s*\((?:e\.g\.|esp\.|i\.e\.)[^)]*\)', '', x) for x in g]
    m = '; '.join(g)
    if len(m) > 60: m = '; '.join(g[:2])
    if len(m) > 60: m = g[0]
    return m
T = fugashi.Tagger()
def lookup(w, r, after, lemma):
    """dictionary form for a chunk: exact word, the word made with the kana that follow, the tokenizer's dictionary form, or a number + counter"""
    if (w, r) in NAMES: return w, r, NAMES[(w, r)]
    if (w, r) in IRR: W, R = IRR[(w, r)]; return W, R, gl2(W, R)
    kana = re.match(r'[぀-ゟ]*', after).group(0)
    if lemma and lemma[0].startswith(w) and lemma[1].startswith(r) and lemma in DICT: return lemma + (gl2(*lemma),)
    if (w, r) in DICT: return w, r, gl2(w, r)
    for n in (4, 3, 2, 1):
        if len(kana) >= n and (w + kana[:n], r + kana[:n]) in DICT: return w + kana[:n], r + kana[:n], gl2(w + kana[:n], r + kana[:n])
    if w[0] in NUM or w[0] == '何': return None       # a number with a counter
    for o in ['る', 'う', 'く', 'ぐ', 'す', 'つ', 'ぬ', 'ぶ', 'む', 'い', 'しい', 'ける', 'える', 'れる', 'べる', 'める', 'じる', 'びる', 'りる', 'きる', 'ねる', 'せる', 'てる', 'げる', 'わる', 'まる', 'かる', 'ます', 'らう']:
        if (w + o, r + o) in DICT and (len(o) == 1 or kana[:1] == o[0]): return w + o, r + o, gl2(w + o, r + o)
    return False
lines = [l.rstrip('\n') for l in open('texts.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]
assert len(lines) % 3 == 0
out, errs, warn, nogloss = {}, [], [], []
CH = re.compile(r'\{([^{}|]+)\|([^{}|]+)\}')
for i in range(0, len(lines), 3):
    key, jp, en = lines[i:i + 3]
    if key not in first: errs.append('%s: not the first kanji of a group' % key); continue
    g = first[key]
    bare = CH.sub('', jp)
    for c in bare:
        if iskanji(c) or c in '{}|': errs.append('%s: kanji or brace outside a {word|reading}: %s in %s' % (key, c, bare)); break
    words, used, seen = [], set(), set()
    plain0 = CH.sub(lambda m: m.group(1), jp); lem, p0 = {}, 0
    for tk in T(plain0):
        p0 = plain0.index(tk.surface, p0)
        if tk.feature.orthBase and tk.feature.kanaBase: lem[p0] = (tk.feature.orthBase, hira(tk.feature.kanaBase))
        p0 += len(tk.surface)
    for m in CH.finditer(jp):
        w, r = m.group(1), m.group(2)
        for c in w:
            if c == '々': continue
            if iskanji(c):
                if c not in gi: errs.append('%s: %s is not a school kanji (%s)' % (key, c, w))
                elif gi[c] > g: errs.append('%s: %s comes later, in group %d (%s)' % (key, c, gi[c] + 1, w))
                used.add(c)
            elif not iskana(c): errs.append('%s: odd character in %s' % (key, w))
        if not re.fullmatch(r'[぀-ゟー]+', r): errs.append('%s: reading not hiragana: %s' % (key, r))
        d = lookup(w, r, jp[m.end():], lem.get(len(CH.sub(lambda x: x.group(1), jp[:m.start()]))))
        if d is False: errs.append('%s: not in the dictionary: %s / %s' % (key, w, r))
        elif d and d[0] not in seen:
            seen.add(d[0]); words.append([d[0], d[1], d[2] or ''])
            if not d[2]: nogloss.append(d[0])
    new = [k for k in groups[g][1] if k in used]
    if len(new) < 3: warn.append('%s: only %d of the group\'s kanji used' % (key, len(new)))
    plain = CH.sub(lambda m: m.group(1), jp)
    mine = hira(CH.sub(lambda m: m.group(2), jp)); fu = hira(''.join((t.feature.kana or t.surface) for t in T(plain)))
    st = lambda t: re.sub(r'[^぀-ゟー]', '', t)
    if st(mine) != st(fu):
        a, b = st(mine), st(fu); p = 0
        while p < min(len(a), len(b)) and a[p] == b[p]: p += 1
        warn.append('%s: tokenizer reads differently near: mine …%s / it …%s' % (key, a[max(0, p - 4):p + 8], b[max(0, p - 4):p + 8]))
    out[key] = {'g': g, 'jp': jp, 'en': en, 'need': ''.join(sorted(used, key=lambda c: gi[c])), 'w': words}
missing = [ks[0] for g, ks in groups if ks[0] not in out and not any(e.startswith(ks[0] + ':') for e in errs)]
print('\n'.join(errs)); print('--- warnings'); print('\n'.join(warn)); print('--- no gloss:', ' '.join(nogloss)); print('missing groups:', missing)
if errs or missing: sys.exit(1)
json.dump([out[ks[0]] for g, ks in groups], open('texts.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('OK', len(out), 'texts')
