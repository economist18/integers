"""Offline, stdlib-only reconstruction of the asynchronous complex derivative.
The unchanged PR493 bit operator is a cited dependency, not freshly verified here.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys,time,gzip
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
P=Path(__file__).resolve().parent
a=argparse.ArgumentParser();a.add_argument('--work',type=Path,required=True);args=a.parse_args()
W=args.work.resolve();assert not W.exists(),'Choose a new output directory; existing outputs are preserved.'
mf=P/'MANIFEST.json'
if mf.exists():
 for n,h in json.loads(mf.read_text()).items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
W.mkdir(parents=True);V=W/'base';V.mkdir();(V/'split-centres').mkdir();shutil.copytree(P/'inputs/work',V/'work')
shutil.copy2(P/'inputs/BASE-WORD.json.gz',V/'BASE-WORD.json.gz')
bit=json.loads((P/'inputs/PR493-EXPECTED.json').read_text())['eleven']
(V/'BIT-PRICE.json').write_text(json.dumps({'lower':bit['bit_lower'],'scope':'PR493 cited published supplier'}))
C=P/'vendor/complex';G=C/'e8-complex-gauge-kernel';A=W/'audit';A.mkdir();H=W/'hosted'
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TEMP=str(W),TMP=str(W))
steps=[]
def run(name,script,*argv):
 start=time.monotonic();print('RUN',name,flush=True)
 with (W/(name+'.log')).open('w',encoding='utf-8') as log:
  result=subprocess.run([sys.executable,'-B',str(script),*map(str,argv)],cwd=V,env=env,stdout=log,stderr=subprocess.STDOUT)
 steps.append({'stage':name,'exit':result.returncode,'seconds':time.monotonic()-start})
 (W/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 if result.returncode:
  print((W/(name+'.log')).read_text()[-5000:]);raise SystemExit(result.returncode)
 print('PASS',name,flush=True)
run('construct',G/'code/gk_word.py',V/'BASE-WORD.json.gz',G/'data/selections/gauge80-kernel42.json',V/'split-centres/FULL-WORD.json.gz')
run('scalar',G/'code/audit_gk.py')
run('emit-local',G/'code/emit_gk.py')
run('phases',C/'split-centres-global/code/complex_phases_full.py')
run('adapters',G/'code/adapters_gk.py',V/'split-centres/CANONICAL-WORD.json.gz',V/'split-centres/RESIDUAL-ADAPTERS.json',V/'LEMMA-A.json')
run('parent-integration',G/'code/integrate_gk.py')
run('parent-replay',G/'code/replay_gk.py')
run('emit-async',P/'code/emit_async.py',G,V,P/'inputs/ASYNC-OWNERS.json.gz',P/'inputs/ASYNC-3.json',H)
run('independent-async',P/'code/audit_async.py',V,H,A/'ASYNC-AUDIT.json')
run('invoice',P/'code/audit_async_invoice.py',A,V,H)
run('two-moments-assembly',P/'code/assemble.py',A,V,H,P/'inputs/PR493-EXPECTED.json')
x=json.loads((A/'EXACT-ASSEMBLY.json').read_text());audit=json.loads((A/'ASYNC-AUDIT.json').read_text())
assert all(z['exit']==0 for z in steps)
result={'status':'PASS_CONDITIONAL_ASYNCHRONOUS_COMPLEX_DERIVATIVE','kappa':x['kappa'],'kappa_decimal':x['kappa_decimal'],'complex_lower':x['complex_lower'],'bit_lower':x['bit_lower'],'template_sha256':x['complex_template_sha256'],'strict_constraints':len(x['strict_outer_constraints']),'scope':'New complex program independently replayed. The unchanged PR493 bit operator and inherited all-size compiler, common-label, Lemma A realization, restored-row, precision/tape and analytic-transfer contracts remain dependencies. No unconditional multiplication bound or fresh Lean certification is claimed.','stages':steps,'package_manifest_sha256':hashlib.sha256(mf.read_bytes()).hexdigest() if mf.exists() else None}
expected=P/'EXPECTED.json'
if expected.exists():
 e=json.loads(expected.read_text())
 for key in ['kappa','complex_lower','bit_lower','template_sha256']:assert result[key]==e[key],key
(W/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],'kappa',result['kappa_decimal'],flush=True)
