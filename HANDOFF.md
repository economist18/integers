# Research handoff — integer-multiplication κ run (2026-10-11/12)

Detailed log: `research/EXPERIMENT-LOG.md`. Tools: `research/*.py`. H1 package: `h1/`.

## Pinned sources

| item | ref |
|---|---|
| upstream main | CrocSwap/integer-mult-bounds `12a4934d15006e8c10f9b2264f13f8f341be802b` (reviewed κ = 90446448750933/1.25e17 ≈ 7.2357e-4) |
| #496 pooled whole owners | `00cf70efd6a8637531deafef698157ca83e249ee` κ 1.332077359286333e-3 |
| #501 retimed pooled (eumemic) | `1dc056496fdbbc74073ed26d948a2dc235dbf356` κ 1.343518018117309e-3 |
| #505 async whole owners (Dugongue) | `4ee769c8e28837482272b5f4742497da8e2fc9d4` κ 1.357701757628940e-3 |
| #506 retimed + async (chafreaky) | `a4948bae…` κ 1.369588870945540e-3 |
| #507 partial-own kernel84 (eumemic) | see log |
| #508 coordinated gauge async (Dugongue) | `3213fc13…` κ 1.372554837726243e-3 |
| #473 partial-own async (rohanarun) | `c0df2ea3…` κ 1.388049083313897e-3; #512 (chafreaky) fresh certificate of the same κ |
| **#514 partial-own + collapse + 92 pivots + async (Dugongue)** | `246bfacd…` **κ 1.391523459591829e-3 — strongest undisputed claim at handoff** |
| **Newest (≈01:00 UTC Oct 12, not reproduced here)** | #527/#473 (rohanarun, 2080903b / c26b3cc7): κ 0.001467289440740487 (rank-sector factory + 112-port restriction); #523 (a900f98b): κ 0.001457945761723368 (punctured 112-port witness); #525: "exact fixed-word packing ceiling" |
| disputed split-residual line | #448/#480/#494/#499 (κ up to 1.4529e-3), single-stream register objection unresolved |

PR bodies were read from github.com pages (WebFetch). The GitHub API is not reachable for this
repository from this session (403; add_repo grants anonymous git reads only), so review threads were
read from the rendered pages, not the API.

## Environment

