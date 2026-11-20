"""Guarded frozen actual Native inertia regression evidence."""
import argparse,json,sys
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);test=BASE/'sofa/test_native_inertia.py';process=guarded([sys.executable,test,'-v'],out/'process',480);result=dict(status='PASS_NATIVE_INERTIA_REGRESSION' if process['exit_code']==0 else 'FAIL_NATIVE_INERTIA_REGRESSION',scope='Actual input law/group bookkeeping/offline derivative;NOT an implicit-force/physical contact/time/B3 qualification',test_sha256=sha(test),producer_sha256=sha(Path(__file__)),process=process);(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'test_native_inertia.py').write_bytes(test.read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
