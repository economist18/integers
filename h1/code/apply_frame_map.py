"""Apply PR501's frozen frame-only retiming map to a freshly rebuilt PR484 word.

Usage: apply_frame_map.py BASE_FULL-WORD.json.gz RETIME-FRAMES.json.gz PIN.json OUT_FULL-WORD.json.gz

PR501's frozen map (data/RETIME-FRAMES.json.gz, byte-identical to PR501) pins the source word by a
hash over its whole JSON, including three report floats (baseline_b, complex_coarse_float,
gain_percent_float) that are discovery diagnostics, not proof inputs, and whose last digits differ
across platforms and Python versions. PIN.json records the hash of the word with exactly those three
keys removed, and the publisher's float values; with those values restored, PR501's original pinned
source and candidate hashes are reproduced (see PIN.json, which this script re-derives and checks).

The checks are per entry: every map entry's recorded old frame must equal the rebuilt word's frame,
no index repeats, all scalar payloads and order are unchanged, the first 531 A gates are unchanged,
and the nested-frame local profile is recomputed with PR501's own unmodified profile() function and
must equal the map's expected local profile. Only frames change; the report's local/global profiles
are rewritten as PR501's apply step does.
"""
import copy, gzip, hashlib, importlib.util, json, sys
from collections import Counter
from pathlib import Path

if not __debug__: raise RuntimeError('assertions must remain enabled')
HERE = Path(__file__).resolve().parent


def canonical(x): return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def main(src, mapfile, pinfile, out):
    assert not out.exists()
    spec = importlib.util.spec_from_file_location('pr501_apply_retime', HERE.parent / 'vendor/pr501/code/apply_retime.py')
    AR = importlib.util.module_from_spec(spec); spec.loader.exec_module(AR)
    w = json.loads(gzip.decompress(src.read_bytes()))
    p = json.loads(gzip.decompress(mapfile.read_bytes()))
    pin = json.loads(pinfile.read_text())
    keys = pin['excluded_report_keys']
    assert sorted(keys) == ['baseline_b', 'complex_coarse_float', 'gain_percent_float']
    assert all(type(w['report'][k]) is float for k in keys)

    def portable(x):
        y = copy.deepcopy(x)
        for k in keys: y['report'].pop(k)
        return hashlib.sha256(canonical(y)).hexdigest()

    assert portable(w) == pin['source_portable_sha256'], 'rebuilt PR484 word differs in a proof-relevant field'
    # The publisher's own pinned hash is reproduced by restoring the publisher's float values.
    pub = copy.deepcopy(w); pub['report'].update(pin['publisher_report_floats'])
    assert hashlib.sha256(canonical(pub)).hexdigest() == p['source_word_json_sha256'] == pin['pinned_source_word_json_sha256']

    z = copy.deepcopy(w)
    for part in ('A', 'B'):
        seen = set()
        for i, old, new in p[part]:
            assert i not in seen and z[part][i][-1] == old, (part, i)
            seen.add(i); z[part][i][-1] = new
        assert [e[:-1] for e in w[part]] == [e[:-1] for e in z[part]]
    assert w['A'][:531] == z['A'][:531]
    for k in w:
        if k not in ('A', 'B', 'report'): assert w[k] == z[k], k
    local = AR.profile(z)
    assert local == {int(r): k for r, k in p['expected_local_profile'].items()}
    oldlocal = {int(r): k for r, k in w['report']['local_profile'].items()}
    g = Counter({int(r): k for r, k in w['report']['global_profile'].items()})
    for r in set(local) | set(oldlocal): g[r] += 72 * (local.get(r, 0) - oldlocal.get(r, 0))
    assert all(k >= 0 for k in g.values())
    g = {r: k for r, k in sorted(g.items()) if k}
    assert g == {int(r): k for r, k in p['expected_global_profile'].items()}
    z['report']['local_profile'] = {str(r): k for r, k in local.items()}
    z['report']['global_profile'] = {str(r): k for r, k in g.items()}
    assert portable(z) == pin['candidate_portable_sha256']
    zp = copy.deepcopy(z); zp['report'].update(pin['publisher_report_floats'])
    assert hashlib.sha256(canonical(zp)).hexdigest() == p['candidate_word_json_sha256'] == pin['pinned_candidate_word_json_sha256']
    out.write_bytes(gzip.compress(canonical(z), mtime=0))
    print(json.dumps(dict(status='PASS_FROZEN_FRAME_ONLY_RETIME_APPLICATION_PORTABLE_PIN', changed_A_frames=len(p['A']),
                          changed_B_frames=len(p['B']), local_profile=local,
                          publisher_hashes_reproduced=True, output_json_sha256=hashlib.sha256(canonical(z)).hexdigest()), indent=2))


if __name__ == '__main__': main(*map(Path, sys.argv[1:5]))
