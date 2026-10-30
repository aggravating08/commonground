import json, os, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from engine import Qloo, Fixture, ProviderError, plan
ROOT=Path(__file__).parent
RATE={}; RATE_LOCK=threading.Lock(); JOBS=threading.BoundedSemaphore(2)

def provider(mode):
    if mode=='fixture': return Fixture()
    if mode=='live': return Qloo()
    raise ValueError('Invalid data mode')
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        super().end_headers()
    def reply(self,status,data):
        raw=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(raw))); self.end_headers();self.wfile.write(raw)
    def allowed(self):
        # Shared global quota bounds cost even behind a reverse proxy; no untrusted X-Forwarded-For.
        with RATE_LOCK:
            now=time.monotonic(); times=[t for t in RATE.get('global',[]) if now-t<60]
            if len(times)>=20: return False
            RATE['global']=times+[now]; return True
    def do_GET(self):
        url=urlparse(self.path); params=parse_qs(url.query)
        if url.path=='/api/status': return self.reply(200,{'live_configured':bool(os.environ.get('QLOO_API_KEY')),'live_verified':False})
        if url.path=='/api/search':
            try:
                mode=params.get('mode',['fixture'])[0]; q=params.get('q',[''])[0].strip()
                if not 2<=len(q)<=100: raise ValueError('Search needs 2–100 characters.')
                if not self.allowed(): return self.reply(429,{'error':'Demo request limit reached. Try again in a minute.'})
                self.reply(200,{'results':provider(mode).search(q),'mode':mode})
            except ValueError as exc:self.reply(400,{'error':str(exc)})
            except ProviderError as exc:self.reply(502,{'error':str(exc)})
        elif url.path.startswith('/api/'):self.reply(404,{'error':'Unknown endpoint'})
        else:super().do_GET()
    def do_POST(self):
        if self.path!='/api/plan':return self.reply(404,{'error':'Unknown endpoint'})
        origin=self.headers.get('Origin');host=self.headers.get('Host','')
        if origin and origin not in ('http://'+host,'https://'+host):return self.reply(403,{'error':'Cross-origin request blocked'})
        if self.headers.get_content_type()!='application/json':return self.reply(415,{'error':'Use application/json'})
        if not self.allowed():return self.reply(429,{'error':'Demo request limit reached. Try again in a minute.'})
        if not JOBS.acquire(blocking=False):return self.reply(503,{'error':'Agent is busy. Try again shortly.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4096:raise ValueError('Invalid request size')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict):raise ValueError('Expected an object')
            self.reply(200,plan(provider(body.get('mode')),body.get('members'),body.get('policy','fair')))
        except (ValueError,TypeError) as exc:self.reply(400,{'error':str(exc)})
        except ProviderError as exc:self.reply(502,{'error':str(exc)})
        finally:JOBS.release()
    def log_message(self,format,*args):pass # Avoid retaining taste queries or client addresses.
if __name__=='__main__':
    ThreadingHTTPServer((os.environ.get('HOST','127.0.0.1'),int(os.environ.get('PORT','8790'))),Handler).serve_forever()
