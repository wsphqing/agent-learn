import concurrent.futures, urllib.request, pathlib, json, re
from html.parser import HTMLParser
sources = {
'overview':'https://docs.docker.com/get-started/docker-overview/',
'install':'https://docs.docker.com/engine/install/',
'containers':'https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/',
'build-best':'https://docs.docker.com/build/building/best-practices/',
'multistage':'https://docs.docker.com/build/building/multi-stage/',
'build-secrets':'https://docs.docker.com/build/building/secrets/',
'dockerfile':'https://docs.docker.com/reference/dockerfile/',
'compose-startup':'https://docs.docker.com/compose/how-tos/startup-order/',
'compose-net':'https://docs.docker.com/compose/how-tos/networking/',
'compose-secrets':'https://docs.docker.com/compose/how-tos/use-secrets/',
'volumes':'https://docs.docker.com/engine/storage/volumes/',
'bind-mounts':'https://docs.docker.com/engine/storage/bind-mounts/',
'network':'https://docs.docker.com/engine/network/',
'ports':'https://docs.docker.com/engine/network/port-publishing/',
'containerd':'https://docs.docker.com/engine/storage/containerd/',
'overlay2':'https://docs.docker.com/engine/storage/drivers/overlayfs-driver/',
'resources':'https://docs.docker.com/engine/containers/resource_constraints/',
'rootless':'https://docs.docker.com/engine/security/rootless/',
'security':'https://docs.docker.com/engine/security/',
'multiplatform':'https://docs.docker.com/build/building/multi-platform/',
'buildkit':'https://docs.docker.com/build/buildkit/',
'oci':'https://github.com/opencontainers/runtime-spec/blob/main/config-linux.md',
'containerd-arch':'https://github.com/containerd/containerd/blob/main/docs/getting-started.md',
'postgres':'https://hub.docker.com/_/postgres',
'ollama':'https://docs.ollama.com/docker',
'ollama-api':'https://docs.ollama.com/api/generate',
'qwen':'https://ollama.com/library/qwen2.5:0.5b',
'restart':'https://docs.docker.com/engine/containers/start-containers-automatically/',
'logs':'https://docs.docker.com/engine/logging/configure/',
'prune':'https://docs.docker.com/engine/manage-resources/pruning/'
}
class Text(HTMLParser):
 def __init__(self): super().__init__(); self.out=[]; self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'): self.skip+=1
  if t in ('p','h1','h2','h3','li','pre','tr'): self.out.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style'): self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip: self.out.append(d)
def fetch(k,u):
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r: raw=r.read().decode(); status=r.status
  p=Text(); p.feed(raw); s=''.join(p.out); s=re.sub(r'[ \t]+',' ',s); pathlib.Path('.work/sources/'+k+'.txt').write_text(s)
  return {'id':k,'url':u,'status':status,'chars':len(s)}
 except Exception as e: return {'id':k,'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 results=list(ex.map(lambda kv:fetch(*kv),sources.items()))
pathlib.Path('.work/sources/index.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for x in results: print(json.dumps(x,ensure_ascii=False))
