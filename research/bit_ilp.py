"""Exact frame assignment for a bitE8 word (fixed scalar order), HiGHS per component.

Free: frames of A and B gates (catalogue frames only).  Fixed: D, C, start, final, and the last
A frame of every retained-total register (snapshot tops unchanged).  Optional LIFTS=1: each free
frame must contain its given frame.  Objective sum_children d*(64/d)**b0.
Usage: bit_ilp.py WORD.json.gz b0 OUT.json [time_limit]
"""
import json, gzip, sys, os, time
from collections import defaultdict, Counter
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
from bit_model import BitWord, rbasis

wpath, b0, outp = sys.argv[1], float(sys.argv[2]), sys.argv[3]
tl = float(sys.argv[4]) if len(sys.argv) > 4 else 900
M = float(os.environ.get('AMBIENT', '64'))
w = json.loads(gzip.decompress(open(wpath, 'rb').read()))
B = BitWord(w); H0, tops0 = B.chains()
L = w['lines']; NL = len(L)
# closed line-set of every catalogue frame
def closure(mask):
    gens = [L[i] for i in range(NL) if mask >> i & 1]
    rb = rbasis(gens); d = len(rb)
    out = 0
    for i in range(NL):
        if mask >> i & 1 or len(rbasis(list(rb) + [L[i]])) == d: out |= 1 << i
    return out
_cl = {}
def cl(mask):
    if mask not in _cl: _cl[mask] = closure(mask)
    return _cl[mask]
FM = [cl(sum(1 << i for i in f)) for f in w['frames']]
dim = list(B.dim)
FMidx = {}
for i_, m_ in enumerate(FM): FMidx.setdefault(m_, i_)
CAP = int(os.environ.get('CAP', '4000'))
cost = lambda d: d * (M / d) ** b0
n = len(B.events)
fixed = set(g for g, (sec, _, _) in enumerate(B.events) if sec in ('D', 'C'))
for q in w['ret']:
    gs = [g for g in B.touch[q] if g < B.nDA]
    if gs: fixed.add(gs[-1])
FULL = (1 << NL) - 1
# forward minimal / backward maximal line sets
cur = {r: FM[w['start'][r]] for r in range(B.N)}; Lg = [0] * n
for g, (_, _, regs) in enumerate(B.events):
    m = 0
    for r in regs: m |= cur[r]
    m = cl(m)
    if g in fixed: assert m & ~FM[B.F[g]] == 0; m = FM[B.F[g]]
    Lg[g] = m
    for r in regs: cur[r] = m
up = {r: FM[w['final'][r]] for r in range(B.N)}; Ug = [0] * n
for g in range(n - 1, -1, -1):
    regs = B.events[g][2]; u = FULL
    for r in regs: u &= up[r]
    if g in fixed: assert FM[B.F[g]] & ~u == 0; u = FM[B.F[g]]
    Ug[g] = u
    for r in regs: up[r] = u
lifts = os.environ.get('LIFTS') == '1'
cands = {}
for g in range(n):
    if g in fixed: continue
    lo = Lg[g] | (FM[B.F[g]] if lifts else 0)
    cs = [f for f in range(len(FM)) if FM[f] & lo == lo and FM[f] & ~Ug[g] == 0]
    if os.environ.get('CLOSED') == '1':  # every root-closed subspace in the window, new ones appended
        lo_c = cl(lo); seen_m = {lo_c}; frontier = [lo_c]; U = Ug[g]
        while frontier and len(seen_m) < CAP:
            nxt = []
            for m0 in frontier:
                rest = U & ~m0
                while rest:
                    i = (rest & -rest).bit_length() - 1; rest &= rest - 1
                    m1 = cl(m0 | (1 << i))
                    if m1 & ~U == 0 and m1 not in seen_m: seen_m.add(m1); nxt.append(m1)
            frontier = nxt
        for m1 in seen_m:
            if m1 not in FMidx: FMidx[m1] = len(FM); FM.append(m1); dim.append(len(rbasis([L[i] for i in range(NL) if m1 >> i & 1])))
            cs.append(FMidx[m1])
    # one representative per distinct line set
    seen = {}; [seen.setdefault(FM[f], f) for f in cs]
    cands[g] = sorted(seen.values(), key=lambda f: (dim[f], f))
    assert any(FM[f] == FM[B.F[g]] for f in cands[g]), ('given frame not a candidate', g)
free = [g for g in cands if len(cands[g]) > 1]
fs = set(free)
const = {g: B.F[g] for g in range(n) if g not in fs}
print('events', n, 'fixed', len(fixed), 'free', len(free), 'max cands', max(len(cands[g]) for g in free), flush=True)
# chains
def frm(node): return node[1] if node[0] == 'c' else None
chains = {}
for r in range(B.N):
    nodes = [('c', w['start'][r])]
    for g in B.touch.get(r, []): nodes.append(('g', g) if g in fs else ('c', const[g]))
    nodes.append(('c', w['final'][r])); chains[r] = nodes
