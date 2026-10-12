import json,gzip,sys,hashlib,copy
from collections import Counter
sys.path.insert(0,'/home/user/w501/research/r489-pooled-retimed-complex/code')
import apply_retime as AR
w=json.loads(gzip.decompress(open('/home/user/integers/runs/r505-a/base/split-centres/FULL-WORD.json.gz','rb').read()))
p=json.loads(gzip.decompress(open('/home/user/w501/research/r489-pooled-retimed-complex/data/RETIME-FRAMES.json.gz','rb').read()))
ok=all(w[part][i][-1]==old for part in 'AB' for i,old,new in p[part]);print('old frames match',ok)
z=copy.deepcopy(w)
for part in 'AB':
  for i,old,new in p[part]: z[part][i][-1]=new
print('base local',AR.profile(w));print('retimed local',AR.profile(z))
# which report fields differ from what map expects? compare canonical hash w/o report
def h(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
print({k:(type(v).__name__) for k,v in w['report'].items() if isinstance(v,float)})
json.dump({'A':[e[-1] for e in z['A']],'B':[e[-1] for e in z['B']]},open('retimed_frames.json','w'))
