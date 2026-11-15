"""Run old tests in a NEW output namespace, never in historical fixture folders."""
import os,subprocess
from grasp_common import ROOT,OUT,PYTHON,write_json
def main():
    out=OUT/'python_tests_isolated';out.mkdir(exist_ok=False)
    (out/'optimization_guards_release').mkdir();(out/'automation').mkdir()
    env=dict(os.environ,PYTHONPATH=str(ROOT)+':'+str(ROOT/'tools'),OPENBLAS_NUM_THREADS='1',REGRIP_VERIFICATION_OUT=str(out),REGRIP_AUTOMATION_OUT=str(out/'automation'),REGRIP_PHYSICS_OUT=str(ROOT/'results/revalidation_20261114T132734Z/physics_release'),REGRIP_BUILD_ROOT=str(ROOT/'build/revalidation_20261114_final'))
    command=[PYTHON,'-m','unittest','discover','-s','tests','-p','test_*.py'];write_json(out/'command.json',dict(command=command,environment={k:v for k,v in env.items() if k.startswith('REGRIP_') or k in ('PYTHONPATH','OPENBLAS_NUM_THREADS')}))
    p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120);(out/'tests.log').write_text(p.stdout+p.stderr);write_json(out/'result.json',dict(status='PASS' if p.returncode==0 else 'FAIL',exit_code=p.returncode,scope='classifier fault-injection fixtures explicitly not physics measurements; real-SOFA launcher tests are separately labelled in tests'))
    print(p.returncode,(p.stdout+p.stderr)[-600:])
if __name__=='__main__':main()
