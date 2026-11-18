"""Preserved independent analytic linear-model unit test."""
import argparse,json,shutil,subprocess,sys
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=out/'test_control_transmission.py';shutil.copy2(ROOT/'tests/test_control_transmission.py',source);shutil.copy2(__file__,out/'runner.py');run=guarded([sys.executable,source],out/'process',120);result=dict(status='FAIL',scope='independent analytic linear three-mass reference;NOT actual nonlinear SOFA',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),process=run)
 if run['exit_code']==0:result.update(json.loads((out/'process/stdout.log').read_text()))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='process'}))
if __name__=='__main__':main()
