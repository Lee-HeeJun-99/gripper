import os,sys,json,hashlib,subprocess,resource,time,pathlib
R=pathlib.Path.cwd();root=R/'product_prototype/stage12_integrated';out=root/'validation/overload/batch6_drive_cycle1';out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name,script,*args=sys.argv[1:];p=R/script
plan=dict(command=[sys.executable,str(p),*args],producer_SHA256=sha(p),memory_limit_bytes=4*1024**3,timeout_s=420)
(out/(name+'_plan.json')).write_text(json.dumps(plan,indent=2)+'\n')
assert not (root/'runtime/STOP').exists()
env=dict(os.environ,PYTHONPATH='/tmp/regrip_stage1_ocp:'+str(root/'scripts'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
def limit():resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
t=time.monotonic()
with (out/(name+'.log')).open('w') as f:
 child=subprocess.Popen(plan['command'],stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=limit)
 try:code=child.wait(timeout=420);timed=False
 except subprocess.TimeoutExpired:child.kill();code=child.wait();timed=True
plan.update(exit_code=code,timeout=timed,elapsed_s=time.monotonic()-t,PID=child.pid,reaped=True)
(out/(name+'_execution.json')).write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(plan))
