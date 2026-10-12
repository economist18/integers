# Negative result: frame-only retiming of the current whole-owner complex words is exactly exhausted (no κ claim)

## Summary

This PR adds `research/exact-retiming-optimality/`. It is an exact (MILP, gap 0) check that the
published frame retimings of the four current whole-owner complex words are **globally optimal**
among all frame-only retimings with the same fixed interface. That interface keeps the following
unchanged:

- scalar payloads and their order;
- helper entrances;
- target levels;
- centre frames;
- the compensation/kernel prelude.

| word | published retiming | prelude | exact optimum |
|---|---|---|---|
| PR484 gauge80-kernel42 | PR501 (= PR495/502 profile) | 531, and 0 | = published {1:2385, 2:264, 3:530, 4:84, 5:270, 6:92, 7:1, 8:17} |
| PR508 coordinated-gauge word | PR495 schedule as carried by PR508 | 531, and 0 | = published {1:2385, 2:248, 3:530, 4:88, 5:270, 6:96, 7:1, 8:17} |
| PR507 partial-own kernel84 word | PR507 | 671, and 0 | = published {1:2493, 2:224, 3:516, 4:84, 5:298, 6:64, 7:1, 8:17} |
| PR514 92-pivot coordinated word | PR507 body frames, transferred by PR514 | 651, and 0 | = published {1:2539, 2:160, 3:530, 4:88, 5:298, 6:68, 7:1, 8:17} |

**There is no κ change and no record claim.** The point is to save future search effort: further
complex-supplier gains must change the word or its interface (payloads, entrances, gauges, kernel,
factory), not its frames.

## Method

The method is described in the package README.

- **Feasible windows.** For every gate, minimal frames are propagated forward and maximal frames
  backward. Every feasible retiming lies inside these windows, so the candidate sets are complete.
- **Components.** Fixed gates split the problem into 38 independent components.
- **ILP.** Each component is solved as a 0/1 program in HiGHS. Register chains use a transportation
  linearisation.
- **Objective.** Σ d·(73/d)^b₀, where b₀ is the word's own exact moment root. A strictly better
  retiming would strictly lower this objective.
- **Controls.**
  - The model reproduces the repository climb rule.
  - Starting from the unretimed PR484 word gives the same optimum.
  - A non-nested frame is rejected.

```sh
python3 -m pip install numpy scipy
python3 -B research/exact-retiming-optimality/check.py /absolute/new/output
```

## Independent reproduction notes from the same run

All runs used Linux x86-64, Python 3.13.16 or 3.14.6, and Boost 1.83.

- **PR505 (4ee769c).** All 11 stages pass and κ/b/c equal EXPECTED.
  - The final `template_sha256` differs. The publisher's run wrote CRLF text: our LOCAL-CHECKS.json and
    RESIDUAL-ADAPTERS.json, rehashed with CRLF, give exactly the published hashes.
  - MANIFEST.json lists `.gitattributes`, which is missing from the uploaded head.
- **PR508 (3213fc1).** Full pass, κ 0.001372554837726243. The same `.gitattributes` omission applies.
- **PR501 (1dc0564) and PR507.** The published verifiers stop at `apply-frame-map` after every earlier
  stage passes.
  - The cause: the frozen map pins a full-JSON hash that includes three non-proof report floats with
    platform-dependent last digits.
  - The publisher's values are 0.0011839865492062917 and 18.471088665044633. Restoring them
    reproduces PR501's pinned source and candidate hashes exactly.
  - PR508's semantic hash, which excludes those floats, already avoids this.
- **PR506 (chafreaky).** Independently reproduced via a separate composition path, PR505's
  scheduler on the PR501-retimed word:
  - κ = 68479443547277/5·10¹⁶ = 0.001369588870945540;
  - b = 342866804295765301697/2.5·10²³.

  This matches PR506 exactly. That package is not included here, since it duplicates PR506.

## Checks run

All on branch head `10a92009`, from base main `12a4934d`, on Linux with Python 3.14.6 and the
pinned sympy 1.14.0.

- **`make verify`** (67m37s): every target passes except one. `verify-joint` → `joint-dual-verify`
  fails with `AssertionError: Makefile`.
  - **That failure predates this PR.** It fails identically on a pristine `origin/main` worktree,
    because `research/joint-dual/SOURCE.json` pins an older root Makefile hash. Open PR #500 re-pins it.
  - This PR does not touch the Makefile, README or any existing file.
  - Rerunning with `make -k verify-joint verify-pair verify-tests` gave the same single failure; the
    rest of `verify-joint`, `verify-pair` and `verify-tests` (isolated tests and `git apply --check`
    of the frozen patches) all pass.
- **`make gen4-bank-verify`**: PASS (8m55s). It reproduces the selected
  κ = 90446448750933/125000000000000000, with all 9 fresh stages and 9 negative controls.
- **`research/exact-retiming-optimality/check.py`**: PASS (4m04s). It covers the 4 cases,
  start-independence and the nesting control.

## Scope

- The certificate is a floating MILP at gap 0, not an exact rational dual certificate.
- The 10⁻¹⁶ fallback term is not in the objective.
- Optimality covers frame-only changes only.
- No inherited all-size, analytic or compiler contract is touched or proved.

## Credits and disclosure

- PR484: DreamingOfClouds.
- PR495: aliromman.
- PR501 and PR507: eumemic.
- PR502 and PR506: chafreaky.
- PR505, PR508 and PR514: Dugongue.
- PR493: eumemic.

Words and maps are theirs; this PR adds only the model, the solver and the checks. Prepared with
Anthropic Claude (Claude Code) assistance. Apache-2.0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01T7kRq1zRvpM2Z2yBuyfDWW
