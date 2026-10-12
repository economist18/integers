"""Exact frame retiming of the PR484 word by ILP (HiGHS), component by component.

Variables: x[g,s] for each free gate g and each subspace s in its global window [L_g, U_g]
(forward-propagated minimal frames / backward-propagated maximal frames, fixed gates as constants).
Each register chain start -> gates -> final contributes, per consecutive pair (u,v), cost c(rank v - rank u)
if the frames differ (0 if equal), with nesting s_u <= s_v.  Pairs of two free gates use a
transportation linearisation y[u,v,s,s'] (tight).  Objective weight c(d) = d*(73/d)**b0.
Usage: retime_ilp.py FULL-WORD.json.gz START_FRAMES.json|- b0 OUT.json [time_limit_per_component]
"""
import json, gzip, sys, math, time, os
from collections import defaultdict
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_matrix
import retime_opt as R


def subspaces_between(L, U):
    """All subspaces S with L <= S <= U (as canonical bases)."""
    spanL = R.span(L)
    # complement vectors of L inside U
    comp = []
    cur = L
    for v in U:
        if not R.inside(R.basis([v]), cur):
            comp.append(v); cur = R.join(cur, (v,))
    k = len(comp)
    out = set()
    # enumerate subspaces of span(comp) via all subsets of vectors in that span, by echelon bases
    vecs = []
    for mask in range(1, 1 << k):
        x = 0
        for i in range(k):
            if mask >> i & 1: x ^= comp[i]
        vecs.append(x)
    # BFS over subspaces of the quotient
    frontier = {L}; out.add(L)
    while frontier:
        nxt = set()
        for S in frontier:
            for x in vecs:
                if x in R.span(S): continue
                T = R.join(S, (x,))
                if T not in out: out.add(T); nxt.add(T)
        frontier = nxt
    assert all(R.inside(L, s) and R.inside(s, U) for s in out)
    return sorted(out)


