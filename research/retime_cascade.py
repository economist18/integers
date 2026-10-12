"""Cascade (push) moves on top of retime_opt.Word. Raise: set F_g:=join(F_g,f) and push
the requirement forward along every participant chain; lower: F_g:=meet(F_g,f) pushed backward.
Fixed/forced gates, cut requirements, start and final frames bound the cascade."""
import json,gzip,sys,math,random
import retime_opt as R

def cascade(W,g,f,up):
    new={};q=[(g,f)]
    while q:
        h,req=q.pop()
        cur=new.get(h,W.F[h])
        nf=R.join(cur,req) if up else R.meet(cur,req)
        if nf==cur: continue
        if h in W.fixed or h in W.forced: return None
        new[h]=nf
        for r in W.events[h][2]:
            gs=W.touch[r];k=W.pos[r,h]
            if up:
                if k+1<len(gs):
                    h2=gs[k+1]
                    if h<W.nA<=h2 and r in W.cutreq:
                        if not R.inside(nf,W.cutreq[r]):return None
                        continue
                    if not R.inside(nf,new.get(h2,W.F[h2])):q.append((h2,nf))
                else:
                    lim=W.cutreq[r] if (h<W.nA and r in W.cutreq) else W.final[r]
                    if not R.inside(nf,lim):return None
            else:
                if k>0:
                    h2=gs[k-1]
                    if h2<W.nA<=h and r in W.cutreq:
                        if not R.inside(W.cutreq[r],nf):return None
                        continue
                    if not R.inside(new.get(h2,W.F[h2]),nf):q.append((h2,nf))
                else:
                    s=W.cutreq[r] if (h>=W.nA and r in W.cutreq) else W.start[r]
                    if not R.inside(s,nf):return None
    return new

def apply_cost(W,new):
    regs=set(r for h in new for r in W.events[h][2])
    before=sum(W.reg_cost(r) for r in regs)
    old={h:W.F[h] for h in new}
    for h,f in new.items():W.F[h]=f
    after=sum(W.reg_cost(r) for r in regs)
    for h,f in old.items():W.F[h]=f
    return after-before

def moves(W,g):
    out=[]
    for r in W.events[g][2]:
        gs=W.touch[r];k=W.pos[r,g]
        for kk in range(k+1,min(len(gs),k+6)):out.append((W.F[gs[kk]],True))
        for kk in range(max(0,k-5),k):out.append((W.F[gs[kk]],False))
        out.append((W.final[r],True))
    return out

def run(W,rng,sweeps,T0,log=print):
    gates=[g for g in range(len(W.events)) if g not in W.fixed and g not in W.forced]
    for s in range(sweeps):
        T=T0*(1-s/max(1,sweeps));acc=0;dt=0
        rng.shuffle(gates)
        for g in gates:
            best=None
            for f,up in moves(W,g):
                new=cascade(W,g,f,up)
                if not new:continue
                d=apply_cost(W,new)
                if d==math.inf:continue
                if d< -1e-9 or (T>0 and rng.random()<math.exp(-d/T)):
                    if best is None or d<best[0]:best=(d,new)
            if best:
                for h,f in best[1].items():W.F[h]=f
                acc+=1;dt+=best[0]
        log(f'sweep {s} T={T:.3f} acc={acc} delta={dt:.3f} total={R.total(W):.3f}',flush=True) if False else print(f'sweep {s} T={T:.3f} acc={acc} delta={dt:.3f} total={R.total(W):.3f}',flush=True)
        if T==0 and acc==0:break

if __name__=='__main__':
    wpath,frames,out,seed,T0,sweeps=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),float(sys.argv[5]),int(sys.argv[6])
    w=json.loads(gzip.decompress(open(wpath,'rb').read()))
    fr=json.load(open(frames)) if frames!='-' else None
    W=R.Word(w,fr and fr['A'],fr and fr['B']);print('start',W.profile(),R.total(W),flush=True)
    rng=random.Random(seed)
    if T0>0:run(W,rng,sweeps,T0)
    run(W,rng,100,0)
    R.descend(W,rng,0,50)
    run(W,rng,100,0)
    p=W.profile();print('end',p,R.total(W),sum(r*n for r,n in p.items()),flush=True)
    json.dump({'A':[list(f) for f in W.F[:W.nA]],'B':[list(f) for f in W.F[W.nA:]],'profile':p},open(out,'w'))
