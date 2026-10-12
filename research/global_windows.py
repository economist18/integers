import json,gzip,sys
from collections import Counter
import retime_opt as R
w=json.loads(gzip.decompress(open(sys.argv[1],'rb').read()))
fr=json.load(open('retimed_frames.json'));W=R.Word(w,fr['A'],fr['B'])
n=len(W.events);fixed=W.fixed|set(W.forced)
# forward minimal frames
cur={r:W.start[r] for r in range(W.n)};Lg=[None]*n
for g,(part,i,regs) in enumerate(W.events):
    if g==W.nA:
        for r,req in W.cutreq.items():cur[r]=req
    L=R.ZERO
    for r in regs:L=R.join(L,cur[r])
    if g in fixed:
        assert R.inside(L,W.F[g]);L=W.F[g]
    Lg[g]=L
    for r in regs:cur[r]=L
# backward maximal frames
up={r:W.final[r] for r in range(W.n)};Ug=[None]*n
for g in range(n-1,-1,-1):
    part,i,regs=W.events[g]
    if g==W.nA-1:
        for r,req in W.cutreq.items():up[r]=req
    U=R.FULL
    for r in regs:U=R.meet(U,up[r])
    if g in fixed:
        assert R.inside(W.F[g],U),g;U=W.F[g]
    Ug[g]=U
    for r in regs:up[r]=U
gap=Counter();bad=0
for g in range(n):
    if not R.inside(Lg[g],Ug[g]):bad+=1;continue
    if g in fixed:continue
    gap[len(Ug[g])-len(Lg[g])]+=1
print('infeasible',bad,'gap histogram (free gates)',dict(sorted(gap.items())))
json.dump({'L':[list(x) for x in Lg],'U':[list(x) for x in Ug]},open('global_windows.json','w'))
