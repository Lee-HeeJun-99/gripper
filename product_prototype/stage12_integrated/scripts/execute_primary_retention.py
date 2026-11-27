"""One bounded analysis child with immutable execution evidence; no Git writes."""
import sys,os,time,subprocess,resource,signal
from baseline_registry import ROOT,REPO,ref,dump
name=sys.argv[1];command=sys.argv[2:];out=ROOT/'validation/integrated/primary_cycle10';out.mkdir(exist_ok=True)
assert not(ROOT/'runtime/STOP').exists();assert not(out/(name+'_plan.json')).exists()
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296));os.setsid()
env=os.environ.copy();env.update(PYTHONPATH='/tmp/regrip_stage1_ocp:/tmp/regrip_stage2_fem',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
dump(out/(name+'_plan.json'),dict(command=command,memory_limit_bytes=4294967296,timeout_s=420,source_hashes={p:ref(REPO/p)['SHA256'] for p in command if p.endswith('.py') and (REPO/p).is_file()}))
start=time.monotonic();timed=False;stop=False
with (out/(name+'.log')).open('w') as log:
 p=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,env=env,preexec_fn=limits())
 while p.poll() is None:
  timed=time.monotonic()-start>420;stop=(ROOT/'runtime/STOP').exists()
  if timed or stop:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   break
  time.sleep(.1)
 code=p.wait()
r=dict(command=command,exit_code=code,timeout=timed,STOP=stop,elapsed_s=time.monotonic()-start,PID=p.pid,reaped=True,memory_limit_bytes=4294967296,timeout_s=420);dump(out/(name+'_execution.json'),r);print(r)
