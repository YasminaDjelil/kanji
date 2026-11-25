#!/usr/bin/env python3
"""Builds the Kanji app.

  python3 src/build.py <dir> pwa     -> <dir>/index.html + <dir>/data.json  (the website)
  python3 src/build.py <file.html>   -> one self-contained file (progress is not kept between visits)

Needs only Python 3. It also re-checks the promise the app makes: every text and every
sentence uses school kanji only, each kanji carries its reading, and no text uses a kanji
from a group later than its own.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def read(name): return json.load(open(os.path.join(HERE, 'data', name), encoding='utf-8'))
def iskanji(c): return '一' <= c <= '鿿'
CH = re.compile(r'\{([^{}|]+)\|([^{}|]+)\}')

A = read('kanji.json'); texts = read('texts.json'); sents = read('sentences.json')
groups = A['groups']
assert len(A['K']) == 1026 and len(texts) == len(groups)
gi = {k: i for i, (g, ks) in enumerate(groups) for k in ks}
assert [x['k'] for x in A['K']] == [k for g, ks in groups for k in ks], 'kanji list and groups disagree'

def check(jp, limit, what):
    bare = CH.sub('', jp)
    bad = [c for c in bare if iskanji(c) or c in '{}|']
    assert not bad, '%s: kanji without a reading: %s' % (what, ''.join(bad))
    for m in CH.finditer(jp):
        assert re.fullmatch(r'[぀-ゟー]+', m.group(2)), '%s: odd reading %s' % (what, m.group(2))
        for c in m.group(1):
            if iskanji(c):
                assert c in gi, '%s: %s is not a school kanji' % (what, c)
                assert limit is None or gi[c] <= limit, '%s: %s belongs to a later group' % (what, c)

for i, t in enumerate(texts): check(t['jp'], i, 'text %d' % (i + 1))
S = []
for s in sents:
    jp = re.sub(r'｜([^《｜]+)《([^》]+)》', r'{\1|\2}', s[0])
    check(jp, None, 'sentence ' + s[2])
    S.append([jp] + s[1:])

data = {
    'k': [[x['k'], x['g'], x['on'], x['kun'], x['m'], x['w'], x['st'], x.get('q', [])] for x in A['K']],
    'g': [[g, ''.join(ks)] for g, ks in groups],
    't': [[t['title'], t['jp'], t['en'], t['w']] for t in texts],
    's': S,
}
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
out = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] == 'pwa':
    head = '<link rel="manifest" href="manifest.webmanifest">\n<link rel="apple-touch-icon" href="icon-180.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Kanji">'
    html = tpl.replace('<!--HEAD-->', head).replace('<!--DATA-->', '').replace('/*HOSTED*/false', 'true')
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(html)
    open(os.path.join(out, 'data.json'), 'w', encoding='utf-8').write(blob)
    print('index.html %d kB, data.json %d kB' % (len(html.encode()) // 1024, len(blob.encode()) // 1024))
else:
    html = tpl.replace('<!--HEAD-->', '').replace('<!--DATA-->', '<script type="application/json" id="data">' + blob.replace('</', '<\\/') + '</script>')
    open(out, 'w', encoding='utf-8').write(html)
    print('%s %d kB' % (out, len(html.encode()) // 1024))
print('%d kanji, %d groups, %d texts, %d sentences: all checks passed' % (len(A['K']), len(groups), len(texts), len(S)))
