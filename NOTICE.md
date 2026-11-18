# Third-party material

Most of the data in this app is other people's work. It is not under the licence in `LICENSE`;
it keeps the licence of the project it comes from.

## KANJIDIC2 and JMdict (kanji, readings, meanings, words)

The school grade, readings, English meanings and newspaper frequency of each kanji come from
KANJIDIC2. The words listed under each kanji, the meanings of the words in the texts, and the
dictionary used to check every reading come from JMdict.

Both files are the property of the [Electronic Dictionary Research and Development Group](https://www.edrdg.org/)
and are used under the [Group's licence](https://www.edrdg.org/edrdg/licence.html), which is
[Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

- Where: `src/data/kanji.json`, the word lists inside `src/data/texts.json`, and their copies in `data.json`.
- Changes made: a selection only. Up to four meanings and a few readings per kanji, up to five words per kanji, glosses shortened to their first few.
- These parts stay under CC BY-SA 4.0. The non-commercial condition in `LICENSE` does not apply to them.

The data was read through the npm package `@johnmorrisdotca/jisho` (KANJIDIC2 of 2026-10-31, JMdict of 2026-11-04).

## KanjiVG (stroke order)

The stroke-order drawings of the 1,026 kanji come from [KanjiVG](https://kanjivg.tagaini.net/),
copyright © Ulrich Apel, licensed under
[Creative Commons Attribution-Share Alike 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

- Where: the stroke paths inside `src/data/kanji.json` (and `data.json`), copied unchanged from KanjiVG's SVG files. The project's own `COPYING` file is at `src/data/KanjiVG-COPYING`. The app icon is drawn from the strokes of 字.
- This data stays under CC BY-SA 3.0.

## Tatoeba (example sentences)

The example sentences and their English translations come from the [Tatoeba](https://tatoeba.org/) project,
licensed under [Creative Commons Attribution 2.0 France](https://creativecommons.org/licenses/by/2.0/fr/).
Each sentence is stored, and shown in the app, with its Tatoeba number and the names of its contributors.
The furigana on them come from the JMdict example files and were kept only where a second tool (MeCab with UniDic) read the sentence the same way.

- Where: `src/data/sentences.json` (and `data.json`).

## What is mine

The app itself (`src/template.html`, `src/build.py`), the order of the kanji within each grade, and the
128 short texts in `src/texts.txt` with their English were made for this project with the help of an AI
assistant. They are under the licence in `LICENSE`.

Nobody named above has reviewed or endorsed this project.
