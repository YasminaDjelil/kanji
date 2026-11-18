#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 src/build.py . pwa
cp src/static/* .
python3 src/build.py kanji.html
