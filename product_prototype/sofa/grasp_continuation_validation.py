"""Bounded current-cycle software evidence plus unchanged SDK,not physics PASS."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in ('test_grasp_continuation.py','test_cable_latch_contract.py','test_conformal_cradle.py','test_mesh_handedness.py'):
  command=['/home/ubuntu/miniconda3/envs/robot_ws/bin/python','-m','unittest','discover','-s',str(BASE/'sofa'),'-p',name];process=guarded(command,out/name,60);text=''.join((out/name/f).read_text() for f in ('stdout.log','stderr.log'));records.append(dict(name=name,source_sha256=sha(BASE/'sofa'/name),process=process,pass_scope=process['exit_code']==0 and 'Ran 4 tests'in text))
 reference=json.loads((BASE/'results/contact_layer_final_regression1363/summary.json').read_text())['SDK_identity'];sdk={name:sha(Path(name)) for name in reference};d=dict(status='PASS_SIXTEEN_SOFTWARE_TESTS_AND_SDK_IDENTITY' if all(r['pass_scope'] for r in records) and sdk==reference else 'FAIL_TEST_OR_SDK',records=records,SDK_identity=sdk,SDK_equal_reference=sdk==reference,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope='Software evidence only,not newgrasp/time/mesh/physicalPASS');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(d['status'])
if __name__=='__main__':main()
