import subprocess,resource,time,json,pathlib,os,sys,hashlib
root=pathlib.Path.cwd(); base=root/'product_prototype/stage12_integrated'; name=sys.argv[1]; command=['python',str(base/'scripts'/sys.argv[2]),*sys.argv[3:]]; out=base/'validation/integrated'/('primary46_'+name+'_execution');out.mkdir(); env=os.environ.copy();env.update(PYTHONPATH='/tmp/regrip_stage2_fem:/tmp/regrip_stage1_ocp',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'plan.json').write_text(json.dumps(dict(command=command,memory_limit_bytes=4294967296,timeout_s=420,source=dict(path=str(pathlib.Path(command[1]).relative_to(root)),SHA256=sha(pathlib.Path(command[1])))),indent=2))
def limits():resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296))
start=time.monotonic(); stop=False; timeout=False
with (out/'stdout.log').open('w') as a,(out/'stderr.log').open('w') as b:
 p=subprocess.Popen(command,stdout=a,stderr=b,env=env,preexec_fn=limits)
 while p.poll() is None:
  stop=(base/'runtime/STOP').exists();timeout=time.monotonic()-start>420
  if stop or timeout:p.kill();break
  time.sleep(.2)
 rc=p.wait()
record=dict(command=command,exit_code=rc,seconds=time.monotonic()-start,timeout=timeout,STOP=stop,reaped=True);(out/'execution.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
