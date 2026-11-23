import argparse,json,subprocess,sys,shutil
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);test=BASE/'sofa/test_cable_origin_lift.py';proc=guarded([sys.executable,test,'-v'],out/'process',60)
 d=dict(status='PASS_EVIDENCE_REGRESSIONS_ONLY' if proc['exit_code']==0 else 'FAIL_EVIDENCE_REGRESSIONS',process=proc,test_sha256=sha(test),producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),physical_validation='NOT QUALIFIED');shutil.copy2(test,out/test.name);shutil.copy2(Path(__file__),out/'producer.py');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
