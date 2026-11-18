import fs from 'fs';
const dir='../voc/_johnmorrisdotca_jisho/package/dist/data/examples/';
const out=[];
for(const f of fs.readdirSync(dir)){ if(!/^s\d+\.data\.js$/.test(f)) continue;
  const m=await import(dir+f);
  for(const row of m.PIECE.rows){ const p=row.split('\t'); for(const ex of p.slice(1)){ const q=ex.split('¦'); out.push([q[1],q[2],q[4],q[5],q[6]]); } } }
fs.writeFileSync('examples_all.json',JSON.stringify(out)); console.log(out.length);
