# Asynchronous whole-owner replicas

Conditional kappa = **0.001357701757628940**, or `67885087881447/50000000000000000`,
from complex saving b = `679773808909616785409/500000000000000000000000` and the unchanged PR493 bit
saving c = `391360506745414227149/250000000000000000000000`. This is **1.923642% above PR496**
under the same whole-owner supplier assumptions.

The new mechanism removes replica lockstep. Eight replicas retain their own
nine-stage order, but run in an order sorted by `(stage + 3*replica/7, stage, replica)`.
Each complete cover invocation is indivisible. This exposes additional legal
pending-child intervals on other replicas, including 4,539 uses of the same
pair number on a different physical replica. No helper is split between owners.
The frozen map names all 40,320 whole helper uses. No optimizer runs in verification.

## What changes

The gauge80-kernel42 local word, both scalar orientations, Gaussian phases,
wrappers and data routes are unchanged. Only the order of complete replica
blocks, whole-helper placement, and exact idle remainders change. The source
controller has 30 replica-local events and two final global events. Every
replica's projection is exactly those 30 events in order; the two final events
run once. New `replica` fields restrict bridges, idle completion, and terminal
events to the named replica. Old decoders that ignore those fields are invalid
for this new template version.

The paid profile is:

```
rank      1      2     3      4      5    6     7     8  16  48
count 148240  66816  7032  19728  26109  144  2209  1224   1 408
```

Ambient dimension 73, live families 7680, physical families 8258, rank mass 558144,
and deficit 2496 are unchanged. There are 3,194 actual orthogonal73-column maps,
9,615 explicit remainder children, and 33,114 cross-replica helper uses.
The maximum child rises to48, still satisfying `73^2 > 2*48^2`.

The old192-bit prefix allowance is replaced. Count 72 full local sweeps and 72
individual bridge sweeps: `20+37+72+72+4=205` bits suffice;512 are charged.
The two-level row invoice charges an additional `2*512` and remains16467<20161.
Both exact rational moment engines agree on the adjacent10^-24 endpoints.
Six bootstrap steps and all 47 strict outer inequalities pass on the 10^-18
kappa grid; the next grid point and three degenerate-parameter controls fail.

## Reproduce offline

Python3.11 or later, standard library only. No C++ compiler, optimizer, network,
Lean, shell extension, or external package is needed. From this directory:

```
python -B verify.py --work /absolute/path/to/a-new-output-directory
```

On Windows use an available drive path for `--work`. The output directory must
not already exist; prior outputs are preserved. POSIX users may run
`bash verify.sh`; its temporary output directory is printed through the result.
The verifier reconstructs the required parent local word and phase data, emits
the new asynchronous program, independently checks its literal chronology and
charts, recounts the scalar/prefix invoice, and performs exact composition.
It rejects19 corrupt controller variants. See RESULT.json in the work directory.
No external absolute data paths occur in the verifier.

The unchanged bit operator is reused from the pinned PR493 publication. Its
published profile is independently repriced here, but its C++ operator replay
is deliberately not rerun. That distinction is explicit in every result.

## Scope and comparison

This is a conditional finite witness under the inherited all-size compiler,
mutable-basis/common-label, PR484 Lemma A realization, restored-row,
precision/tape and analytic-transfer contracts. Finite replay does not prove
those contracts, and this is not a new unconditional multiplication theorem.
The positive mathematical statement is the sufficient endpoint-preserving
asynchronous construction in PROOF.md, with independently checked hypotheses.

PR conversations were downloaded through 497, then the public snapshot was
frozen for packaging. PR496 is the comparable whole-owner frontier. PR494's
larger0.001435468764627892 computation was explicitly under review because its
split-residual operator interface was disputed; that interface is not used.
This package does not claim to surpass that number or reach0.0014.
No submission, fork change, or publication is performed by this package.
