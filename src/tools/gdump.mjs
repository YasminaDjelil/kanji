import fs from 'fs';
const dir='../voc/_johnmorrisdotca_jisho/package/dist/data/words/';
const out={};
for(const f of fs.readdirSync(dir)){ if(!/\.data\.js$/.test(f)) continue;
  const m=await import(dir+f); const t=Object.values(m)[0]; if(!t||!t.rows) continue;
  for(const row of t.rows){ const p=row.split('\t'); if(p.length<4||!p[3].includes('¦')) continue; const g=p[3].split('¦').slice(1,4);
    for(const w of p[1].split('|')){ const k=w+'\t'+p[0]; if(!(k in out)) out[k]=g; } } }
fs.writeFileSync('allgloss.json',JSON.stringify(out)); console.log(Object.keys(out).length);
