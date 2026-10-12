# Asynchronous whole-owner scheduling of the frame-retimed gauge/kernel word

This package composes two independent derivatives of PR496's pooled whole-owner complex supplier:

- **PR501** (eumemic; the same profile is also reached by chafreaky's PR502): a frozen,
  frame-only retiming of PR484's gauge80-kernel42 local word. It changes 411 A and 504 B gate frames.
  All 4,107 scalar payloads and their order, the first 531 A gates, every helper entrance, the target
  levels, the centre frames, the cut and the cleanup stay fixed.
- **PR505** (Dugongue): removing replica lockstep. Complete local invocations run in the order sorted by
  `(stage + 3*replica/7, stage, replica)`, with an explicit whole-owner map of all 40,320 helper
  residuals into pending idle children on the owner replica's timeline.

The bit supplier is PR493's R489 word (eumemic), which does not bind.

## Why the two changes compose

PR505's owner map, its windows and its correctness argument (`vendor/pr505/SCHEDULING-LEMMA.md`)
use only the following properties of the local word:

1. Each complete invocation is an arbitrary-dirt-valid shear on its two active data banks.
2. Each helper `h` has one residual, of width `9 - rank(entrance_h)`, on its assigned pending block.
   The width histogram is {9:438, 8:104, 7:14, 5:4}.
3. Every complete invocation restores borrowed spectators and private work. It uses 800 distinct
   physical owners.
4. The 120 port bases and pending idle axes of `DATA-PHASES.json` (`idle_children[i].orthogonal_axes`)
   determine the helper charts.

PR501's retiming changes none of the scalar payloads, the entrances, the ports or the idle-child
structure. So (2) and (4) are literally unchanged. PR501 re-establishes (1) and (3) for the retimed word
from scratch:

- the exact all-800-column scalar audit and both orientations (`audit_gk.py`);
- freshly rebuilt Gaussian phase recipes (`complex_phases_full.py`) and residual adapters (Lemma A);
- the independent program replay;
- Lemma G label, instance and end-to-end identities, including the 14 necessity controls;
- the independent frame reviewer.

The verifier reruns all of these. PR505's emitter and its independent controller audit then read the
retimed word's actual `CANONICAL-WORD`, `LOCAL-CHECKS`, `DATA-PHASES` and parent `GLOBAL-TEMPLATE`.
They recheck widths, windows, charts, disjoint footprints and complete idle remainders against those
files, so this argument is not taken on trust. PR505's scheduling lemma then applies verbatim, because
it is stated for any admitted complete-invocation supplier with properties (1)–(4).

The paid profile is additive. It is the sum over the 72 calls of the local word's paid profile, plus
the explicit idle remainders. The remainders depend only on the owner map and the idle-child ranks:

```
idle remainders (PR505, unchanged)  {1:136, 3:3432, 5:3501, 7:2137, 16:1, 48:408}
72 x PR501 retimed local profile    {1:171720, 2:19008, 3:38160, 4:6048, 5:19440, 6:6624, 7:72, 8:1224}
composed paid profile               {1:171856, 2:19008, 3:41592, 4:6048, 5:22941, 6:6624, 7:2209, 8:1224, 16:1, 48:408}
```

The rank mass is 558,144 and the deficit is 73·7680 − 558144 = 2496. Both are unchanged, and the
largest child is still 48 (73² = 5329 > 2·48² = 4608). PR505's emitter recomputes this profile from the
retimed `LOCAL-CHECKS.json` and the owner map. `data/ASYNC-H1.json` differs from PR505's `ASYNC-3.json`
only in the expected profile and status text. The verifier asserts this field by field. Using PR505's
original plan against the retimed word is a mandatory negative control and must be rejected.

## Prefix and finite invoice

The prefix and finite-invoice audit (`audit_async_invoice.py`) is rerun on the retimed programs. It
checks the following:

- the local scalar/Horner envelope of the retimed word is again 20 bits;
- the async global prefix is 20 + 37 + 72 + 72 + 4 = 205 bits, with 512 bits charged;
- the two-level row coefficient is below 20161;
- the physical stock, router, literal and precision inequalities hold.

These are recomputed from the actual retimed local programs, not copied.

## Result

The two exact rational moment engines are run with the inherited bad-cover fallback. Six bootstrap
levels and the 47 strict outer inequalities are checked. The next 10⁻¹⁸ grid point and the zero-η,
zero-β and unit-β degenerate controls are rejected. See `EXPECTED.json` for the exact values.

## Retained conditions

The result is conditional on the inherited all-size compiler and mutable-basis/common-label
interfaces, PR484's Lemma A realization, and the restored-row, precision/tape and analytic-transfer
contracts. This package proves none of these. It is a finite construction with exact checks. It is
not an unconditional multiplication theorem and not a Lean proof. The κ is an exponent saving, not a
runtime measurement.

## What this package does not use

It does not use the split-residual cross-copy interface of PR448/480/494/499. That interface is
currently disputed, so this package makes no comparison with those numbers.
