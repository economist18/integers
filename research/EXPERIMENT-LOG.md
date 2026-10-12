# Experiment log — integer-mult-bounds research run (2026-10-11)

Upstream: https://github.com/CrocSwap/integer-mult-bounds, main `12a4934d15006e8c10f9b2264f13f8f341be802b`
(reviewed record κ = 90446448750933/125000000000000000 ≈ 7.23571590007464e-4, gen4 + #279).

## Frontier snapshot (PR heads fetched via `git fetch origin '+refs/pull/*/head:refs/remotes/pr/*'`)

PR bodies read via github.com web pages (API returns 403 to this session for an unattached repo).

| PR | head | claim | interface | notes |
|---|---|---|---|---|
| #499 | 0f3e55db | κ 1.452948511251494e-3 | split-residual cross-copy (#448) | disputed: single-stream register model (hipotures, conceded by higherbeing on #448) |
| #494 | 419907c7 | κ 1.435468764627892e-3 | split-residual | same dispute |
| **#505** | 4ee769c8 | κ 1.357701757628940e-3 | whole-owner | async replica scheduling on #496; complex binds b=1.359547617819233570818e-3; bit c (PR493) 1.565442e-3 |
| #501 | 1dc05649 | κ 1.343518018117309e-3 | whole-owner | frame retiming of #484 word under #496 placement |
| #502 | 4d30b832 | κ 1.343518018117309e-3 | whole-owner | same κ as #501 via #495→#484 frame transfer |
| #473 | 628b454d | 1.343523e-3 draft | whole-owner | verification pending |
| #496 | 00cf70ef | κ 1.332077359286333e-3 | whole-owner | parent of #501 and #505 |
| #503 | 3f271470 | bit c 1.5747e-3 | — | bit side; non-binding at current complex b |

Strongest undisputed comparable witness: **#505 @ 4ee769c8e28837482272b5f4742497da8e2fc9d4**.
Binding component is complex. Bit improvements (#503) do not help until b > c.

## R1 — reproduce #505

- First attempt: `python3.13 -B verify.py --work runs/r505-a` from PR head → **FAIL** at manifest check:
  `.gitattributes` listed in MANIFEST.json is absent from the PR head (web "Add files via upload" drops dotfiles).
  All other 63 manifest hashes match.
- Second attempt: copy package to `runs/pkg505`, drop only the `.gitattributes` manifest entry, rerun.

## H1 — compose #505 async scheduling with #501 frame retiming

Rationale: #505 consumes only helper residual widths, entrances and owner windows of the local word
(emit_async computes profile = Σ_calls local profile + idle remainders). #501 states the retiming fixes all
entrances and residual widths. Hence the async owner map should remain valid and only the local profile changes.

Numerical screen (`research/screen_h1.py`, exact PR361 moment engine, m=73, W=7680):
- idle remainders of #505 = {1:136, 3:3432, 5:3501, 7:2137, 16:1, 48:408}
- composed profile = idle + 72·L501 = {1:171856, 2:19008, 3:41592, 4:6048, 5:22941, 6:6624, 7:2209, 8:1224, 16:1, 48:408}; mass 558144, deficit 2496
- b(505) = 0.001359547617819233570818 (matches published), b(501) = 0.001345325487149526878087 (matches published)
- **b(H1) = 0.001371467217183061206788** (+0.877% over #505). Screen only; needs full rebuild + audits.

### R1 result (#505 reproduction) — PASS for mathematics, platform hash mismatch diagnosed
- Command: `cd runs/pkg505 && python3.13 -B verify.py --work runs/r505-a` (copy of PR head with only the `.gitattributes` manifest entry removed). 4m25s.
- All 11 stages exit 0: construct, scalar, emit-local, phases, adapters, parent-integration, parent-replay, emit-async, independent-async (19 controls rejected), invoice, two-moments-assembly (47 strict inequalities; next-grid/zero-eta/zero-beta/unit-beta rejected).
- κ = 67885087881447/50000000000000000, b = 679773808909616785409/5e23, c = 391360506745414227149/2.5e23 — all equal EXPECTED.json.
- Final check fails only on `template_sha256` (ours aa74187…, published 276b69e…). Cause: publisher ran on Windows; `Path.write_text` wrote CRLF. Our LOCAL-CHECKS.json and RESIDUAL-ADAPTERS.json hashed with LF→CRLF equal the published source_artifact hashes exactly. Every non-hash field of ASYNC-AUDIT, OWNERS-AND-PROFILE, PREFIX-AND-INVOICE, EXACT-ASSEMBLY, GLOBAL-PREFIX matches the published evidence.
- Conclusion: #505 is a reproducible witness on Linux/Python 3.13 up to platform byte encodings.

## R2 — reproduce #501 (needed as H1's retimed supplier)
- Command: `python3.14 -B research/r489-pooled-retimed-complex/verify.py runs/r501-a --boost-include /usr/include` (Python 3.14.6, Boost 1.83, g++), PR head 1dc05649.
- PASS: toolchain probes, complete493 (fresh PR493 bit operator, 211 s), independent493 local owners/invoice, complete484 (fresh PR442 parent + PR484 gauge80-kernel42, 1067 s), guarded Lemma G instances and end-to-end.
- **FAIL at rebuild-retimed/apply-frame-map**: `RETIME-FRAMES.json.gz` pins `source_word_json_sha256` over the full word JSON, which includes three report floats (`baseline_b`, `complex_coarse_float`, `gain_percent_float`). Their last digits differ by platform: Py3.14/Linux gives 0.0011839865492062921 / 18.471088665044675; Py3.13 (#505 pipeline) gives 0.001183986549206271 / 18.471088665042544.
- Diagnosis: ulp search recovered the publisher's values 0.0011839865492062917 / 18.471088665044633; with them our rebuilt word hashes to the pinned 52f89042… exactly and the retimed candidate to the pinned 06d204be… exactly. Both fresh rebuilds have identical float-excluded hash 3b5b4136… . Proof-relevant content is identical; only non-proof floats drift.
- Patching #501's apply_retime to compare a portable hash was **blocked by the session's safety classifier** (modifying another verifier's check). Not pursued. Instead H1 uses its own applicator (`h1/code/apply_frame_map.py`) with per-entry old-frame equality, unchanged payloads, recomputed profile via PR501's unmodified `profile()`, a portable pin, AND reproduction of both PR501 pinned hashes after restoring the publisher floats.

## H2 — further frame-only retiming of the PR484 word: NEGATIVE (exact)
- `research/retime_opt.py` model reproduces `apply_retime.profile` exactly on base and #501 words.
- Single-gate descent / annealing (seeds 1,2,3; T0 2–3, 60 sweeps): best 23269.306 (d·ln(73/d) proxy) = #501's endpoint; runs from the original word reach only 23291–23343.
- Cascade (push) moves (`retime_cascade.py`, seeds 7,8): no improvement over #501.
- **Exact ILP** (`retime_ilp.py`, HiGHS via SciPy 1.18.1, weight d·(73/d)^0.00137): global windows (forward-minimal / backward-maximal frames) make candidate sets complete; 2,480 free gates, 38 independent components (max 1,053 gates), all solved to optimality (gap 0) in <10 s each. Optimum local profile = {1:2385,2:264,3:530,4:84,5:270,6:92,7:1,8:17} = PR501's exactly.
- Releasing the 531 fixed prelude gates (FIXED_A=0): identical optimum.
- Conclusion: PR501's retiming is globally optimal for frame-only retiming of this word with fixed entrances, target levels and centre frames. Further local gains need a different word (payload/entrance/centre changes), not retiming.

## H1 result — VERIFIED but SUPERSEDED / DUPLICATE
- Feasibility certification (`h1/code/build_retimed.py` on fresh #484 output from R2, then unmodified #505 emit/audit/invoice/assemble with `h1/data/ASYNC-H1.json`): all stages exit 0.
  - retimed variant: apply (portable pin + publisher hashes reproduced), word/pipeline/hosting mutations, scalar, emit, phases, adapters, integrate, replay, Lemma G + 14 necessity controls.
  - async: profile {1:171856,2:19008,3:41592,4:6048,5:22941,6:6624,7:2209,8:1224,16:1,48:408}; prefix 205/512; row 16467<20161; local bits 20.
  - **κ = 68479443547277/50000000000000000 = 0.001369588870945540**; b = 342866804295765301697/2.5e23 = 0.001371467217183061206788; next b rejected; 47 strict inequalities; controls next_grid/zero_eta/zero_beta/unit_beta rejected. Binding: complex. +0.8755% over #505.
- Frontier recheck (git refs 22:5x UTC): **PR #506 (chafreaky, a4948bae) reports exactly the same κ and b** (#502 ⊕ #505), opened before this run completed. H1 is an independent duplicate; it independently confirms #506's number on Linux/Py3.14.
- Further superseded by #508 (Dugongue, 3213fc13): κ 0.001372554837726243 (coordinated 4-gauge collapse + retime + offset6 async) and draft #473 (rohanarun, 2857c976): κ 0.001388049083313897 (#507 partial-own factory + async; cached complex replay).

## H3 (idle repacking) — not pursued
Idle capacity per replica: 720×r8, 480×r16, 480×r32, 480×r48; demand per call 438×w9, 104×w8, 14×w7, 4×w5. 9-only packings of 16/32/48 force remainders 7/5/3; scarce 8/7/5 are the only fillers and #505's MILP is gap-0 for its order. Upside requires changing entrances (a new word).

## H4 — exact ILP retiming of the newer local words (#508 collapsed-gauge word, #473/#507 partial-own word)
Next.

## R3 — reproduce #508 (Dugongue, head 3213fc13): PASS
- `.gitattributes` again absent from the web-uploaded PR head (listed in MANIFEST.json); copy `runs/pkg508` with only that entry dropped (all other hashes enforced).
- `python3.13 -B verify.py --work runs/r508-a`: all 14 stages pass in 4m33s; κ = 0.001372554837726243 = EXPECTED. (No template-hash issue: #508 uses an LF-forcing launcher.)

## H4a — exact ILP retiming of #508's collapsed-gauge word: NEGATIVE
- Word: runs/r508-a/base/split-centres/FULL-WORD.json.gz (A 3267, B 840), local {1:2385,2:248,3:530,4:88,5:270,6:96,7:1,8:17}.
- ILP optimum (FIXED_A=531 and FIXED_A=0) = the same profile. #508's transferred PR495 schedule is already globally optimal for this word.

## R4 — #507 (eumemic, partial-own kernel84) reproduction: FAILS as published (same float-pin issue)
- `python3.14 -B research/r489-partial-own-kernel84/verify.py runs/r507-a --boost-include /usr/include`: complete493, independent493*, complete484, guarded Lemma G, construct-partial-own, selection-mutations, apply-kernel-selection, unretimed scalar/emit all PASS; apply-frame-map FAILS on the full-JSON source hash (report floats 0.0011839865492062444 / 18.471088665039904 on this platform).
- Research-only: map applied with per-entry old-frame checks reproduces the expected local profile {1:2493,2:224,3:516,4:84,5:298,6:64,7:1,8:17}.

## H4b — exact ILP retiming of #507's word: NEGATIVE
- FIXED_A=671 (its prelude) and FIXED_A=0: optimum = #507's profile.

## Exact-root confirmation
ILP weight d·(73/d)^b0 with b0 = each word's own exact moment root (0.001371467217183061 H1/#506; 0.001374441333828160 #508; 0.001389978441615608 #473-reported; 0.001365476727944168 #507 lockstep): optimum = published profile in all four. Since the moment LHS is increasing in b and linear in child counts, a strictly better frame-only retiming would lower LHS at b0; HiGHS (gap 0) finds none. Caveats: floating MILP tolerance; the 1e-16 bad-cover fallback term (≈2e-13 relative per child) is not in the objective.

## H5 — #508's coordinated 4-gauge collapse on #507's partial-own word: screened, not pursued
- gk_word.build with gauges 540–543 → [408,102] on #507's base + KERNEL-SELECTION: legal; targets 81,82,84,87 rank 4→2; widths {9:396,8:146,7:14,5:4} → {9:396,8:146,7:18}.
- Exact-retimed local profile {1:2493,2:208,3:516,4:88,5:298,6:68,7:1,8:17}: local mass +8/call (entrance rank moves into residuals); ILP objective 6810.43 vs 6802.42 (worse locally). Any gain must come from repacking the widened residuals, which needs a new async owner map on top of draft #473 (cached-replay verification only). #477's latest commit ("Archive partial-own async composition and unverified coordinated-gauge followup", rohanarun) indicates this exact composition is already in progress elsewhere — not duplicated.

## Frontier recheck (~00:10 UTC Oct 12)
- #514 (Dugongue, 246bfacd): κ 0.001391523459591829 — #507 partial-own factory + coordinated 4-gauge collapse + 92-pivot kernel + transferred body retiming + async order (7*stage+6*replica).
- #512 (chafreaky, 73d367fe): κ 0.001388049083313897 — fresh certificate of #473's partial-own async number.
- #473 (rohanarun, c0df2ea3): "Complete coordinated partial-own finite admission" — the H5 composition, done by its author.
- #510/#515: bit-word improvements (c), non-binding.

## H4c — exact ILP retiming of #514's word: NEGATIVE
- Word from #514's own verifier (unmodified run; an earlier attempt where I dropped a manifest entry broke #514's new manifest format and was discarded). A 3331 (prelude 651), B 840.
- Optimum (FIXED_A=651 and 0) = published {1:2539,2:160,3:530,4:88,5:298,6:68,7:1,8:17}. The transferred PR507 body frames are already optimal for the new word.
- Package `research/exact-retiming-optimality/` now covers 4 words.

## R5 — reproduce #514 (Dugongue, 246bfacd): PASS
- Unmodified `python3.13 -B verify.py --work runs/r514-a` (nice 5): all 13 stages pass, 5m04s; κ = 0.001391523459591829 = EXPECTED. (#514's new manifest format no longer requires .gitattributes in the upload.)

## H1 clean certification: PASS (independent confirmation of #506)
- `python3.14 -B h1/verify.py runs/h1-clean --boost-include /usr/include`; exit 0; 42m53s.
- Stages: toolchain ×3; complete493; independent493 local/invoice; complete484; rebuild-retimed (apply via portable pin + publisher-hash reproduction; word/pipeline/hosting mutations; scalar; emit; phases; adapters; integrate; replay; hosting; Lemma G + 14 mutants); independent-retimed-frames; retimed guarded lg_instances/lg_e2e; emit-async; independent-async (19 controls); invoice; two-moments-assembly.
- Negative controls rejected as required: unretimed-profile plan, corrupt frame map, mutated source word, owner outside window.
- κ = 68479443547277/50000000000000000 (0.001369588870945540); manifest 8bf65526…; EXACT-MATH 7ffe1693….

## Repository checks on branch research/exact-retiming-optimality (10a92009, base 12a4934d)
- `make verify` (PATH=venv314; 67m37s): EXIT 2 at `verify-joint` → `joint-dual-verify`: `AssertionError: Makefile` (research/joint-dual/SOURCE.json pins an old root Makefile hash). Reproduced identically on a pristine origin/main worktree → pre-existing; open #500 re-pins it. All earlier verify sub-targets passed.
- `make -k verify-joint verify-pair verify-tests`: only that same failure; audit_joint_candidate, verify-pair, isolated tests and frozen patch checks pass.
- `make gen4-bank-verify`: EXIT 0, 8m55s, κ 90446448750933/125000000000000000, 9 fresh stages, 9 omitted-stage controls rejected.
- `check.py` (4 cases + controls): PASS, 4m04s.

# ROUND 2 ("try again", 2026-10-12)

## Frontier at start of round 2
- main db0e57bc publishes reviewed κ 0.001517760977820331 (#531, direct-delivery 504 helpers, 112 ports).
- Open: #534 (rohanarun) 0.001526158885117467 (SA frame lifts on #531); #535 (icekylinx) 0.001584931111785787 (rank-4 post-centre kernels; complex b 0.001589991533606044; bit-bound with #510 c 0.001587447106092548); #541 (Dugongue) 0.001587212454640692 (preload60 bit, c 0.001589735702947999); #542 (rohanarun draft) slice+causal-min bit c 0.0015895030.

## Tool generalisation
- retime_opt.Word reads v = len(ports) (112-port words). retime_ilp.py: env LIFTS=1 (each frame must contain its given frame; PR534's interface), AMBIENT.
- Validation: model profile = repository profile for #531 and #535 words. **ILP (LIFTS) on #531's word returns exactly #534's 40-seed SA optimum {1:2220,2:368,3:460,4:168,5:168,6:56,7:8}** → #534 is optimal.

## H2c complex — exact lifts retiming of #535's word: +gain
- ILP optimum {1:2304,2:440,3:472,4:184,5:56,6:56,8:8} vs #535 {1:2208,2:728,3:184,4:280,5:56,6:56,8:8}; 416 gate frames lifted.
- Feasibility pipeline (unmodified #531/#535 scripts): audit_and_transport (exact scalar both orientations) PASS; phases_delta 832 fresh exact edges + 2095 reused PASS; emit_local, adapters_local (Lemma A), audit_local (both orientations, 11 controls) PASS; prepare_supplier_base, emit_supplier_hosted (plan profile restated = idle + 72·new local), audit_supplier_hosted, invoice_final PASS; assemble_combined: **b′ = 0.001591248091486981105925** (vs 0.001589991533606044).

## H2b bit — #541 preload60 ∘ #542 slice ∘ exact frames
- bit_model.py reproduces #541's chain profile; bit fixed-order frame ILP (bit_ilp.py) on #541's word: rigid (143 free gates), optimum = given.
- Naive #541∘#542 with #542's causal-minimum frames: c 0.0015879 (WORSE; causal-min undoes preloads).
- Slice only + exact ILP (catalogue + all root-closed subspaces in windows): profile {1:1270,2:1320,3:50,4:170,6:130,8:9}, 11 frames changed, no new frames. Control: same ILP on sliced #510 beats #542's causal-min (−0.0609 vs ≈−0.045 fee).
- Unmodified native C++ checks (legality, 960/1440 formal columns, 6+18 controls, interface, Gram, structural/mutable controls) PASS; global_k/adapt/parent audit/emit_k/hosted audit/assemble9 PASS (138240 whole residuals, 0 banks): **c′ = 0.001591129919227630331373**.
- Assembly (h2/code/assemble_h2.py, adapted from #541 assemble_meta): κ = 0.001588602246663212 (bit binds).
- **DUPLICATE**: #544 (chafreaky) reports exactly this κ and c (same bit delta 10(e1−e3−e4+e6)), with a better complex supplier (static44 b 0.001593245593667525). Not a record.

## Round-2 frontier update (~04:00 UTC)
- #543 (eumemic): 420-helper bit word c 0.001653826988146799 (nine-stage), κ complex-bound with #535.
- #545 (DreamingOfClouds, draft): punctured 111-port bit c 0.0016594720 (stacked hosting caveat).
- #546 (rohanarun draft): static44 + #542 bit κ 0.001587480974500277.
- With c ≥ 1.65e-3 the complex side binds; best complex supplier is #544's static44 (b 0.0015932456).

## H3 — exact lifts retiming of #544's static44 complex word + #543 bit (in progress)

## H3 — exact lifts on #544 static44 + #543 R420 bit: VERIFIED, highest claim at certification
- ILP (LIFTS=1, FIXED_A=0) on static44 word: 416 lifts; local {1:2300,2:440,3:472,4:184,5:56,6:56,8:8} (from {1:2204,2:728,3:184,4:280,...}); 34 components, gap 0.
- Feasibility: full #531/#544 complex pipeline (audit_and_transport, emit_local, audit_local 11 controls, adapters, phases_full every edge, prepare base, emit owners with restated plan, owner audit + mutation controls, invoice) PASS; b″ = 1594507308884431019637/10^24.
- #543 reproduced (verify.sh; nine-stage c 413456747036699736067/2.5e23; controls exact). #544 reproduced (κ 0.001588602246663212).
- Composition via #543/#510 assemble9.py (unmodified): κ = 795984451416673/5e17 = 0.001591968902833346 (complex-bound), 47/47, controls; in-run controls reproduce #543's κ (pr535 b) and #547's first κ (pr544 b) exactly.
- Package research/exact-retimed-static44 on branch main(db0e57bc)+#543+#544; final clean run `verify.py --work runs/h3-final`: EXIT 0, 900 s, 4 negative controls rejected, EXPECTED and manifest held.
- Frontier at certification: #547 (draft, rohanarun) 0.001590984155135328 (#548 complex + R420); #548 (Dugongue) 0.001590591090759927; #544 0.001588602246663212. H3 is +0.0619% over #547.
- Caveat: inherits #543's open phase-B interface question; with an undisputed-interface bit (c 0.0015911299) the bound is bit-bound and the complex gain does not raise κ.

## H4 — exact lifts with #548's register versions / owner allocation: NEGATIVE
- #548 local stages: static44 {1:2204,...} → lifted (PR534 port) {1:2284,2:456,3:488,4:168,...} → syndrome (same profile). Entropy fee: #548 lifted 19704.6/call vs exact 19690.8/call.
- ILP lifts from #548's syndrome frames: no improvement (heuristic lifts lock in a worse configuration).
- #548 idle remainders = #544's idle remainders; syndrome saves scalar ops only. Exact lifts + #548 idle gives the same b″ as H3. No b gain from composing.
