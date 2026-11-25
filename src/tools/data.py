import json, re, os, sys
D = json.load(open('kanjidic.json', encoding='utf-8'))
C = json.load(open('common.json', encoding='utf-8'))
KV = '../kv/whl/kanji'
rows = {r[0]: r for r in D['rows']}
order, groups = [], []          # groups: [grade, [kanji...]]
for g in '123456':
    ks = sorted(D['grades'][g], key=lambda k: (rows[k][4] or 9999, k))
    n = len(ks); G = [ks[i:i+8] for i in range(0, n, 8)]
    if len(G[-1]) < 4:
        t = G.pop(); G[-1] = G[-1] + t
    for x in G: groups.append([int(g), x])
    order += ks
assert len(order) == 1026 and len(set(order)) == 1026
pos = {k: i for i, k in enumerate(order)}
def iskanji(c): return '一' <= c <= '鿿' or c == '々'
def iskana(c): return '぀' <= c <= 'ヿ'
BASIC = {(l.split('|')[0], l.split('|')[1]): i for i, f in enumerate(['words_n5.txt', 'words_n4.txt']) for l in open(f, encoding='utf-8') if '|' in l}
BAD = re.compile(r'\b(uk|arch|obs|rare|vulg|derog|sl|X|col|hist|dated|poet|ok|oK|rK|sK|iK|io|net-sl|fam|male|fem|on-mim|euph|joc|abbr|pn|n-pr)\b')
def hira(t): return ''.join(chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c for c in t)
def gloss(e):
    gl = [re.sub(r'\s*\((?:e\.g\.|esp\.|i\.e\.)[^)]*\)', '', x) for x in e['s'][0]['g'][:3]]
    m = '; '.join(gl)
    if len(m) > 60: m = '; '.join(gl[:2])
    if len(m) > 60: m = gl[0]
    return m
cand = {k: [] for k in order}; byWR = {}
seen = set()
for i, e in enumerate(C):
    w = e['w'][0]
    ks = [c for c in w if iskanji(c)]
    if not ks or '々' in ks: continue
    if any(not (iskanji(c) or iskana(c)) for c in w): continue
    if any(c not in pos for c in ks): continue
    if not e['s'] or BAD.search(e['s'][0]['m']): continue
    if (w, e['id']) in seen: continue          # first reading of an entry only
    seen.add((w, e['id']))
    byWR.setdefault((w, e['r']), e)
    last = max(ks, key=lambda c: pos[c])
    ichi = 'ichi1' in e['tags']
    key = (BASIC.get((w, e['r']), 2), 0 if ichi else 1, e['rank'], len(w), i)
    for c in set(ks):
        cand[c].append((key, w, e['r'], gloss(e), c == last, max(rows[x][2] for x in ks)))
EXTRA = {'茨': [('茨城', 'いばらき', 'Ibaraki (prefecture)')], '栃': [('栃木', 'とちぎ', 'Tochigi (prefecture)')], '媛': [('愛媛', 'えひめ', 'Ehime (prefecture)')],
 '奈': [('奈良', 'なら', 'Nara (city, prefecture)')], '埼': [('埼玉', 'さいたま', 'Saitama (city, prefecture)')], '阜': [('岐阜', 'ぎふ', 'Gifu (city, prefecture)')],
 '滋': [('滋賀', 'しが', 'Shiga (prefecture)')], '梨': [('山梨', 'やまなし', 'Yamanashi (prefecture)')], '昭': [('昭和', 'しょうわ', 'Shōwa era (1926–1989)')],
 '岐': [('岐阜', 'ぎふ', 'Gifu (city, prefecture)')], '賀': [('滋賀', 'しが', 'Shiga (prefecture)'), ('佐賀', 'さが', 'Saga (city, prefecture)')], '阪': [('大阪', 'おおさか', 'Osaka (city, prefecture)')],
 '潟': [('新潟', 'にいがた', 'Niigata (city, prefecture)')], '熊': [('熊本', 'くまもと', 'Kumamoto (city, prefecture)')], '鹿': [('鹿児島', 'かごしま', 'Kagoshima (city, prefecture)')], '崎': [('長崎', 'ながさき', 'Nagasaki (city, prefecture)')], '沖': [('沖縄', 'おきなわ', 'Okinawa (prefecture)')], '縄': [('沖縄', 'おきなわ', 'Okinawa (prefecture)')], '岡': [('福岡', 'ふくおか', 'Fukuoka (city, prefecture)')], '佐': [('佐賀', 'さが', 'Saga (city, prefecture)')], '富': [('富山', 'とやま', 'Toyama (city, prefecture)')], '井': [('福井', 'ふくい', 'Fukui (city, prefecture)')], '香': [('香川', 'かがわ', 'Kagawa (prefecture)')], '徳': [('徳島', 'とくしま', 'Tokushima (city, prefecture)')], '群': [('群馬', 'ぐんま', 'Gunma (prefecture)')]}