par = {g: g for g in free}
def find(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
for nodes in chains.values():
    for a, b in zip(nodes, nodes[1:]):
        if a[0] == 'g' and b[0] == 'g': par[find(a[1])] = find(b[1])
comps = defaultdict(list)
for g in free: comps[find(g)].append(g)
def inside(fa, fb): return FM[fa] & ~FM[fb] == 0
def pc(fa, fb): return 0.0 if FM[fa] == FM[fb] else cost(dim[fb] - dim[fa])
base = 0.0; pairs = defaultdict(list)
for r, nodes in chains.items():
    for a, b in zip(nodes, nodes[1:]):
        if a[0] == 'c' and b[0] == 'c':
            assert inside(a[1], b[1]), (r, a, b); base += pc(a[1], b[1])
        else: pairs[find(a[1]) if a[0] == 'g' else find(b[1])].append((a, b))
newF = list(B.F); total = base
print('components', len(comps), 'largest', max(len(v) for v in comps.values()), flush=True)
for ci, (root, gates) in enumerate(sorted(comps.items(), key=lambda kv: len(kv[1]))):
    t0 = time.time(); var = {}; obj = []; ub = []; rows = []; cols = []; vals = []; lo = []; hi = []; nr = 0
    def add(k, c):
        var[k] = len(obj); obj.append(c); ub.append(1.0); return var[k]
    for g in gates:
        for f in cands[g]: add(('x', g, f), 0.0)
        for f in cands[g]: rows.append(nr); cols.append(var['x', g, f]); vals.append(1.0)
        lo.append(1); hi.append(1); nr += 1
    for a, b in pairs[root]:
        if a[0] == 'c':
            for f in cands[b[1]]:
                if not inside(a[1], f): ub[var['x', b[1], f]] = 0
                else: obj[var['x', b[1], f]] += pc(a[1], f)
        elif b[0] == 'c':
            for f in cands[a[1]]:
                if not inside(f, b[1]): ub[var['x', a[1], f]] = 0
                else: obj[var['x', a[1], f]] += pc(f, b[1])
        else:
            u, v = a[1], b[1]; y1 = defaultdict(list); y2 = defaultdict(list)
            for f in cands[u]:
                for h in cands[v]:
                    if inside(f, h):
                        j = add(('y', u, v, f, h, len(obj)), pc(f, h)); y1[f].append(j); y2[h].append(j)
            for f in cands[u]:
                for j in y1[f]: rows.append(nr); cols.append(j); vals.append(1.0)
                rows.append(nr); cols.append(var['x', u, f]); vals.append(-1.0); lo.append(0); hi.append(0); nr += 1
            for h in cands[v]:
                for j in y2[h]: rows.append(nr); cols.append(j); vals.append(1.0)
                rows.append(nr); cols.append(var['x', v, h]); vals.append(-1.0); lo.append(0); hi.append(0); nr += 1
    A = coo_matrix((vals, (rows, cols)), shape=(nr, len(obj))).tocsr()
    integ = np.array([1 if k[0] == 'x' else 0 for k in var])
    res = milp(np.array(obj), constraints=LinearConstraint(A, lo, hi), integrality=integ, bounds=Bounds(0, np.array(ub)), options=dict(time_limit=tl, mip_rel_gap=0))
    assert res.x is not None, res.message
    for g in gates:
        pick = [f for f in cands[g] if res.x[var['x', g, f]] > 0.5]; assert len(pick) == 1; newF[g] = pick[0]
    total += res.fun
    if len(gates) > 50: print(f'comp {ci} gates {len(gates)} vars {len(obj)} obj {res.fun:.3f} {res.message[:30]} {time.time()-t0:.1f}s', flush=True)
H1 = Counter(); cur1 = list(w['start'])
for g, (sec, i, regs) in enumerate(B.events):
    for r in regs:
        a = cur1[r]; assert FM[a] & ~FM[newF[g]] == 0
        if dim[newF[g]] > dim[a]: H1[dim[newF[g]] - dim[a]] += 1
        cur1[r] = newF[g]
for r, f in enumerate(w['final']):
    a = cur1[r]; assert FM[a] & ~FM[f] == 0
    if dim[f] > dim[a]: H1[dim[f] - dim[a]] += 1
H1 = dict(sorted(H1.items())); tops1 = tops0
new_frames = sorted(set(f for f in newF if f >= len(w['frames'])))
print('new frames used', len(new_frames))
assert [B.dim[t] for t in tops1] == [B.dim[t] for t in tops0] and [FM[t] for t in tops1] == [FM[t] for t in tops0]
f0 = sum(n_ * cost(d) for d, n_ in H0.items()); f1 = sum(n_ * cost(d) for d, n_ in H1.items())
print('given', H0, round(f0, 4)); print('ILP  ', H1, round(f1, 4), 'delta', round(f1 - f0, 4), flush=True)
json.dump(dict(new_frame_masks=[FM[f] for f in new_frames], frames=newF, profile=H1, given=H0, fee_given=f0, fee_ilp=f1, ilp_objective=total), open(outp, 'w'))
