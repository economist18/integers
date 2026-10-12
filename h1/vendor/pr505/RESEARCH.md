# Research appendix: corpus reuse, the achieved mechanism, and preserved candidates

The delivered conditional bound is **kappa = 0.001357701757628940**. Its new contribution is asynchronous scheduling of complete replica invocations. The local gauge/kernel word is unchanged from PR484/496; the stronger bit supplier comes from PR493. The package's final receipts, physical audit and exact assembly are the evidence for the numerical claim. The inherited complete-invocation, compiler and analytic contracts remain explicit conditions; this is not a new Lean certification of integer multiplication.

## The mechanism that improved the bound

Earlier packing advanced all eight replicas in lockstep. The new schedule preserves each replica's nine-stage controller order while allowing replicas to occupy different stages. A helper may then use an idle block whenever its entire invocation lies between consecutive touches on the **owner's** timeline. The selected order sorts calls by `(stage + 3*replica/7, stage, replica)`.

Correctness uses completed invocation endpoints. Each invocation restores arbitrary dirty workspace and borrowed spectators, and leaves only its specified residual on its assigned pending block. Different residual blocks of an idle child are disjoint; their product with the paid remainder is the original child. Completing that product before the owner's next touch preserves each replica's original controller. No scalar gate is commuted through an unfinished invocation, and no residual is split between owners.

A flow nomination is converted to literal owners using bipartite edge coloring. There are 72 calls and 40,320 helper occurrences, with 560 distinct helper families per call. Ambient dimension 73, live stock7680 and deficit 2496 stay fixed. The changed paid profile is:

    1:148240, 2:66816, 3:7032, 4:19728, 5:26109,
    6:144, 7:2209, 8:1224, 16:1, 48:408.

The complete schedule needs its own physical chart checks and prefix invoice. Its gain does not follow from the floating packing objective alone.

## What was actually reused from the OpenAI corpus

The inspected snapshot is `adc7f1241b42e322a6451854ab7e4b4c146bf78a` of [openai/math](https://github.com/openai/math). `APPENDIX-SOURCES.json` records repository-relative source paths and hashes. Direct source inspection and Git consistency checks are distinct from compiling these modules in this round; no claim is made that every paper in the collection is formalized.

- [FourierCircuit/WordScheduling.lean](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/OAI/Computability/FourierCircuit/WordScheduling.lean): `scheduledStep_product` and `scheduledLayer_product` preserve products under order-preserving schedules on fixed disjoint supports. `Word.matrix_substitute` and `Word.weight_substitute` preserve semantics and account for substituted calls. These supplied the structural template for scheduling complete normalized invocations. The new owner-relative interval argument is stated and checked separately; the fixed-support theorem is not silently applied to aliased unfinished programs.
- [MatroidCounting/CommonBases.lean](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/lean/OAI/Combinatorics/MatroidCounting/CommonBases.lean): `greedyOracle_correct`, `greedyOracle_rank`, and the parallel/nonparallel pair-rank lemmas motivated response-matroid basis and circuit-component selection. The common-integer-polymatroid preprint, problem114, also suggested moving capacity across fixed stage partitions. The actual packing family is not asserted to be a matroid, and no counting FPRAS is used as a packing certificate.
- `FourierCircuit/TensorTools.lean`, `RowCompression.sparse_row_compression`, and `SparseShear.lean`, `cancellation_identity`, provide explicit row-basis changes and cancellation of a shared exterior block. Independent dirty replica coordinates cannot be deleted merely by compressing a displayed response matrix. No additional gain was obtained from this route.
- `FourierCircuit/PivotJoin.lean`, `PivotJoin.of_join`, and `MonomialFeedback.lean`, `Dense2x2.price`, suggested alternative local compositions. The latter's abstract normalized price bound is not a literal bounded-coefficient routine in this model. The exact-Fourier documentation also limits its theorem to a subsequence; it does not supply the missing all-length bit-complexity implementation.
- `Topology/ArtinGroups/Cancellation/BlockPivot.lean`, `homotopy_square`, `homotopy_retract`, `remainder_retained`, and `NumberTheory/TwoPoint/Walks/ColumnRankRelations.lean`, `columnDifference_disjoint_minor`, were inspected for simultaneous elimination and donor/pivot separation. They did not produce another priced gain in this round.

## Three checked local constructions, not added to the achieved gain

For a common entrance frame, choose a basis of a response-matroid component as donors. Each remaining column is an exact rational donor combination. Prepending its cancelling donor shears makes that pivot's dirty response zero; reverse cleanup restores the helper state. All required frame nesting and source spans must still hold.

The following concrete words passed exact rational reconstruction, all 800 arbitrary-dirt columns in both forward and inverse-transpose orientations, and every individual pivot-correction omission control:

| Candidate | Local profile change from PR484/496 | Residual counts (width:count) | Omission controls |
|---|---|---|---:|
| COMPONENT | -10 rank 1, -14 rank 2, +14 rank 3 | 5:4, 7:14, 8:100, 9:442 | 38 |
| JOINT-47 | -14 rank 1, -2 rank 2, -4 rank 3, +4 rank 4, +4 rank 5 | 5:4, 7:12, 8:102, 9:442 | 48 |
| JOINT-51 | -14 rank 1, -4 rank 2, +8 rank 3, -2 rank 4, +2 rank 5 | 5:4, 7:14, 8:100, 9:442 | 40 |

These improve selected local objectives but lose scarce narrow residual inventory. Their tested lockstep allocations, including stage-selective portfolios and paid banks, did not improve the full bound. None is counted in the delivered kappa. They remain useful sufficient constructions for future schedules.

The companion base, three selections and `REBUILD.json` permit source-bound reconstruction through `rebuild_candidate.py`; `audit_component_scalar.py` checks each reconstructed word independently. `LOCAL-CANDIDATE-AUDITS.json` preserves the three exact scalar receipts. The constructor reuses the retained, hash-pinned `gk_word.py` and `gk_common.py` with their attribution.

## Other bounded lessons

All14,851 subspaces contained in first-touch frames were screened. Under the fixed80 gauge exclusions, only 14 classes had positive response nullity, all dimension 1. Allowing excluded gauge helpers exposed63 additional components, still dimension 1. A catalogue of 646 components from deletion minors up to depth two did not beat the inherited42-pivot width budget. These are finite-search results, not global impossibility theorems.

The proposed gauged-donor ordering is algebraically sufficient when original dirt compensation precedes the kernel update. Adding individual donors while retaining the current palette failed exact target/centre nesting in all 86 tested cases; geometric admissibility alone was insufficient. Whole-palette replacements remain a separate route.

Native frame-retiming searches on the full joint gauge word and its cleanup extension found no better profile. A direct lift of PR493's bit skeleton to the complex side also failed a specific structural test: all 14,400 port pairs obey complemented adjacency. An even-parity-frame repair and the identity `G Hadamard G + A_orth - J = 3 I` are constructive leads, but require extra paid copies and a different decoder; they are not achieved improvements.

The productive change was therefore at the scheduling level: reuse the already checked local engine, remove replica lockstep, and reconstruct the complete physical ownership and prefix bill.


Portable companion files are under `research-notes/kernel/`. From the package root, rebuild a local candidate with:

```
python -B research-notes/kernel/rebuild_candidate.py vendor/complex/e8-complex-gauge-kernel/code research-notes/kernel JOINT-47 /new/output-word.json.gz
python -B research-notes/kernel/audit_component_scalar.py /new/output-word.json.gz research-notes/kernel/JOINT-47-SELECTION.json /new/scalar-receipt.json
```

These separate local identities are not added to the achieved kappa.
