"""Frame model of a bitE8 word (format bitE8/1+mut), mirroring build_preload60.replay.

Sections run D, A, snapshot of retained totals, scatter (no climbs), B, C, final climbs.
A gate [f, t, sources] climbs every touched register to catalogue frame f; a strict increase
pays a child of rank dim(f) - dim(cur).  Frames are spans of rational lines in Q^8.
"""
import json, gzip, sys
from fractions import Fraction as Q
from collections import Counter, defaultdict


def rbasis(vecs):
    B = {}
    for rr in vecs:
        row = list(map(Q, rr))
        for c in sorted(B):
            q = row[c]
            if q: row = [a - q * b for a, b in zip(row, B[c])]
        c = next((i for i, x in enumerate(row) if x), None)
        if c is not None:
            q = row[c]; row = [x / q for x in row]
            for k in list(B):
                p = B[k][c]
                if p: B[k] = [a - p * b for a, b in zip(B[k], row)]
            B[c] = row
    return tuple(tuple(B[c]) for c in sorted(B))  # reduced row echelon form, canonical


class BitWord:
    SECTIONS = ('D', 'A', 'B', 'C')

    def __init__(self, w):
        self.w = w; self.V = w['v']; self.N = len(w['start'])
        self.FB = [rbasis([w['lines'][i] for i in f]) for f in w['frames']]
        self.dim = [len(b) for b in self.FB]
        # canonical subspace -> list of catalogue indices (duplicates possible)
        self.canon = {}
        for i, b in enumerate(self.FB): self.canon.setdefault(b, i)
        self._sub = {}
        self.events = []  # (section, idx, regs)
        for sec in self.SECTIONS:
            for i, (f, t, ss) in enumerate(w[sec]): self.events.append((sec, i, [t, *ss]))
        self.F = [w[sec][i][0] for sec, i, _ in self.events]
        self.nDA = len(w['D']) + len(w['A'])  # snapshot point
        self.touch = defaultdict(list)
        for g, (_, _, regs) in enumerate(self.events):
            for r in regs: self.touch[r].append(g)
        self.pos = {(r, g): k for r, gs in self.touch.items() for k, g in enumerate(gs)}

    def sub(self, a, b):
        k = (a, b)
        if k not in self._sub:
            self._sub[k] = self.dim[a] <= self.dim[b] and len(rbasis(list(self.FB[a]) + list(self.FB[b]))) == self.dim[b]
        return self._sub[k]

    def chains(self, F=None):
        F = F or self.F; w = self.w; H = Counter(); cur = list(w['start']); tops = None
        for g, (sec, i, regs) in enumerate(self.events):
            if g == self.nDA: tops = [cur[q] for q in w['ret']]
            f = F[g]
            for r in regs:
                a = cur[r]; assert self.sub(a, f), (g, r, a, f)
                if self.dim[f] > self.dim[a]: H[self.dim[f] - self.dim[a]] += 1
                cur[r] = f
        for r, f in enumerate(w['final']):
            a = cur[r]; assert self.sub(a, f), ('final', r, a, f)
            if self.dim[f] > self.dim[a]: H[self.dim[f] - self.dim[a]] += 1
            cur[r] = f
        return dict(sorted(H.items())), tops


if __name__ == '__main__':
    w = json.loads(gzip.decompress(open(sys.argv[1], 'rb').read()))
    B = BitWord(w); H, tops = B.chains()
    print('chain profile', H, 'tops', Counter(B.dim[t] for t in tops))
    print('distinct catalogue subspaces', len(B.canon), 'of', len(B.FB))
