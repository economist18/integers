"""Compose PR541's preload60 bit word with PR542's zero-target-response slice, then assign
frames by PR542's causal-minimum rule.  Discovery script: exact F2 endpoint and exact rational
root-closed frames; physical admission is separate.
Usage: compose_bit.py PRELOAD60_WORD.json.gz OUT_DIR
"""
import json, gzip, sys, copy, hashlib
from fractions import Fraction as Q
from collections import Counter
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=False)
w = json.loads(gzip.decompress(src.read_bytes())); v = w['v']; n = 2 * v + w['R']; full = 1
lines = w['lines']


def scalar(word):
    z = [1 << r for r in range(n)]
    for sec in ['D', 'A', 'B', 'C']:
        if sec == 'B':
            held = [z[r] for r in word['ret']]
            for j, cs in enumerate(word['scatter']):
                for c in cs: z[v + j] ^= held[c]
        for f, d, ss in word[sec]:
            for s in ss: z[d] ^= z[s]
    assert all(z[r] == ((1 << r) | (1 << (r - v)) if v <= r < 2 * v else 1 << r) for r in range(n))


def rref(vs):
    b = {}
    for row in vs:
        x = list(map(Q, row))
        for p, y in sorted(b.items()):
            if x[p]: a = x[p]; x = [s - a * t for s, t in zip(x, y)]
        if any(x):
            p = next(j for j, a in enumerate(x) if a); a = x[p]; x = [q / a for q in x]
            for q, y in list(b.items()):
                if y[p]: a = y[p]; b[q] = [s - a * t for s, t in zip(y, x)]
            b[p] = x
    return b


def contains(b, row):
    x = list(map(Q, row))
    for p, y in sorted(b.items()):
        if x[p]: a = x[p]; x = [s - a * t for s, t in zip(x, y)]
    return not any(x)


scalar(w)
# 1. PR542's simultaneous zero-target-response slice (same backward F2 response rule).
resp = [0] * n
for j in range(v): resp[v + j] = 1 << j
for f, d, ss in reversed(w['B']):
    for q in ss: resp[q] ^= resp[d]
for j, cs in enumerate(w['scatter']):
    for c in cs: resp[w['ret'][c]] ^= resp[v + j]
dead = []
for i in reversed(range(len(w['A']))):
    f, d, ss = w['A'][i]
    if resp[d] == 0: dead.append(i)
    for q in ss: resp[q] ^= resp[d]
deadset = set(dead); removed = [w['A'][i] for i in sorted(dead)]
w['A'] = [g for i, g in enumerate(w['A']) if i not in deadset]
w['C'] = [[full, d, list(ss)] for f, d, ss in reversed(w['A'])]
scalar(w)
# 2. causal-minimum frames (PR542 rule), new root-closed frames appended to the catalogue.
bs = [rref([lines[i] for i in f]) for f in w['frames']]; dim = [len(b) for b in bs]; masks = []
for f, b in zip(w['frames'], bs):
    closed = {i for i, x in enumerate(lines) if contains(b, x)}; assert set(f) == closed; masks.append(sum(1 << i for i in closed))
idx = {m: f for f, m in enumerate(masks)}
def join(mask):
    basis = rref([lines[i] for i in range(len(lines)) if mask >> i & 1])
    closed = sum(1 << i for i, x in enumerate(lines) if contains(basis, x))
    if closed not in idx: idx[closed] = len(masks); masks.append(closed); dim.append(len(basis))
    return idx[closed]
le = lambda a, b: masks[a] & masks[b] == masks[a]
cur = list(w['start']); moves = 0
import os
EXTRA = os.environ.get('NOCAUSAL')
for sec in ['D', 'A', 'B', 'C']:
    for g in w[sec]:
        f, d, ss = g
        if sec in ('A', 'B') and not __import__('os').environ.get('NOCAUSAL'):
            m = 0
            for r in [d] + ss: m |= masks[cur[r]]
            nf = join(m); assert le(nf, f)
            if nf != f: g[0] = nf; moves += 1
            f = g[0]
        for r in [d] + ss: assert le(cur[r], f); cur[r] = f
for r, f in enumerate(w['final']): assert le(cur[r], f)
w['frames'] = [[i for i in range(len(lines)) if m >> i & 1] for m in masks]
scalar(w)
raw = json.dumps(w, sort_keys=True, separators=(',', ':')).encode()
(out / 'WORD.json.gz').write_bytes(gzip.compress(raw, mtime=0))
rec = dict(source_sha256=hashlib.sha256(json.dumps(json.loads(gzip.decompress(src.read_bytes())), sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
           removed_A=len(dead), removed_gates=removed, causal_moves=moves, frames=len(masks), word_json_sha256=hashlib.sha256(raw).hexdigest())
(out / 'COMPOSE.json').write_text(json.dumps(rec, indent=1) + '\n')
print(json.dumps({k: v for k, v in rec.items() if k != 'removed_gates'}))
