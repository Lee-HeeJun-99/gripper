"""Bounded single analysis execution with preserved log and exact source plan."""
import subprocess,resource,time,os,signal,json,sys,shutil
from baseline_registry import ROOT,REPO,ref,dump
assert not(ROOT/'runtime/STOP').exists()
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'runner.py')
cmd=['python',*sys.argv[2:]]
dump(out/'plan.json',dict(command=cmd,memory_limit_bytes=4*1024**3,timeout_s=420,source=ref(REPO/cmd[1])))
def limits():resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
t=time.monotonic();timeout=False;stop=False
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
with (out/'analysis.log').open('w') as f:
 p=subprocess.Popen(cmd,cwd=REPO,stdout=f,stderr=subprocess.STDOUT,preexec_fn=limits,start_new_session=True,env=env)
 while p.poll() is None:
  if time.monotonic()-t>420 or (ROOT/'runtime/STOP').exists():
   timeout=time.monotonic()-t>420;stop=(ROOT/'runtime/STOP').exists();os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL)
   break
  time.sleep(.2)
 p.wait()
dump(out/'execution.json',dict(command=cmd,exit_code=p.returncode,elapsed_s=time.monotonic()-t,timeout=timeout,STOP=stop,reaped=True,PID=p.pid,log=ref(out/'analysis.log')))
print((out/'execution.json').read_text())
