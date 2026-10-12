# Conditional κ = 0.001591968902833346: exactly retimed static44 complex supplier with the R420 bit

## Summary

This adds `research/exact-retimed-static44/`. It solves the frame-lift problem of PR544's static44
complex word **exactly**, then composes the result with PR543's R420 bit supplier.

- **Exact lifts.** A per-component 0/1 program finds the optimum over all monotone frame lifts
  (PR534's interface). It lifts 416 gate frames, and the complex supplier rises to
  b = 1594507308884431019637/10²⁴.
- **Bit side.** The R420 bit supplier (c = 0.001653826988146799) is slack, so the complex side binds.
- **Result.** κ = 795984451416673/(5·10¹⁷) = **0.001591968902833346**.

| reference (at this PR's snapshot) | κ | this PR |
|---|---|---|
| main (PR531, reviewed) | 0.001517760977820331 | +4.889% |
| PR544 | 0.001588602246663212 | +0.2113% |
| PR548 | 0.001590591090759927 | +0.0866% |
| PR547 (current, PR548 complex + R420) | 0.001590984155135328 | +0.0619% |
| same composition without retiming (static44 + R420) | 0.001590711200057236 | +0.0791% |

These are exponent savings, not runtime measurements.

## Method

The exact lift solver, the validation against PR534, and the composition argument are in the
package README.

The ILP reproduces PR534's 40-seed optimum on PR531's word exactly, which validates it. On static44
it finds a strictly better configuration: the local profile moves from
{1:2204, 2:728, 3:184, 4:280, 5:56, 6:56, 8:8} to {1:2300, 2:440, 3:472, 4:184, 5:56, 6:56, 8:8}
at unchanged rank mass. Helper entrances and widths are unchanged, so PR544's literal owner map is
reused. The plan differs only in its stated profile, which the verifier asserts.

## Verification

`python3 -B research/exact-retimed-static44/verify.py --work DIR --boost-include /usr/include`
takes about 15 minutes. All of the following run unmodified unless noted.

1. **PR544's full verifier.** This runs both of its suppliers and reproduces κ 0.001588602246663212.
2. **PR543's full verifier.** This gives R420 c = 413456747036699736067/2.5·10²³.
3. **Frozen lift application** (this package). It checks that each map entry is current and that
   each new frame is a strict lift. It also checks nesting through the cut, centres, levels and
   finals, and that the profile and rank mass are as expected.
4. **The complex pipeline on the changed word:**
   - PR531 exact scalar/frame transport over 728 columns in both orientations;
   - local emission and the independent local replay, with 11 controls;
   - Lemma A wrappers;
   - PR544's every-edge phase lowering;
   - data binding and whole-owner emission;
   - the independent owner audit with its mutation controls;
   - a fresh finite invoice (row 16467 < 20161, prefix 225 < 512, halving 5329 > 4608).
5. **Two exact moment engines** for b, with the next grid point rejected.
6. **Composition** through PR543/PR510's own `assemble9.py`:
   - 47/47 strict inequalities, and the next-grid, zero-η, zero-β and unit-β controls rejected;
   - in-run controls reproduce PR543's κ (PR535 b) and PR547's first κ (PR544 b) exactly.
7. **Negative controls**, all rejected: a reversed lift, a stale map entry, a non-nested frame, and
   PR544's own plan applied to the retimed word.

The final clean run passed. Its receipt is described in `HANDOFF.md`.

## Caveats

- Every inherited supplier contract stays conditional: all-size compiler, common-label/mutable
  basis, Lemma A realization, restored rows, precision/tape and analytic transfer.
- **PR543's open interface question is inherited.** It concerns its phase-B source rewrites after
  target reads, under PR425's lemma. With a bit supplier inside the undisputed interface, the bound
  is bit-bound and this complex gain does not raise κ.
- The optimum holds for frame lifts under the stated fixed interface only.
- This is not a formal proof of the asymptotic theorem, and not a runtime result.

## Credits

- Dugongue (PR541 static44 presentation)
- chafreaky (PR544 admission and owner map)
- eumemic (PR543 R420)
- icekylinx (PR531/535 word and pipeline)
- rohanarun (PR534 lift interface; PR547 first composition)
- DreamingOfClouds (PR484 Lemma A/G, PR510 nine-stage pipeline)
- all inherited notices

Prepared with Anthropic Claude (Claude Code) assistance. Apache-2.0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01T7kRq1zRvpM2Z2yBuyfDWW
