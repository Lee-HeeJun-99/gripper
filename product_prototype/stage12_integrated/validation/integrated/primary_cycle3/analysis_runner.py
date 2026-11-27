import os,resource,subprocess,time,json,hashlib,sys
from pathlib import Path
b=Path.cwd()/'product_prototype/stage12_integrated';out=b/'validation/integrated/primary_cycle3';name=sys.argv[1];cmd=sys.argv[2:]
assert not(b/'runtime/STOP').exists()
def limits():resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296));os.setsid()
t=time.monotonic();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONPATH='/tmp/regrip_stage1_ocp:/tmp/regrip_stage2_fem')
with (out/(name+'.log')).open('w') as log:
 p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,preexec_fn=limits)
 try:code=p.wait(timeout=420);timeout=False
 except subprocess.TimeoutExpired:
  import signal
  os.killpg(p.pid,signal.SIGKILL);code=p.wait();timeout=True
record=dict(command=cmd,exit_code=code,timeout=timeout,elapsed_s=time.monotonic()-t,PID=p.pid,reaped=True,memory_limit_bytes=4294967296,timeout_s=420)
(out/(name+'_execution.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
