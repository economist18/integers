"""Rebuild PR501's frame-only retimed PR484 variant from a freshly verified PR484 output.

Same step sequence, scripts and arguments as PR501's code/rebuild_retimed.py; the only difference is
the first step, which uses this package's apply_frame_map.py (per-entry old-frame checks plus a
portable source pin, see that file) instead of PR501's apply_retime.py. Every later step runs the
unmodified vendored PR484 / PR501 scripts.
Usage: build_retimed.py PR484_SOURCE VERIFIED_PR484_VARIANT OUT_VARIANT
"""
import hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path

if not __debug__: raise RuntimeError('assertions must remain enabled')
ROOT = Path(__file__).resolve().parent.parent
S, B, O = map(lambda x: Path(x).resolve(), sys.argv[1:4])
assert not O.exists(); O.mkdir(parents=True)
C = S / 'code'; P501 = ROOT / 'vendor/pr501'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
steps = []


def run(name, script, *args, cwd=None):
    log = O / (name + '.log'); t = time.monotonic()
    with log.open('w') as f:
        p = subprocess.run([sys.executable, '-B', str(script), *map(str, args)], cwd=cwd or O, env=env, stdout=f, stderr=subprocess.STDOUT)
    steps.append(dict(name=name, exit_code=p.returncode, seconds=round(time.monotonic() - t, 3), log_sha256=sha(log)))
    (O / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
    assert p.returncode == 0, (name, log.read_text()[-4000:])
    print('PASS', name, flush=True)


shutil.copytree(B / 'work', O / 'work')
shutil.copytree(B / 'sc_base', O / 'sc_base')
shutil.copy2(B / 'BIT-PRICE.json', O / 'BIT-PRICE.json')
sc = O / 'split-centres'; sc.mkdir()
run('apply-frame-map', ROOT / 'code/apply_frame_map.py', B / 'split-centres/FULL-WORD.json.gz', P501 / 'data/RETIME-FRAMES.json.gz', ROOT / 'data/RETIME-PIN.json', sc / 'FULL-WORD.json.gz')
run('word-mutations', C / 'controls_gk.py', sc / 'FULL-WORD.json.gz', O / 'CONTROLS-WORD.json')
run('pipeline-mutations', C / 'controls_pipeline.py', O, S / 'data/selections/gauge80-kernel42.json', O / 'CONTROLS-PIPELINE.json')
run('scalar-frame', C / 'audit_gk.py')
run('emit-both-orientations', C / 'emit_gk.py')
run('exact-gaussian-phases', S.parent / 'split-centres-global/code/complex_phases_full.py')
run('residual-adapters', C / 'adapters_gk.py', sc / 'CANONICAL-WORD.json.gz', sc / 'RESIDUAL-ADAPTERS.json', O / 'LEMMA-A.json')
run('integrate-global', C / 'integrate_gk.py')
run('independent-program-replay', C / 'replay_gk.py')
run('baseline-hosting', C / 'hosted_gk.py', sc, O / 'hosted', '--one-helper-per-family', '--selection', S / 'data/SELECTION.json', '--key', 'complex-gauge80-kernel42')
run('baseline-hosting-audit', C / 'audit_hosted_gk.py', sc, O / 'hosted', O / 'HOSTING-AUDIT.json', '--one-helper-per-family')
run('hosting-mutations', C / 'controls_hosting.py', O, S / 'data/SELECTION.json', 'complex-gauge80-kernel42', O / 'CONTROLS-HOSTING.json')
run('lemma-G-identities', C / 'lemmaG/check.py', O.parent, O.name, O / 'lemmaG')
run('retimed-lemma-G-mutants', P501 / 'code/retimed_lemma_mutants.py', S, O.parent, cwd=O / 'lemmaG')
receipt = dict(status='PASS_FRESH_FROZEN_RETIMED_COMPLEX_WORD', source_full_word_sha256=sha(B / 'split-centres/FULL-WORD.json.gz'),
               frame_map_sha256=sha(P501 / 'data/RETIME-FRAMES.json.gz'), retimed_full_word_sha256=sha(sc / 'FULL-WORD.json.gz'), steps=steps,
               artifacts={str(p.relative_to(O)): sha(p) for p in [sc / 'FULL-WORD.json.gz', sc / 'CANONICAL-WORD.json.gz', sc / 'LOCAL-PROGRAMS.json.gz', sc / 'LOCAL-CHECKS.json', sc / 'INTEGRATION.json', O / 'LEMMA-A.json', O / 'HOSTING-AUDIT.json', O / 'lemmaG/LEMMA-G-CHECK.json', O / 'lemmaG/MUTANTS.json', O / 'lemmaG/MUTANT-ADAPTER-RECEIPT.json']})
(O / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], flush=True)
