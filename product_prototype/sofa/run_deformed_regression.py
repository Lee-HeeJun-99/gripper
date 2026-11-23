import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--pattern',choices=['test_deformed_and_joint.py','test_initial_assembly.py'],default='test_deformed_and_joint.py');p.add_argument('--expected',type=int,default=8);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    test=BASE/'sofa'/a.pattern;cmd=['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s',str(BASE/'sofa'),'-p',test.name]
    proc=guarded(cmd,out/'process',60);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));d=dict(status='PASS_SOFTWARE_SCOPE_REGRESSION' if proc['exit_code']==0 and f'Ran {a.expected} tests' in logs else 'FAIL_REGRESSION',process=proc,test_source_sha256=sha(test),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),physical_validation='NOT QUALIFIED')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'test_source.py').write_bytes(test.read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
