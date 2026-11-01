import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
const db=JSON.parse(fs.readFileSync(path.resolve('data/seed.json'),'utf8'));
const src=new Map(db.sources.map(x=>[x.id,x]));
const cmp=new Map(db.companies.map(x=>[x.id,x]));
test('T01 / data schema and unique IDs',()=>{
 assert.equal(db.schemaVersion,1);assert.equal(db.companies.length,5);
 assert.equal(src.size,db.sources.length);assert.equal(cmp.size,db.companies.length);
 assert.ok(db.classification.levels.length===4);
});
test('T02 / all published numbers cite HTTPS original',()=>{
 for(const s of db.sources){assert.match(s.url,/^https:\/\//);assert.ok(s.publisher&&s.location&&s.period);assert.equal(s.verified,true)}
 for(const c of db.companies){assert.ok(c.evidence.length>0);for(const id of c.evidence)assert.ok(src.has(id));}
});
test('T03 / financial ratio calculation against original reports',()=>{
 assert.ok(Math.abs(37456518745.90/38239935640.67*100-97.95)<0.01);
 assert.ok(Math.abs(24771155676.88/24841854840.22*100-99.72)<0.01);
 assert.ok(Math.abs((2084386267.76+2997945108.74)/5163432471.16*100-98.43)<0.01);
 assert.equal(cmp.get('cohr').revenue,5275);
 assert.equal(cmp.get('lite').revenue,2005.6);
});
test('T04 / every claim linked to company and evidence',()=>{
 for(const c of db.claims){assert.ok(cmp.has(c.company));assert.ok(['A','B','C','D','E'].includes(c.level));for(const id of c.evidence)assert.ok(src.has(id));if(c.level==='A')assert.equal(c.status,'verified')}
});
test('T05 / CPO R&D never upgraded to realized revenue',()=>{
 const c=db.claims.find(x=>x.id==='C04');assert.equal(c.level,'C');assert.ok(c.explanation.includes('不属于订单'));
 assert.equal(db.claims.find(x=>x.id==='C08').level,'E');
});
test('T06 / peer relations show comparability and noncomparability',()=>{
 assert.ok(db.comparisons.length>=4);for(const p of db.comparisons){assert.ok(cmp.has(p.a)&&cmp.has(p.b));assert.ok(p.why.length>=2&&p.not.length>=2);for(const x of p.sources)assert.ok(src.has(x));}
});
test('T07 / scenarios have observable financial indicators',()=>{
 for(const e of db.events){assert.equal(e.status,'情景假设');assert.ok(e.paths.length>=3);assert.ok(e.observe.length>=3);assert.ok(src.has(e.source));}
});
test('T08 / income labels explicitly distinguish periods and units',()=>{
 for(const c of db.companies){assert.ok(c.period&&c.denominator);assert.match(c.revenueLabel,/亿(元|美元)/)}
});