words, stats = {}, [0, 0, 0, 0]
useful = {}
BX = {}
_s = set()
for e in C:
    w = e['w'][0]; lv = BASIC.get((w, e['r']))
    if lv is None or (w, e['r']) in _s or not e['s']: continue
    _s.add((w, e['r']))
    for c in set(w):
        if c in pos: BX.setdefault(c, []).append((lv, e['rank'], w, e['r'], gloss(e)))

for k in order:
    L = sorted(cand[k]); g = rows[k][2]; r = rows[k]
    pick, used = [], set()
    def add(w, rd, m, later=0):
        if w in used or len(pick) >= 5: return
        used.add(w); pick.append([w, rd, m] + ([1] if later else []))
    kw = []
    for n, kun in enumerate(r[6]):                # the kanji's own words, read the kun way
        kun = kun.strip('-')
        stem, _, oku = kun.partition('.')
        e = byWR.get((k + oku, stem + oku))
        if e: kw.append((BASIC.get((k + oku, stem + oku), 2), 0 if 'ichi1' in e['tags'] else 1, n, k + oku, stem + oku, gloss(e)))
    for on in r[5]:
        e = byWR.get((k, hira(on)))
        if e and (k, hira(on)) in BASIC and not any(x[3] == k for x in kw): kw.append((BASIC[(k, hira(on))], 0, 0, k, hira(on), gloss(e)))
    kw.sort()
    for x in kw[:2]:
        if x[0] < 2 or x[1] == 0 or not pick: add(x[3], x[4], x[5])
    if not pick:
        for on in r[5]:
            e = byWR.get((k, hira(on)))
            if e: add(k, hira(on), gloss(e)); break
    for x in L:
        kk = [c for c in x[1] if iskanji(c)]
        if x[4] and len(x[1]) <= 4 and len(kk) > 1 and len(set(kk)) == len(kk) and not any(iskana(c) for c in x[1][:-1]): add(x[1], x[2], x[3])
    for x in L:
        kk = [c for c in x[1] if iskanji(c)]
        if x[4] and len(set(kk)) == len(kk): add(x[1], x[2], x[3])
    if len(pick) < 3:
        for x in L:
            if x[5] <= g and len(pick) < 3: add(x[1], x[2], x[3], 1)
    if len(pick) < 2:
        for x in L:
            if len(pick) < 2: add(x[1], x[2], x[3], 1)
    for w, rd, m in EXTRA.get(k, []):
        add(w, rd, m, 1 if any(pos[c] > pos[k] for c in w) else 0)
    words[k] = pick
    # useful words: the best-known words with this kanji, whatever other school kanji they use
    use, uu = [], set()
    def addu(w, rd, m):
        if w in uu or len(use) >= 6: return
        uu.add(w); use.append([w, rd, m])
    for x in kw[:2]:
        if x[0] < 2 or x[1] == 0 or not use: addu(x[3], x[4], x[5])
    if not use:
        for on in r[5]:
            e = byWR.get((k, hira(on)))
            if e and 'ichi1' in e['tags']: addu(k, hira(on), gloss(e)); break
    for x in sorted(BX.get(k, []))[:5]:
        if x[2] != k and len(x[2]) <= 5: addu(x[2], x[3], x[4])
    ok = [x for x in L if x[1] != k and len(x[1]) <= 4 and len(set(c for c in x[1] if iskanji(c))) == len([c for c in x[1] if iskanji(c)])]
    good = [x for x in ok if x[0][0] < 2 or (x[0][1] == 0 and x[0][2] <= 6000)]
    for x in good[:4]:
        if len(use) < 5: addu(x[1], x[2], x[3])
    for on in r[5][:3]:
        h = hira(on)
        if any(h in u[1] for u in use): continue
        for x in good:
            if h in x[2]: addu(x[1], x[2], x[3]); break
    for x in good: addu(x[1], x[2], x[3])
    if len(use) < 4:
        for x in ok:
            if len(use) < 4: addu(x[1], x[2], x[3])
    if not use:
        for p in pick: addu(p[0], p[1], p[2])
    for w, rd, m in EXTRA.get(k, []): addu(w, rd, m)
    useful[k] = use
    stats[min(len([p for p in pick if len(p) == 3]), 3)] += 1
print('kanji with 0/1/2/3+ strict words:', stats, 'no words at all:', [k for k in order if not words[k]])

import collections
P='../kanji-repo/src/data/kanji.json'
A=json.load(open(P,encoding='utf-8'))
for x in A['K']:
    x['q']=[p[:3] for p in words[x['k']] if p[0] not in {u[0] for u in useful[x['k']]}]
    x['w']=useful[x['k']]
json.dump(A,open(P,'w',encoding='utf-8'),ensure_ascii=False)
print(collections.Counter(len(x['w']) for x in A['K']))
for c in '地県電車会社新聞雨震鉄手上分行楽':
    x=[y for y in A['K'] if y['k']==c][0]; print(c,' '.join(w[0]+'('+w[1]+')' for w in x['w']),'| quiz:',' '.join(w[0] for w in x['q']))
