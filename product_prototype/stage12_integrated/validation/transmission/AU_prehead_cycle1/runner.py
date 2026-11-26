import subprocess,resource,os,json,time,hashlib
from pathlib import Path
r=Path('product_prototype/stage12_integrated');out=r/'validation/transmission/AU_prehead_cycle1'
def ref(p):return dict(path=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
steps=[('access',r/'scripts/preheaded_idler_access.py',[]),('release',r/'scripts/integrated_release_gate.py',['--tag','AU_prehead_release1'])]
(out/'preexecution.json').write_text(json.dumps(dict(sources=[ref(s) for _,s,_ in steps],parent=ref(r/'cad/exports/revAO_root2/summary.json')),indent=2)+'\n')
def limit():resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
env=dict(os.environ,PYTHONPATH='/tmp/regrip_stage1_ocp:'+str(r/'scripts'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
records=[]
for name,s,args in steps:
 if (r/'runtime/STOP').exists():raise RuntimeError('STOP')
 t=time.monotonic()
 with (out/(name+'.log')).open('w') as f:
  try:p=subprocess.run(['python3',str(s),*args],stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=limit,timeout=420);code=p.returncode
  except subprocess.TimeoutExpired:code=124
 records.append(dict(name=name,exit_code=code,elapsed_seconds=time.monotonic()-t,actually_executed=True,limit_seconds=420,virtual_memory_KiB=4194304,threads=1,log=ref(out/(name+'.log')),producer=ref(s)))
 (out/'execution.json').write_text(json.dumps(records,indent=2)+'\n')
 if name=='access' and code not in (0,2):break
print(json.dumps(records,indent=2))