- Python 3.13 (system) for the stdlib packages (#505, #508).
- Python 3.14.6 venv `/home/user/venv314` (uv) with numpy 2.5.4, sympy 1.14.0, scipy 1.18.1.
- `libboost-dev` 1.83 via apt (`/usr/include`). 4 cores, 15 GB RAM.

## Verified results (this run)

- **#505 reproduced** (Linux/Py3.13). All 11 stages pass and κ/b/c match exactly. The template hash
  differs only because the publisher's Windows run wrote CRLF; this was diagnosed exactly.
  Workaround: PR head lacks `.gitattributes` listed in MANIFEST.
- **#501 does not reproduce as published** on Linux/Py3.14.6. The bit (PR493) and complex (PR484)
  suppliers and the guarded Lemma G stages pass, but the frozen map's source hash covers non-proof
  report floats that drift by platform. The publisher's float values were recovered
  (0.0011839865492062917, 18.471088665044633). With them, both pinned hashes reproduce exactly.
- **#508 and #514 reproduced** with their own verifiers: κ 0.001372554837726243 and 0.001391523459591829.
- **H1 = #505 async ⊕ #501 retiming, certified by a full clean run** (`h1/verify.py`, 42m53s, 4 negative controls rejected):
  κ = 68479443547277/5e16 = 0.001369588870945540, b = 0.001371467217183061206788.
  **This duplicates #506** (identical κ, opened ~minutes earlier), so it is an independent confirmation,
  not a new record. Package in `h1/`.

## Negative results (reproducible)

- **Exact frame retiming (H2/H4).** `research/retime_ilp.py` solves the frame-only retiming of a
  gk-type local word exactly. It uses HiGHS, global forward/backward frame windows, 38 independent
  components and a transportation linearization. The optimum equals:
  - PR501's profile for the PR484 word (also with the 531-gate prelude released);
  - #508's profile for its collapsed-gauge word.

  Frame-only retiming is exhausted for those words.
- **Idle repacking (H3).** Remainders 3/5/7 are forced by the 9-heavy width mix. #508 also reports that
  the stock-only relaxation equals its packing.
- **Single-gate and cascade annealing** cannot beat #501 (logs in `research/`).

## Next experiments

1. Exact ILP retiming is now done for #484/#501, #508, #507 and #514 words: all already optimal.
   Any new word (new kernel/gauge/factory) should be pushed through `research/exact-retiming-optimality/code/retime_ilp.py`
   before transferring old body frames — it costs seconds.
2. Port the ILP model to the 112-port words of #523/#527. `retime_model.Word` hardcodes v=120 and
   n=240+R; parametrise them from `len(w['ports'])`. Then check whether their retimings are optimal.
   This costs minutes once ported.
3. Gauge-selection search with exact retiming as the inner solver and width-aware packing cost.
   #508 found one coordinated 4-gauge collapse; its screens cover 382 single and 20 coordinated choices.
4. Settle the split-residual (multi-stream register) interface question. It is worth more than any
   local tweak.

## Deliverables

- `submission/0001-…patch`, `submission/PR-DESCRIPTION.md` and `submission/SUBMIT.md`: a negative-result
  PR (`research/exact-retiming-optimality/`) ready to apply on upstream `12a4934d`. Submit it through a
  fork, since none exists yet.
- Repository checks on that branch:
  - `make verify` fails only at the pre-existing `joint-dual-verify` Makefile pin, which fails
    identically on pristine main (fix in open #500);
  - `make gen4-bank-verify` passes;
  - `check.py` passes.
- `h1/`: independent reproduction package for #506's κ. It is not submitted, since it duplicates #506.

## Process notes

- The safety classifier blocked editing PR501's `apply_retime.py` to accept a portable hash, because
  that modifies another contributor's check. H1 instead uses its own applicator, which makes stricter
  per-entry checks and reproduces the publisher hashes.
- The PR505, PR508 and PR514 web uploads omit dotfiles. A manifest-entry workaround was used only for
  #505 and #508's old manifest format; #514 ran unmodified.

# ROUND 2 ("try again") — summary

## Best verified candidate: H3, κ = 795984451416673/5·10¹⁷ = 0.001591968902833346 (complex-bound) — DUPLICATED by #551 and #552 (same κ), optimality corroborated by #557

- **Construction.** Exact lifts-only frame retiming of #544's static44 complex word: 416 lifts,
  b = 1594507308884431019637/10²⁴. It is composed with #543's R420 bit word
  (c = 0.001653826988146799) through #543/#510's own `assemble9.py`.
- **Package.** `research/exact-retimed-static44/`, on an upstream branch built from main
  `db0e57bc` + #543 `2065fe4f` + #544 `4858bb38`. The patch is
  `submission/h3-patches/0003-…patch`, with `submission/PR-H3-DESCRIPTION.md` and
  `submission/SUBMIT-H3.md`.
- **Certification.** The final clean `verify.py` run passed in 900 s:
  - #544's and #543's full verifiers, unmodified;
  - the frozen lift application;
  - the full complex pipeline on the changed word;
  - two-engine pricing and the composition;
  - 4 negative controls rejected.

  Receipts are in `research/receipts/h3-final-*`.
- **Frontier at certification.** #547 (draft) 0.001590984155135328, #548 0.001590591090759927,
  #544 0.001588602246663212, main 0.001517760977820331. H3 is +0.0619% over #547 and +4.889% over
  main.
- **Conditional.** H3 inherits every supplier contract plus **#543's open phase-B interface
  question**. With an undisputed-interface bit supplier, the bound is bit-bound and this complex
  gain does not raise κ.

## Other round-2 results

- **H2 (#535 exact lifts + #541∘#542 bit with exact frames).** Verified, κ 0.001588602246663212.
  It **duplicates #544** (same bit delta), so it is not a record.
- **Exact ILP validation.** It reproduces #534's 40-seed SA optimum on #531's word exactly.
- **Bit words.** Fixed-order frame assignment is rigid: optimum = given on #541. The exact ILP beats
  #542's causal-minimum rule on the sliced #510 word (fee −0.0609 vs ≈ −0.045).
- **H4 (#548 register versions/allocation + exact lifts).** No b gain: #548's idle = #544's, and the
  syndrome step doesn't change the profile.

## Reproductions this round

All on Linux, with Python 3.14.6 unless noted:
- #541 PASS;
- #543 PASS;
- #544 PASS;
- #548 complex local/global PASS (Py3.14).

## Next experiments

1. **Exact lifts for any new complex word.** It takes about 1 min: `discovery/retime_ilp.py`
   with `LIFTS=1 FIXED_A=0`. Heuristic lift searches leave about +0.08% on the table.
2. **Bit side within the undisputed interface.** Trace refinements (preload/slice) plus exact
   frames. Fixed-order frames are exhausted, so gains need more trace moves.
3. **Settle #543's phase-B question.** If accepted, the complex side binds and complex
   improvements pay off directly.

## Final status (round 2)

H3 was certified, but **#551 (chafreaky) and #552 (Dugongue) published the identical κ first**, and
#557 certifies the same frame ceiling. So no strict record survives from this session. Every
improvement found (H1, H2, H3) was reached independently by other contributors within minutes to an
hour.

Durable contributions:
- the exact frame-retiming ILP for gk-type and bitE8 words, validated against #534's search result;
- independent reproductions of #505, #508, #514, #541, #543, #544 and #548;
- the diagnosed platform-float reproduction failures in #501 and #507;
- the negative results above.

**Repository checks on the H3 branch.**
- `make -k verify` passed every target apart from one stale-artifact failure in
  `positive-skip-build` (a leftover `build/` directory from round 1).
- That target passes when rerun on its own.
- The run also regenerates `certificates/mixed-point-audit.json`. Its old source hash is
  pre-existing drift on main, so I restored the file.
