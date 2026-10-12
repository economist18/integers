"""Frame-retiming local search on the PR484 gauge80-kernel42 complex word.

Model (mirrors apply_retime.profile / audit_gk climb rules):
- every register keeps a nested chain of frames; a gate runs at one common frame
  for all its registers; each strict increase is one paid child of rank delta;
- the first FIXED_A A gates keep their frames (same interface PR501 kept);
- targets must equal their target level, and centres their centre frame, at the cut;
- after B every register climbs to its final frame (FULL, or perp(port) for targets).
Scalar payloads and order never change.  Output is a frame list for A and B; the
candidate must then pass the repository's full rebuild/audit pipeline.
"""
import json, gzip, sys, math, random, copy
from collections import Counter, defaultdict

FIXED_A = int(__import__("os").environ.get("FIXED_A","531"))


def basis(vs):
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1: x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in b:
                if b[q] >> p & 1: b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


_join = {}
def join(a, b):
    k = (a, b) if a <= b else (b, a)
    r = _join.get(k)
    if r is None: r = _join[k] = basis(a + b)
    return r

def inside(a, b): return join(a, b) == b

_meet = {}
def meet(a, b):
    k = (a, b) if a <= b else (b, a)
    r = _meet.get(k)
    if r is None:
        sa = span(a); sb = span(b)
        r = _meet[k] = basis(sorted(sa & sb))
    return r

_span = {}
def span(a):
    r = _span.get(a)
    if r is None:
        s = {0}
        for v in a: s |= {u ^ v for u in s}
        r = _span[a] = frozenset(s)
    return r

FULL = basis([1 << i for i in range(9)])
ZERO = ()
M = 73

def cost(d):  # first-order moment proxy per paid child of rank d
    return d * math.log(M / d)


class Word:
    def __init__(self, w, frames_A=None, frames_B=None):
        self.w = w
        v = len(w['ports']); self.v = v; n = 2 * v + w['report']['R']; self.n = n
        self.events = []  # (part, idx, regs)
        for part in ('A', 'B'):
            for i, e in enumerate(w[part]):
                regs = [e[1], e[2]] if e[0] == 'add' else [e[1]]
                self.events.append((part, i, regs))
        self.nA = len(w['A'])
        fa = frames_A if frames_A is not None else [e[-1] for e in w['A']]
        fb = frames_B if frames_B is not None else [e[-1] for e in w['B']]
        self.F = [basis(f) for f in fa] + [basis(f) for f in fb]
        self.start = [basis([p]) for p in w['ports']] + [ZERO] * v + [basis(w['start_extra'].get(str(r), [])) for r in range(2 * v, n)]
        self.final = [FULL] * v + [basis([x for x in range(1, 512) if not (x & w['ports'][r - v]).bit_count() % 2]) for r in range(v, 2 * v)] + [FULL] * w['report']['R']
        lev = {int(t): basis(E) for t, E in w.get('target_levels', {}).items()}
        self.cutreq = {}
        for t in range(v): self.cutreq[v + t] = lev.get(t, ZERO)
        for r, F in zip(w['centers'], w['center_frames']): self.cutreq[r] = basis(F)
        # centre descents in B (fixed cost, not recomputed, as in profile())
        self.touch = defaultdict(list)
        for g, (_, _, regs) in enumerate(self.events):
            for r in regs: self.touch[r].append(g)
        self.pos = {}
        for r, gs in self.touch.items():
            for k, g in enumerate(gs): self.pos[r, g] = k
        self.fixed = set(range(FIXED_A))
        # gates that must equal a cut requirement: last A touch of a target/centre
        self.forced = {}
        for r, req in self.cutreq.items():
            gs = [g for g in self.touch.get(r, []) if g < self.nA]
            if gs:
                self.forced.setdefault(gs[-1], []).append(req)
        # centres never touched in B (checked)
        self.centre_regs = set(w['centers'])

    # chain of frames for register r as seen by the climb rule
    def chain(self, r):
        seq = [('s', self.start[r])]
        for g in self.touch.get(r, []):
            if g == self.nA_cut_marker(r, g): pass
            seq.append((g, self.F[g]))
        return seq

    def nA_cut_marker(self, r, g): return None

    def reg_cost(self, r, F=None):
        F = F or self.F
        cur = self.start[r]; c = 0.0; crossed = False
        for g in self.touch.get(r, []):
            if g >= self.nA and not crossed:
                crossed = True
                if r in self.cutreq:
                    if cur != self.cutreq[r]: return math.inf
                    if r in self.centre_regs: return math.inf  # centres must not be touched in B
            f = F[g]
            if f != cur:
                if not inside(cur, f): return math.inf
                c += cost(len(f) - len(cur)); cur = f
        if not crossed and r in self.cutreq and cur != self.cutreq[r]: return math.inf
        if r in self.centre_regs: cur = self.cutreq[r]  # stays at centre frame for final climb, as in profile()
        f = self.final[r]
        if f != cur:
            if not inside(cur, f): return math.inf
            c += cost(len(f) - len(cur))
        return c

    def profile(self, F=None):
        F = F or self.F
        paid = Counter()
        for r in range(self.n):
            cur = self.start[r]; crossed = False
            for g in self.touch.get(r, []):
                if g >= self.nA and not crossed:
                    crossed = True
                    if r in self.cutreq: assert cur == self.cutreq[r], r
                f = F[g]
                if f != cur:
                    assert inside(cur, f); paid[len(f) - len(cur)] += 1; cur = f
            if not crossed and r in self.cutreq: assert cur == self.cutreq[r]
            if r in self.centre_regs: cur = self.cutreq[r]
            f = self.final[r]
            if f != cur: assert inside(cur, f); paid[len(f) - len(cur)] += 1
        # fixed centre descents
        w = self.w; lev = {int(t): basis(E) for t, E in w.get('target_levels', {}).items()}
        for r, F0 in zip(w['centers'], w['center_frames']):
            old = basis(F0)
            for E in sorted({lev.get(e[1] - self.v, ()) for e in w['cut'] if e[2] == r}, key=lambda E: -len(E)):
                if old != E: paid[len(old) - len(E)] += 1; old = E
        return dict(sorted(paid.items()))

    def window(self, g):
        """lower/upper frame bounds for gate g with all other gates fixed."""
        L = ZERO; U = FULL
        for r in self.events[g][2]:
            gs = self.touch[r]; k = self.pos[r, g]
            # previous frame of r
            if k == 0: prev = self.start[r]
            else:
                pg = gs[k - 1]; prev = self.F[pg]
                if pg < self.nA <= g and r in self.cutreq: prev = self.cutreq[r]
            if k == 0 and g >= self.nA and r in self.cutreq: prev = self.cutreq[r]
            L = join(L, prev)
            if k + 1 < len(gs):
                ng = gs[k + 1]; nxt = self.F[ng]
                if g < self.nA <= ng and r in self.cutreq: nxt = self.cutreq[r]
            else:
                nxt = self.cutreq[r] if (g < self.nA and r in self.cutreq) else self.final[r]
            U = meet(U, nxt)
        return L, U


