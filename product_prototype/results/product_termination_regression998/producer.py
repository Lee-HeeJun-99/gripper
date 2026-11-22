"""Bounded design/provenance regressions;not physical product certification."""
import argparse,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
from analyse import sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);test=BASE/'cad/test_manufacturing.py';proc=guarded([sys.executable,test,'-v'],out/'process',480)
 result=dict(status='PASS_DESIGN_REGRESSIONS_NOT_PRODUCT_GATES' if proc['exit_code']==0 else 'FAIL_DESIGN_REGRESSION',scope='CAD numerical/reference checks and measured-data provenance guards only;NO physical fatigue/strength/holding/lift/STEP/timeGate qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),test_sha256=sha(test),process=proc)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'test_manufacturing.py').write_bytes(test.read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