def main():
    wpath, frames, b0, outp = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    tl = float(sys.argv[5]) if len(sys.argv) > 5 else 600
    w = json.loads(gzip.decompress(open(wpath, 'rb').read()))
    fr = json.load(open(frames)) if frames != '-' else None
    W = R.Word(w, fr and fr['A'], fr and fr['B'])
    MAMB = float(os.environ.get('AMBIENT', '73')); c = lambda d: d * (MAMB / d) ** b0
    n = len(W.events); fixedset = W.fixed | set(W.forced)
    # global windows
    cur = {r: W.start[r] for r in range(W.n)}; Lg = [None] * n
    for g, (_, _, regs) in enumerate(W.events):
        if g == W.nA:
            for r, req in W.cutreq.items(): cur[r] = req
        L = R.ZERO
        for r in regs: L = R.join(L, cur[r])
        if g in fixedset: L = W.F[g]
        Lg[g] = L
        for r in regs: cur[r] = L
    up = {r: W.final[r] for r in range(W.n)}; Ug = [None] * n
    for g in range(n - 1, -1, -1):
        regs = W.events[g][2]
        if g == W.nA - 1:
            for r, req in W.cutreq.items(): up[r] = req
        U = R.FULL
        for r in regs: U = R.meet(U, up[r])
        if g in fixedset: U = W.F[g]
        Ug[g] = U
        for r in regs: up[r] = U
    if os.environ.get('LIFTS') == '1':  # interface of PR534: every frame must contain its given frame
        for g in range(n):
            if g not in fixedset:
                Lg[g] = R.join(Lg[g], W.F[g])
                assert R.inside(Lg[g], Ug[g]), ('given frame outside window', g)
    free = [g for g in range(n) if Lg[g] != Ug[g]]
    fs = set(free)
    const = {g: Lg[g] for g in range(n) if g not in fs}
    # register chains as node lists; node = ('c', frame) or ('g', g)
    chains = {}
    for r in range(W.n):
        nodes = [('c', W.start[r])]
        crossed = False
        for g in W.touch.get(r, []):
            if g >= W.nA and not crossed:
                crossed = True
                if r in W.cutreq: nodes.append(('c', W.cutreq[r]))
            nodes.append(('g', g) if g in fs else ('c', const[g]))
        if not crossed and r in W.cutreq: nodes.append(('c', W.cutreq[r]))
        if r in W.centre_regs: nodes.append(('c', W.cutreq[r]))
        nodes.append(('c', W.final[r]))
        chains[r] = nodes
    # components over free gates
    par = {g: g for g in free}
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for r, nodes in chains.items():
        for a, b in zip(nodes, nodes[1:]):
            if a[0] == 'g' and b[0] == 'g': par[find(a[1])] = find(b[1])
    comps = defaultdict(list)
    for g in free: comps[find(g)].append(g)
    cands = {g: subspaces_between(Lg[g], Ug[g]) for g in free}
    print('free', len(free), 'components', len(comps), 'max cands', max(len(v) for v in cands.values()), flush=True)
    newF = list(W.F)
    for g in const: newF[g] = const[g]
    # constant-constant pair costs
    base_const = 0.0
    total_obj = 0.0
    pairs_by_comp = defaultdict(list)
    for r, nodes in chains.items():
        for a, b in zip(nodes, nodes[1:]):
            if a[0] == 'c' and b[0] == 'c':
                assert R.inside(a[1], b[1]), (r, a, b)
                if a[1] != b[1]: base_const += c(len(b[1]) - len(a[1]))
            else:
                key = find(a[1]) if a[0] == 'g' else find(b[1])
                pairs_by_comp[key].append((a, b))
    print('constant part', base_const, flush=True)
    for ci, (root, gates) in enumerate(sorted(comps.items(), key=lambda kv: len(kv[1]))):
        t0 = time.time()
        var = {}; obj = []; rows = []; cols = []; vals = []; lo = []; hi = []; nr = 0; ub = []
        def addvar(key, cost, upper=1.0):
            var[key] = len(obj); obj.append(cost); ub.append(upper); return var[key]
        for g in gates:
            for s in cands[g]: addvar(('x', g, s), 0.0)
            # one-hot
            for s in cands[g]: rows.append(nr); cols.append(var['x', g, s]); vals.append(1.0)
            lo.append(1.0); hi.append(1.0); nr += 1
        for a, b in pairs_by_comp[root]:
            if a[0] == 'c':
                g = b[1]
                for s in cands[g]:
                    if not R.inside(a[1], s): ub[var['x', g, s]] = 0.0
                    elif a[1] != s: obj[var['x', g, s]] += c(len(s) - len(a[1]))
            elif b[0] == 'c':
                g = a[1]
                for s in cands[g]:
                    if not R.inside(s, b[1]): ub[var['x', g, s]] = 0.0
                    elif s != b[1]: obj[var['x', g, s]] += c(len(b[1]) - len(s))
            else:
                u, v = a[1], b[1]
                ys = defaultdict(list); ys2 = defaultdict(list)
                for s in cands[u]:
                    for t in cands[v]:
                        if R.inside(s, t):
                            j = addvar(('y', u, v, s, t, len(obj)), c(len(t) - len(s)) if s != t else 0.0)
                            ys[s].append(j); ys2[t].append(j)
                for s in cands[u]:
                    for j in ys[s]: rows.append(nr); cols.append(j); vals.append(1.0)
                    rows.append(nr); cols.append(var['x', u, s]); vals.append(-1.0); lo.append(0.0); hi.append(0.0); nr += 1
                for t in cands[v]:
                    for j in ys2[t]: rows.append(nr); cols.append(j); vals.append(1.0)
                    rows.append(nr); cols.append(var['x', v, t]); vals.append(-1.0); lo.append(0.0); hi.append(0.0); nr += 1
        A = coo_matrix((vals, (rows, cols)), shape=(nr, len(obj))).tocsr()
        integ = np.array([1 if k[0] == 'x' else 0 for k in var], dtype=int)
        res = milp(np.array(obj), constraints=LinearConstraint(A, lo, hi), integrality=integ, bounds=Bounds(0, np.array(ub)),
                   options=dict(time_limit=tl, mip_rel_gap=0))
        assert res.x is not None, (ci, res.message)
        for g in gates:
            pick = [s for s in cands[g] if res.x[var['x', g, s]] > 0.5]
            assert len(pick) == 1; newF[g] = pick[0]
        total_obj += res.fun
        print(f'comp {ci} gates {len(gates)} vars {len(obj)} obj {res.fun:.4f} status {res.status} {res.message[:40]} {time.time()-t0:.1f}s', flush=True)
    W.F = newF
    p = W.profile()
    print('ILP total', base_const + total_obj, 'model total', R.total(W), 'profile', p, flush=True)
    json.dump({'A': [list(f) for f in W.F[:W.nA]], 'B': [list(f) for f in W.F[W.nA:]], 'profile': p, 'objective': base_const + total_obj}, open(outp, 'w'))


if __name__ == '__main__': main()
