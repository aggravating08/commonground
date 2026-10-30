import json, threading, unittest, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from server import Handler, RATE
class HttpTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.url='http://127.0.0.1:'+str(cls.http.server_port)
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
 def setUp(self):RATE.clear()
 def request(self,path,body=None,headers=None):
  req=urllib.request.Request(self.url+path,data=body,headers=headers or {})
  try:
   with urllib.request.urlopen(req) as r:return r.status,r.read(),r.headers
  except urllib.error.HTTPError as r:return r.code,r.read(),r.headers
 def test_home_csp_and_status(self):
  status,body,headers=self.request('/');self.assertEqual(status,200);self.assertIn("script-src 'self'",headers['Content-Security-Policy']);self.assertIn(b'CommonGround',body)
 def test_malformed_json(self):self.assertEqual(self.request('/api/plan',b'{',{'Content-Type':'application/json'})[0],400)
 def test_cross_origin_write(self):self.assertEqual(self.request('/api/plan',b'{}',{'Content-Type':'application/json','Origin':'https://evil.example'})[0],403)
 def test_full_fixture_http(self):
  payload={'mode':'fixture','policy':'fair','members':[{'id':'fixture-0','name':'Orbit Letters'},{'id':'fixture-1','name':'The Quiet Garden'}]}
  status,raw,_=self.request('/api/plan',json.dumps(payload).encode(),{'Content-Type':'application/json'});data=json.loads(raw)
  self.assertEqual(status,200);self.assertEqual(data['results'][0]['name'],'The Long Way Home');self.assertNotEqual(data['results'][0]['id'],data['baseline'][0]['id'])
 def test_search_bounded(self):self.assertEqual(self.request('/api/search?q=a')[0],400)
 def test_wrong_content_type(self):self.assertEqual(self.request('/api/plan',b'{}')[0],415)
