"""Laptop USB bridge. pip install pyserial; python diagnostic_server.py --port COM5"""
import argparse,json,os,secrets,threading,time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from collections import deque
try: import serial
except ImportError: serial=None
class Bridge:
 def __init__(self,port):
  self.port=port;self.dev=None;self.telemetry=None;self.last=0;self.error=None;self.events=deque(maxlen=40);self.lock=threading.Lock()
  if port and serial: threading.Thread(target=self.listen,daemon=True).start()
  elif port: self.error='Install pyserial'
 def listen(self):
  while True:
   try:
    with serial.Serial(self.port,115200,timeout=.2,write_timeout=1) as dev:
     with self.lock: self.dev=dev;self.error=None
     while True:
      line=dev.readline()
      if not line or len(line)>4096: continue
      try: obj=json.loads(line.decode())
      except (ValueError,UnicodeError): continue
      if not isinstance(obj,dict): continue
      with self.lock:
       self.last=time.monotonic()
       if obj.get('type')=='ack': self.events.append(obj)
       elif obj.get('v')==1 and isinstance(obj.get('outputs'),dict): self.telemetry=obj
   except Exception as exc:
    with self.lock: self.error=str(exc)[:150]
   finally:
    with self.lock: self.dev=None
   time.sleep(1)
 def status(self):
  with self.lock:
   connected=bool(self.dev and time.monotonic()-self.last<2.5)
   return dict(connected=connected,port=self.port,error=self.error,telemetry=self.telemetry if connected else None,events=list(self.events))
 def send(self,cmd,side):
  if cmd not in ('test_indicator','stop_test') or (cmd=='test_indicator' and side not in ('left','right','hazard')): raise ValueError('Invalid test')
  payload={'cmd':cmd}
  if cmd=='test_indicator': payload.update(side=side,duration_ms=10000)
  with self.lock:
   if not self.dev or time.monotonic()-self.last>=2.5: raise ConnectionError('Pico offline')
   self.dev.write((json.dumps(payload)+'\n').encode())
   self.events.append({'type':'sent','command':payload})
  return payload
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=str(Path(__file__).parent/'web'),**kw)
 def response(self,code,obj):
  data=json.dumps(obj).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def auth(self): return secrets.compare_digest(self.headers.get('X-Bike-Token',''),self.server.token)
 def do_GET(self):
  if self.path.split('?')[0]=='/api/diagnostics': return self.response(200,self.server.bridge.status()) if self.auth() else self.response(401,{'error':'Invalid token'})
  if self.path.startswith('/api/'): return self.response(404,{'error':'Unknown endpoint'})
  return super().do_GET()
 def do_POST(self):
  if self.path!='/api/test': return self.response(404,{'error':'Unknown endpoint'})
  if not self.auth(): return self.response(401,{'error':'Invalid token'})
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<=256: raise ValueError('Invalid size')
   obj=json.loads(self.rfile.read(n))
   return self.response(202,{'sent':self.server.bridge.send(obj.get('cmd'),obj.get('side'))})
  except (ValueError,TypeError,ConnectionError) as exc: return self.response(400,{'error':str(exc)})
  except Exception: return self.response(503,{'error':'Serial failure'})
 def log_message(self,*args): pass
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port');p.add_argument('--host',default='127.0.0.1');p.add_argument('--http-port',type=int,default=8080);p.add_argument('--token',default=os.environ.get('BIKE_DIAG_TOKEN'));args=p.parse_args()
 token=args.token or secrets.token_urlsafe(24);httpd=ThreadingHTTPServer((args.host,args.http_port),Handler);httpd.bridge=Bridge(args.port);httpd.token=token
 print('Open http://localhost:%d/ (or laptop LAN IP)'%args.http_port,flush=True);print('Diagnostic token:',token,flush=True)
 if args.host=='0.0.0.0':print('WARNING: HTTP not encrypted; trusted Wi-Fi only, no public exposure',flush=True)
 try:httpd.serve_forever()
 except KeyboardInterrupt:pass
