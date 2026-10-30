import io, json, unittest
from engine import Fixture, Qloo, ProviderError, consensus, plan
class EngineTests(unittest.TestCase):
 def test_fair_policy_protects_floor(self):
  lists=[[{'id':'a','name':'A'},{'id':'b','name':'B'},{'id':'c','name':'C'}],[{'id':'c','name':'C'},{'id':'b','name':'B'}]]
  self.assertEqual(consensus(lists,[])[0]['id'],'b')
 def test_missing_is_unknown_zero(self):
  rows=consensus([[{'id':'a','name':'A'}],[]],[]);self.assertEqual(rows[0]['positions'],[1,None]);self.assertEqual(rows[0]['floor'],0)
 def test_seeds_excluded(self):self.assertEqual(consensus([[{'id':'a','name':'A'}]]*2,['a']),[])
 def test_fixture_plan_has_trace_and_no_seeds(self):
  r=plan(Fixture(),[{'id':'fixture-0','name':'Orbit Letters'},{'id':'fixture-1','name':'The Quiet Garden'}],'fair')
  self.assertEqual(r['mode'],'fixture');self.assertEqual(len(r['trace']),5);self.assertTrue(all(x['id'] not in ['fixture-0','fixture-1'] for x in r['results']))
 def test_forged_seed_rejected(self):
  with self.assertRaises(ValueError):plan(Fixture(),[{'id':'bad','name':'Orbit Letters'}]*2,'fair')
 def test_invalid_group_and_policy(self):
  for people,policy in [([], 'fair'),([{}]*5,'fair'),([{}]*2,'invalid')]:
   with self.assertRaises(ValueError):plan(Fixture(),people,policy)
 def test_missing_key_never_falls_back(self):
  p=Qloo();p.key=None
  with self.assertRaises(ProviderError):p.search('hello')
 def test_contract_and_secret_header(self):
  calls=[]
  def opener(req,timeout):calls.append(req);return io.BytesIO(json.dumps({'results':[{'entity_id':'id','name':'Title'}]}).encode())
  q=Qloo('test-not-real',opener);self.assertEqual(q.search('Title')[0]['id'],'id');self.assertTrue(calls[0].full_url.startswith('https://hackathon.api.qloo.com/search?'));self.assertNotIn('test-not-real',calls[0].full_url);self.assertEqual(calls[0].get_header('X-api-key'),'test-not-real')
 def test_bad_schema_rejected(self):
  q=Qloo('test',lambda *a,**k:io.BytesIO(b'{"results":{}}'))
  with self.assertRaises(ProviderError):q.search('hello')
 def test_insights_contract(self):
  calls=[]
  def opener(req,timeout):calls.append(req);return io.BytesIO(b'{"results":{"entities":[{"entity_id":"x","name":"X"}]}}')
  self.assertEqual(Qloo('test',opener).recommend('seed')[0]['name'],'X');self.assertIn('signal.interests.entities=seed',calls[0].full_url)
if __name__=='__main__':unittest.main()
