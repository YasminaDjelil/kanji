import {COMMON_WORDS} from '../voc/_johnmorrisdotca_jisho/package/dist/data/words/common.data.js';
import {KANJI} from '../voc/_johnmorrisdotca_jisho/package/dist/data/kanji.data.js';
import {GRADES} from '../voc/_johnmorrisdotca_jisho/package/dist/data/grades.data.js';
import * as W from '../voc/_johnmorrisdotca_jisho/package/dist/words-rows.js';
import fs from 'fs';
console.log(Object.keys(W));
const out=[];
for(const r of COMMON_WORDS.rows){
  const f=r.split('\t'); const flags=f[2];
  const m=flags.match(/^([^~#]*)(?:~([^#]*))?(?:#(.*))?$/);
  const tags=m[2]?W.priorityTags(m[2]):[];
  out.push({r:f[0],w:f[1].split('|'),k:m[1],tags,rank:W.rankOfTags(tags),id:m[3],s:f.slice(3).map(x=>{const p=x.split('¦');return {m:p[0],g:p.slice(1)}})});
}
fs.writeFileSync('kj/common.json',JSON.stringify(out));
fs.writeFileSync('kj/kanjidic.json',JSON.stringify({rows:KANJI.rows,grades:GRADES.grades}));
console.log(out.length,JSON.stringify(out.filter(x=>['日','学校','食べる','大きい','日本'].includes(x.w[0])).map(x=>[x.r,x.w,x.k,x.tags,x.rank,x.s[0]])));
for(const g of '123456') console.log(g,GRADES.grades[g].length);
