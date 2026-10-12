"""Rebuild one checked local candidate from a pinned pre-gauge base and selection.
python rebuild_candidate.py GK_CODE_DIR LANE_DATA CANDIDATE OUTPUT_WORD
CANDIDATE is COMPONENT, JOINT-47 or JOINT-51. Uses retained Apache-2.0 upstream
code with original attribution. Physical hosting and pricing are separate.
"""
import sys,json,gzip,hashlib
from pathlib import Path
code,data,name,out=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4])
assert not out.exists();r=json.loads((data/'REBUILD.json').read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f,h in r['gk_sources'].items():assert sha(code/f)==h,(f,'source hash')
assert sha(data/'BASE-WORD.json.gz')==r['base_sha256'];c=r['candidates'][name];assert sha(data/c['selection'])==c['selection_sha256']
sys.dont_write_bytecode=True;sys.path.insert(0,str(code.resolve()));import gk_word as g
word=g.build(json.loads(gzip.decompress((data/'BASE-WORD.json.gz').read_bytes())),json.loads((data/c['selection']).read_bytes()));raw=g.dump(word);assert hashlib.sha256(raw).hexdigest()==c['word_sha256'];out.write_bytes(raw);print('PASS_SOURCE_BOUND_RECONSTRUCTION',name,c['word_sha256'])
