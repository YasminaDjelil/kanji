import json, re, fugashi, collections
T = fugashi.Tagger()
A = json.load(open('kanji_all.json', encoding='utf-8'))
order = [x['k'] for x in A['K']]; pos = {k: i for i, k in enumerate(order)}
E = json.load(open('examples_all.json', encoding='utf-8'))
def hira(t): return ''.join(chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c for c in t)
def iskanji(c): return '一' <= c <= '鿿' or c == '々'
RB = re.compile(r'｜([^《｜]+)《([^》]+)》')
seen, ok, why = set(), [], collections.Counter()
for s, en, tid, a1, a2 in E:
    if s in seen: continue
    seen.add(s)
    plain = RB.sub(lambda m: m.group(1), s)
    if not (6 <= len(plain) <= 28): why['len'] += 1; continue
    rest = RB.sub('', s)
    if any(iskanji(c) for c in rest): why['bare kanji'] += 1; continue
    ks = [c for c in plain if iskanji(c)]
    if not ks: why['no kanji'] += 1; continue
    if any(c not in pos for c in ks): why['other kanji'] += 1; continue
    if re.search(r'[A-Za-zＡ-Ｚａ-ｚ]', plain): why['latin'] += 1; continue
    mine = hira(RB.sub(lambda m: m.group(2), s))
    fu = hira(''.join((w.feature.kana or w.surface) for w in T(plain)))
    strip = lambda t: re.sub(r'[^぀-ゟー]', '', t)
    if strip(mine) != strip(fu): why['reading differs'] += 1; continue
    if not en or len(en) > 90: why['en'] += 1; continue
    ok.append((max(pos[c] for c in ks), len(plain), s, en, tid, a1, a2, set(ks)))
print(len(E), len(ok), why)
ok.sort(key=lambda x: (x[0], abs(x[1] - 16)))
keep, byLast, byK = {}, collections.Counter(), collections.Counter()
for x in ok:                       # sentences that open up at each kanji
    if byLast[x[0]] < 7: byLast[x[0]] += 1; keep[x[2]] = x
    for c in x[7]: byK[c] += (x[2] in keep)
for x in ok:                       # make sure each kanji has a few of the easiest sentences that hold it
    need = [c for c in x[7] if byK[c] < 3]
    if need and x[2] not in keep:
        keep[x[2]] = x
        for c in x[7]: byK[c] += 1
S = [[x[2], x[3], x[4], x[5], x[6]] for x in sorted(keep.values(), key=lambda x: (x[0], x[1]))]
json.dump(S, open('sentences.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(S), 'kept;', 'kanji with no sentence:', ''.join(k for k in order if not byK[k]), '; with <3:', sum(1 for k in order if byK[k] < 3))
import os; print(os.path.getsize('sentences.json'))
for x in S[:6] + S[1500:1504] + S[-3:]: print(x)
