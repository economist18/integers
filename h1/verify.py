"""Fresh, offline verification of the H1 composition: PR505 asynchronous whole-owner scheduling
applied to PR501's frame-retimed PR484 complex word, with the PR493 bit supplier.

Every stage below either runs an unmodified vendored script (byte-pinned to its PR head in
SOURCE.json) or one of this package's two small scripts (code/apply_frame_map.py,
code/build_retimed.py). Nothing is cached: both suppliers are reconstructed from their pinned inputs.

Usage: python3.14 -B verify.py /absolute/new/output --boost-include /usr/include [--cxx c++]
Requires Python 3.14 (PR501/PR493 pin it), NumPy, SymPy, a C++17 compiler and Boost headers.
"""
import argparse, concurrent.futures, copy, gzip, hashlib, json, os, shutil, subprocess, sys, threading, time
from pathlib import Path

if not __debug__: raise RuntimeError('assertions must remain enabled')
ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument('out', type=Path); ap.add_argument('--boost-include', type=Path, required=True); ap.add_argument('--cxx', default='c++')
a = ap.parse_args()
OUT = a.out.resolve(); assert not OUT.exists() and not OUT.is_relative_to(ROOT), 'choose a new output directory outside the package'
P501 = ROOT / 'vendor/pr501'; P505 = ROOT / 'vendor/pr505'
BIT = P501 / 'vendor/bit'; COMPLEX = P501 / 'vendor/complex/e8-complex-gauge-kernel'; C501 = P501 / 'code'
G505 = P505 / 'vendor/complex/e8-complex-gauge-kernel'; C505 = P505 / 'code'


def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(): return {str(p.relative_to(ROOT)): sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts}


def integrity():
    assert inventory() == read(ROOT / 'MANIFEST.json'), 'package manifest'
    for p, z in read(ROOT / 'SOURCE.json')['files'].items(): assert sha(ROOT / p) == z['sha256'], p


integrity(); OUT.mkdir(); start = time.monotonic(); steps = []; lock = threading.Lock()
env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', BOOST_INCLUDE=str(a.boost_include), CXX=a.cxx)
env.pop('PYTHONOPTIMIZE', None)


