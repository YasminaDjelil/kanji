# Data preparation scripts

These made the files in `src/data/`. You do not need them to build the site, only to regenerate the data.
They were run once from a scratch folder, so the paths at the top of each script need adjusting.

They need:

- Node.js and the npm package `@johnmorrisdotca/jisho` (KANJIDIC2, JMdict and the Tatoeba examples, already split into tables)
- the KanjiVG SVG files
- Python 3 with `fugashi` and `unidic-lite` (a tokenizer, used as a second opinion on readings)

In order:

1. `dump.mjs`, `exdump.mjs`, `wdump.mjs`, `gdump.mjs` write the dictionary tables out as JSON.
2. `data.py` builds `kanji.json`: the 1,026 kanji in order, their groups, words and strokes. `words_n5.txt` and `words_n4.txt` are only used to prefer well-known words.
3. `sent.py` builds `sentences.json`: short sentences that use school kanji only and whose readings the tokenizer agrees with.
4. `texts.py` checks `src/texts.txt` and builds `texts.json`. It fails if a kanji has no reading, belongs to a later group, or if a word and reading are not in JMdict.
