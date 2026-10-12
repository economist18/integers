# How to submit the negative-result PR

This session could not open the PR itself. No fork of `CrocSwap/integer-mult-bounds` exists under your
account, and this session has only anonymous read access to that repository.

1. Fork https://github.com/CrocSwap/integer-mult-bounds on GitHub.
2. Run:

   ```sh
   git clone https://github.com/<you>/integer-mult-bounds && cd integer-mult-bounds
   git checkout -b research/exact-retiming-optimality 12a4934d15006e8c10f9b2264f13f8f341be802b
   git am /path/to/0001-Exact-ILP-check-published-frame-retimings-of-four-wh.patch
   python3 -m pip install -r research/exact-retiming-optimality/requirements.txt
   python3 -B research/exact-retiming-optimality/check.py /tmp/ilp-check-$(date +%s)   # ~4 min
   git push -u origin research/exact-retiming-optimality
   ```

3. Open a PR against `CrocSwap:main`, using `PR-DESCRIPTION.md` as the body. Before posting, fill in
   the `make verify` / `make gen4-bank-verify` results from `HANDOFF.md`.
4. Re-check the queue first. If newer words have appeared, run them through
   `code/retime_ilp.py` too and add a case.

Do not describe this as a κ improvement: it is a negative result, plus reproduction notes.