def record(name, rc, t, log, expect_fail=False):
    with lock:
        steps.append(dict(name=name, returncode=rc, expected_failure=expect_fail, seconds=round(time.monotonic() - t, 3), log_sha256=sha(log)))
        (OUT / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
    if expect_fail:
        assert rc != 0, ('negative control was ACCEPTED', name); print('REJECTED (as required)', name, flush=True)
    else:
        assert rc == 0, (name, log.read_text()[-6000:]); print('PASS', name, flush=True)


def run(name, args, cwd=None, extra=None, expect_fail=False):
    t = time.monotonic(); log = OUT / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f: r = subprocess.run(list(map(str, args)), cwd=cwd, env=env | dict(extra or {}), stdout=f, stderr=subprocess.STDOUT)
    record(name, r.returncode, t, log, expect_fail)


def py(name, p, *args, **kw): run(name, [sys.executable, '-B', p, *args], **kw)


def bit_worker():
    run('complete493', ['bash', BIT / 'verify.sh', OUT / 'bit'])
    py('independent493-local-owners', C501 / 'audit493/review_local.py', BIT, OUT / 'bit', OUT / 'BIT-LOCAL-OWNERS.json')
    py('independent493-invoice', C501 / 'audit493/review_invoice.py', BIT, OUT / 'bit', OUT / 'BIT-INVOICE.json')


def complex_worker():
    py('complete484', COMPLEX / 'verify.py', OUT / 'complex')


try:
    header = a.boost_include.resolve() / 'boost/multiprecision/cpp_int.hpp'
    assert header.is_file() and not (BIT / 'portable-include/boost').exists()
    probe = OUT / 'boost-probe.cpp'
    probe.write_text('#include <boost/multiprecision/cpp_int.hpp>\n#include <iostream>\nint main(){boost::multiprecision::cpp_int n=1; n<<=256; std::cout << n+1 << "\\n";}\n')
    run('compiler-version', [a.cxx, '--version'])
    run('boost-header-trace', [a.cxx, '-std=c++17', '-H', '-I' + str(BIT / 'portable-include'), '-I' + str(a.boost_include), str(probe), '-o', OUT / 'boost-probe'])
    run('boost-arbitrary-integer', [OUT / 'boost-probe'])
    assert int((OUT / 'boost-arbitrary-integer.log').read_text().strip()) == (1 << 256) + 1

    # 1. Both suppliers, fresh and in parallel (unmodified PR493 and PR484 verifiers as vendored by PR501).
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for f in [pool.submit(bit_worker), pool.submit(complex_worker)]: f.result()

    # 2. PR501's frozen frame-only retiming on the fresh PR484 word, then its complete rebuild and checks.
    base = OUT / 'complex/gauge80-kernel42'; R = OUT / 'retimed/gauge80-kernel42'
    py('rebuild-retimed', ROOT / 'code/build_retimed.py', COMPLEX, base, R)
    py('independent-retimed-frames', C501 / 'review_frames.py', '--baseline', base / 'split-centres', '--candidate', R / 'split-centres', '--out', OUT / 'RETIME-FRAME-REVIEW.json')
    g = OUT / 'retimed-guarded'; g.mkdir()
    for script in ['lg_instances.py', 'lg_e2e.py']:
        py('retimed-guarded-' + Path(script).stem, C501 / 'guarded_lemma.py', COMPLEX, script, 'gauge80-kernel42', cwd=g, extra={'LG_BASE': str(OUT / 'retimed')})

    # 3. PR505's asynchronous whole-owner schedule on the retimed word (unmodified PR505 code;
    #    the plan differs from PR505's ASYNC-3.json only in its stated expected profile).
    H = OUT / 'hosted'; A = OUT / 'audit'; A.mkdir()
    assert all(sha(R / 'work/pr361/code/engines' / f) == sha(base / 'work/pr361/code/engines' / f) for f in ('moment.py', 'base_two_moment.py', 'outer.py'))
    plan3 = read(P505 / 'inputs/ASYNC-3.json'); planH = read(ROOT / 'data/ASYNC-H1.json')
    assert {k: v for k, v in plan3.items() if k not in ('profile', 'status', 'numeric_saving')} == {k: v for k, v in planH.items() if k not in ('profile', 'status', 'numeric_saving')}
    py('emit-async', C505 / 'emit_async.py', G505, R, P505 / 'inputs/ASYNC-OWNERS.json.gz', ROOT / 'data/ASYNC-H1.json', H, cwd=R)
    py('independent-async', C505 / 'audit_async.py', R, H, A / 'ASYNC-AUDIT.json', cwd=R)
    py('invoice', C505 / 'audit_async_invoice.py', A, R, H, cwd=R)
    # bind the cited PR493 price to the fresh replay before using it
    cited = read(P505 / 'inputs/PR493-EXPECTED.json')['eleven']; fresh = read(OUT / 'bit/RESULT.json')
    assert fresh['bit_lower'] == cited['bit_lower'] and fresh['emitted_program_sha256'] == cited['emitted_program_sha256']
    assert {int(k): v for k, v in fresh['bit_profile'].items()} == {int(k): v for k, v in cited['profile'].items()}
    assert all(fresh['bit'][k] == cited['bit'][k] for k in ('charged_three_level_coefficient_bits', 'row_coefficient', 'charged_prefix_bits'))
    py('two-moments-assembly', C505 / 'assemble.py', A, R, H, P505 / 'inputs/PR493-EXPECTED.json', cwd=R)

    # 4. Negative controls specific to the composition.
    neg = OUT / 'negative'; neg.mkdir()
    # (a) PR505's own plan (unretimed expected profile) must not validate against the retimed word.
    py('neg-unretimed-profile-plan', C505 / 'emit_async.py', G505, R, P505 / 'inputs/ASYNC-OWNERS.json.gz', P505 / 'inputs/ASYNC-3.json', neg / 'hosted-a', cwd=R, expect_fail=True)
    # (b) a corrupted frame map (one recorded old frame changed) must be rejected.
    m = read(P501 / 'data/RETIME-FRAMES.json.gz'); m['A'][0][1] = [1]
    (neg / 'BAD-MAP.json.gz').write_bytes(gzip.compress(json.dumps(m).encode(), mtime=0))
    py('neg-corrupt-frame-map', ROOT / 'code/apply_frame_map.py', base / 'split-centres/FULL-WORD.json.gz', neg / 'BAD-MAP.json.gz', ROOT / 'data/RETIME-PIN.json', neg / 'b.json.gz', expect_fail=True)
    # (c) a source word with one scalar payload changed must fail the portable pin.
    w = read(base / 'split-centres/FULL-WORD.json.gz'); w['B'][0][3] = -w['B'][0][3]
    (neg / 'BAD-WORD.json.gz').write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    py('neg-mutated-source-word', ROOT / 'code/apply_frame_map.py', neg / 'BAD-WORD.json.gz', P501 / 'data/RETIME-FRAMES.json.gz', ROOT / 'data/RETIME-PIN.json', neg / 'c.json.gz', expect_fail=True)
    # (d) owner map with one helper moved outside its owner window must fail emission.
    roles = read(P505 / 'inputs/ASYNC-OWNERS.json.gz'); bad = copy.deepcopy(roles); bad[0]['time'] = (bad[0]['time'] + 36) % 72
    (neg / 'BAD-OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(bad).encode(), mtime=0))
    py('neg-owner-outside-window', C505 / 'emit_async.py', G505, R, neg / 'BAD-OWNERS.json.gz', ROOT / 'data/ASYNC-H1.json', neg / 'hosted-d', cwd=R, expect_fail=True)

    r = read(A / 'EXACT-ASSEMBLY.json'); own = read(A / 'OWNERS-AND-PROFILE.json'); inv = read(A / 'PREFIX-AND-INVOICE.json')
    math = dict(kappa=r['kappa'], kappa_decimal=r['kappa_decimal'], complex_lower=r['complex_lower'], next_b_rejected=r['next_b_rejected'],
                bit_lower=r['bit_lower'], binding_component=r['binding_component'], outer_controls=r['outer_controls'],
                strict_outer_constraints=r['strict_outer_constraints'], bootstrap=r['bootstrap'], complex_profile=own['paid_profile'],
                complex_live=own['live'], complex_physical=own['physical'], global_prefix_bits=inv['global_prefix_bits'],
                charged_prefix_bits=inv['charged_prefix_bits'], complex_finite=inv['finite'], retimed_local_profile=read(R / 'split-centres/LOCAL-CHECKS.json')['forward']['paid_profile'])
    (OUT / 'EXACT-MATH.json').write_text(json.dumps(math, indent=2) + '\n')
    for k, v in read(ROOT / 'EXPECTED.json').items(): assert math[k] == v, (k, math.get(k), v)
    integrity()
    receipt = dict(status='PASS_H1_ASYNC_RETIMED_WHOLE_OWNER_COMPOSITION', kappa=r['kappa'], kappa_decimal=r['kappa_decimal'], python=sys.version.split()[0],
                   manifest_sha256=sha(ROOT / 'MANIFEST.json'), exact_math_sha256=sha(OUT / 'EXACT-MATH.json'), steps=steps, seconds=round(time.monotonic() - start, 3),
                   scope='Conditional finite witness. Both suppliers rebuilt fresh; retimed word fully recompiled and audited; asynchronous owner map, controller, invoice and 47 strict outer inequalities checked. Inherited all-size compiler, mutable-basis/common-label, PR484 Lemma A realization, restored-row, precision/tape and analytic-transfer contracts remain assumptions.')
    (OUT / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'steps'}, indent=2))
except BaseException as e:
    (OUT / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e)[:4000], steps=steps), indent=2) + '\n'); raise
