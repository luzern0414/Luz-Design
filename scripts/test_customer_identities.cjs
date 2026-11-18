const {test}=require('node:test'),assert=require('node:assert/strict');
const D=require('../kit/frontend/shared/customer-domain.js');
const clients=n=>Array.from({length:n},(_,i)=>({id:'customer-'+i,name:'客户'+i,accountId:'a',line:'software',stage:'待联系'}));
test('identity allocation is unique and stable across rename reorder and serialization',()=>{
  const s=D.empty();s.clients=clients(108);D.assignIdentities(s);
  const initial=new Map(s.clients.map(c=>[c.id,c.icon]));assert.equal(new Set(initial.values()).size,108);assert.ok([...initial.values()].every(Boolean));
  s.clients.reverse();s.clients.forEach(c=>c.name='名称已修改');const restored=D.initial(JSON.parse(JSON.stringify(s)));
  assert.ok(restored.clients.every(c=>c.icon===initial.get(c.id)));
  restored.clients.push(...clients(1).map(c=>({...c,id:'later-client'})));D.assignIdentities(restored);
  assert.ok(restored.clients.filter(c=>initial.has(c.id)).every(c=>c.icon===initial.get(c.id)));
  assert.ok(![...initial.values()].includes(restored.clients.at(-1).icon));
});
test('pool exhaustion preserves objects without recycling icons',()=>{
  const s=D.empty();s.clients=clients(D.icons.length+4);D.assignIdentities(s);
  const assigned=s.clients.map(c=>c.icon).filter(Boolean);assert.equal(new Set(assigned).size,D.icons.length);
  assert.equal(s.clients.filter(c=>!c.icon).length,4);assert.equal(s.clients.length,D.icons.length+4);
});
test('legacy and duplicated identity assignments are reconciled once',()=>{
  const s=D.empty();s.clients=clients(3).map(c=>({...c,icon:D.icons[0],iconStyle:D.identityStyle}));D.assignIdentities(s);
  assert.equal(new Set(s.clients.map(c=>c.icon)).size,3);const first=JSON.stringify(s.clients);D.assignIdentities(s);assert.equal(JSON.stringify(s.clients),first);
});
