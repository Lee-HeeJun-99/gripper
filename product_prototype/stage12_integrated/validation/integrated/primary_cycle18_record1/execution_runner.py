import os,sys,resource,subprocess,time,json,hashlib,signal
from pathlib import Path
root=Path.cwd(); b=root/'product_prototype/stage12_integrated';out=b/'validation/integrated/primary_cycle18';out.mkdir(exist_ok=True);name=sys.argv[1];cmd=sys.argv[2:];assert not(b/'runtime/STOP').exists();assert not(out/(name+'_execution.json')).exists()
def ref(p):return dict(path=str(p.relative_to(root)),SHA256=hashlib.sha256(p.read_bytes()).hexdigest())
plan=dict(command=cmd,memory_limit_bytes=4294967296,timeout_s=420,source_hashes={p:ref(root/p)['SHA256'] for p in cmd if (root/p).is_file()});(out/(name+'_plan.json')).write_text(json.dumps(plan,indent=2)+'\n')
def limits():resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296));os.setsid()
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONPATH='/tmp/regrip_stage1_ocp:/tmp/regrip_stage2_fem:'+str(b/'scripts'))
t=time.monotonic();timed=False;stopped=False
with (out/(name+'.log')).open('w') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=limits)
 while p.poll() is None:
  if time.monotonic()-t>=420 or (b/'runtime/STOP').exists():
   timed=time.monotonic()-t>=420;stopped=not timed;os.killpg(p.pid,signal.SIGKILL);break
  time.sleep(.2)
 code=p.wait()
record=dict(command=cmd,exit_code=code,timeout=timed,STOP=stopped,elapsed_s=time.monotonic()-t,PID=p.pid,reaped=True,memory_limit_bytes=4294967296,timeout_s=420);(out/(name+'_execution.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