def local_cost(W, g, f):
    old = W.F[g]; W.F[g] = f
    c = sum(W.reg_cost(r) for r in set(W.events[g][2]))
    W.F[g] = old
    return c


def candidates(W, g):
    L, U = W.window(g)
    if not inside(L, U): return []
    cs = {L, U}
    for r in W.events[g][2]:
        gs = W.touch[r]; k = W.pos[r, g]
        for kk in (k - 2, k - 1, k + 1, k + 2):
            if 0 <= kk < len(gs): cs.add(W.F[gs[kk]])
        cs.add(W.start[r]); cs.add(W.final[r])
    out = []
    for f in cs:
        if inside(L, f) and inside(f, U): out.append(f)
    return out


def descend(W, rng, T0=0.0, sweeps=10, log=print):
    gates = [g for g in range(len(W.events)) if g not in W.fixed and g not in W.forced]
    for sweep in range(sweeps):
        T = T0 * (1 - sweep / max(1, sweeps))
        rng.shuffle(gates); improved = 0; delta_tot = 0.0
        for g in gates:
            base = local_cost(W, g, W.F[g])
            best = None
            for f in candidates(W, g):
                if f == W.F[g]: continue
                c = local_cost(W, g, f)
                d = c - base
                if d < -1e-12 or (T > 0 and d < math.inf and rng.random() < math.exp(-d / T)):
                    if best is None or d < best[0]: best = (d, f)
            if best is not None:
                W.F[g] = best[1]; improved += 1; delta_tot += best[0]
        log(f'sweep {sweep} T={T:.3f} moves={improved} delta={delta_tot:.3f} total={total(W):.3f}')
        if improved == 0 and T == 0: break


def total(W):
    return sum(W.reg_cost(r) for r in range(W.n))


if __name__ == '__main__':
    wpath, framesjson, out, seed, T0, sweeps = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    w = json.loads(gzip.decompress(open(wpath, 'rb').read()))
    fr = json.load(open(framesjson)) if framesjson != '-' else None
    W = Word(w, fr and fr['A'], fr and fr['B'])
    print('start profile', W.profile(), 'cost', total(W))
    rng = random.Random(seed)
    if T0 > 0: descend(W, rng, T0, sweeps)
    descend(W, rng, 0, 50)
    p = W.profile(); print('end profile', p, 'cost', total(W), 'mass', sum(r * n for r, n in p.items()))
    json.dump({'A': [list(f) for f in W.F[:W.nA]], 'B': [list(f) for f in W.F[W.nA:]], 'profile': p}, open(out, 'w'))
