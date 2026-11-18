import fs from 'fs';
const dir='../voc/_johnmorrisdotca_jisho/package/dist/data/words/';
const out=new Set();
for(const f of fs.readdirSync(dir)){ if(!/\.data\.js$/.test(f)) continue;
  const m=await import(dir+f); const t=Object.values(m)[0]; if(!t||!t.rows) continue;
  for(const row of t.rows){ const p=row.split('\t'); if(p.length<3) continue; for(const w of p[1].split('|')) out.add(w+'\t'+p[0]); } }
fs.writeFileSync('allwords.tsv',[...out].join('\n')); console.log(out.size);
