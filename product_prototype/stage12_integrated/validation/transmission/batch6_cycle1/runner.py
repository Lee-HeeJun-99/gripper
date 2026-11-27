"""Bounded sequential analysis only; no manager or Git writes."""
import hashlib,json,os,resource,signal,subprocess,time
from pathlib import Path
repo=Path.cwd();root=repo/'product_prototype/stage12_integrated';out=root/'validation/transmission/batch6_cycle1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def limits():resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
env=dict(os.environ,PYTHONPATH='/tmp/regrip_stage1_ocp:'+str(root/'scripts'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
records=[]
for name,script in [('operating2','batch6_operating_contract.py'),('interface1','batch6_micro_drive.py')]:
    assert not (root/'runtime/STOP').exists()
    p=root/'scripts'/script;cmd=['python',str(p)];start=time.time()
    with (out/(name+'.log')).open('x') as f:
        proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,preexec_fn=limits,start_new_session=True)
        timeout=False
        try:code=proc.wait(timeout=420)
        except subprocess.TimeoutExpired:
            timeout=True;os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            code=proc.returncode
    records.append(dict(name=name,command=cmd,producer_SHA256=sha(p),exit_code=code,timeout=timeout,elapsed_s=time.time()-start,PID=proc.pid,reaped=True,memory_limit_bytes=4*1024**3))
    (out/'execution.json').write_text(json.dumps(records,indent=2)+'\n')
    if code not in (0,2):break
print(json.dumps(records,indent=2))
