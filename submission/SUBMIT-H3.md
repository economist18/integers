# Submitting the H3 PR (κ = 0.001591968902833346)

No fork of CrocSwap/integer-mult-bounds exists under your account, and this session has read-only
access upstream, so the PR could not be opened from here.

The package depends on two open PRs being present in the tree, which is the same structure PR547 uses:
- PR543 head `2065fe4f72a914d907f1046603f5a36f17018535` (eumemic, R420 bit), which fast-forwards from main;
- PR544 head `4858bb38da10cd8a1cd25ef85e7c14f4e2b529dd` (chafreaky, static44).

```sh
# fork CrocSwap/integer-mult-bounds on GitHub, then:
git clone https://github.com/<you>/integer-mult-bounds && cd integer-mult-bounds
git remote add upstream https://github.com/CrocSwap/integer-mult-bounds
git fetch upstream main 'refs/pull/543/head:pr543' 'refs/pull/544/head:pr544'
git checkout -b research/exact-retimed-static44 upstream/main      # main was db0e57bc at certification
git merge --no-edit pr543 && git merge --no-edit pr544
git am /path/to/h3-patches/0003-Conditional-kappa-0.001591968902833346-exactly-retim.patch
python3 -m pip install numpy sympy                                   # plus a C++17 compiler and libboost-dev
python3 -B research/exact-retimed-static44/verify.py --work /tmp/h3-$(date +%s) --boost-include /usr/include   # ~15 min
git push -u origin research/exact-retimed-static44
```

Open the PR against `CrocSwap:main` with `PR-H3-DESCRIPTION.md` as the body. Before posting:
1. Re-check the queue. If a higher undisputed κ has appeared, retitle this as an independent
   contribution: the exact lifts give a better complex supplier than any heuristic lift set.
2. Fill in the `make verify` result from HANDOFF.md.

If PR543 or PR544 change upstream, rebuild the branch on their new heads and rerun the verifier.
`apply_lifts.py` pins the static44 word, so any change to it fails loudly.
