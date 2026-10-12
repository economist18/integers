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
2. Gauge-selection search with exact retiming as the inner solver and width-aware packing cost.
   #508 found one coordinated 4-gauge collapse; its screens cover 382 single and 20 coordinated choices.
3. Settle the split-residual (multi-stream register) interface question. It is worth more than any
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
