import {test} from 'node:test';import assert from 'node:assert/strict';import {Fixture,Qloo,plan,consensus,ProviderError} from '../lib/consensus.mjs';
const members=[{id:'fixture-0',name:'Orbit Letters'},{id:'fixture-1',name:'The Quiet Garden'}];
test('fair and average expose a real policy tradeoff',async()=>{const p=await plan(new Fixture(),members);assert.equal(p.results[0].name,'The Long Way Home');assert.equal(p.baseline[0].name,'Midnight Algorithm');assert.equal(p.mode,'fixture');assert.equal(p.trace.length,5)});
test('unknown coverage is zero, not an invented rank',()=>{const r=consensus([[{id:'a',name:'A'}],[]],[])[0];assert.deepEqual(r.positions,[1,null]);assert.equal(r.floor,0)});
test('forged identity fails',async()=>{await assert.rejects(()=>plan(new Fixture(),[{id:'fake',name:'Orbit Letters'},members[1]]))});
test('missing key fails without fixture fallback',async()=>{await assert.rejects(()=>new Qloo(null).search('film'),ProviderError)});
test('live adapter uses correct host header and contract',async()=>{let request;const q=new Qloo('fake-test-key',async(url,init)=>{request={url,init};return Response.json({results:[{entity_id:'abc',name:'Film'}]})});assert.equal((await q.search('Film'))[0].id,'abc');assert.match(request.url,/^https:\/\/hackathon.api.qloo.com\/search\?/);assert.equal(request.init.headers['X-Api-Key'],'fake-test-key');assert.ok(!request.url.includes('fake-test-key'))});
test('malformed provider data rejected',async()=>{const q=new Qloo('test',async()=>Response.json({results:{}}));await assert.rejects(()=>q.search('film'),ProviderError)});
