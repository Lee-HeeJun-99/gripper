"""Bounded frozen regression bundle for actual Native contact/ODE limits."""
import argparse,json,sys
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);test=BASE/'sofa/test_native_contact_policy.py';proc=guarded([sys.executable,test,'-v'],out/'process',480);result=dict(status='PASS_CONTACT_POLICY_REGRESSIONS_ONLY' if proc['exit_code']==0 else 'FAIL_REGRESSION',scope='Preserve measured Native negative controls,not contact/time/B3 product qualification',test_sha256=sha(test),producer_sha256=sha(Path(__file__)),process=proc);(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'test_native_contact_policy.py').write_bytes(test.read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
