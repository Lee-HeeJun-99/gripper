"""Archived independent tests of the frozen-oscillator rational integrators."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');files=['tools/film_surface_modal_response.py','tools/curve_common.py','tests/test_modal_rational.py']
 for name in files:
  target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 run=guarded(['/home/ubuntu/miniconda3/envs/robot_ws/bin/python',out/'sources/tests/test_modal_rational.py'],out/'run',60);write_json(out/'summary.json',dict(status='PASS' if run['exit_code']==0 else 'FAIL',scope='independent damped oscillator local-order/energy/ballistic unit tests;NOT SOFA integration',run=run,sources={name:sha(ROOT/name) for name in files}));print(json.dumps(dict(status='PASS' if run['exit_code']==0 else 'FAIL')))
if __name__=='__main__':main()
