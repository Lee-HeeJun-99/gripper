"""Bounded scoped software regressions and SDK identity,not physics PASS."""
import argparse,json,subprocess
from pathlib import Path
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);py='/home/ubuntu/miniconda3/envs/robot_ws/bin/python';records=[]
 tests=[(BASE/'sofa/test_reinforcement_bending.py',8),(BASE/'sofa/test_contact_layer.py',20),(BASE/'tools/test_research_queue.py',5),(BASE/'tools/test_layer_measurement_ingest.py',8),(BASE/'sofa/test_contact_adaptation_profile.py',3),(BASE/'sofa/test_opposed_tendon.py',8),(BASE/'sofa/test_antagonistic_routes.py',4)]
 tests.extend([(BASE/'sofa/test_eyelet_entry.py',3),(BASE/'sofa/test_eccentric_eyelet_mesh.py',3),(BASE/'sofa/test_eyelet_evidence.py',3)])
 for i,(test,count) in enumerate(tests):
  cmd=[py,'-m','unittest','discover','-s',str(test.parent),'-p',test.name];proc=guarded(cmd,out/f'test{i}',60);log=''.join((out/f'test{i}'/f).read_text() for f in ('stdout.log','stderr.log'));records.append(dict(test=str(test.relative_to(BASE)),sha256=sha(test),expected_tests=count,pass_scope=proc['exit_code']==0 and f'Ran {count} tests'in log,process=proc))
 old=json.loads((BASE/'results/contact_layer_final_regression1363/summary.json').read_text());sdk={f:sha(Path(f)) for f in old['SDK_identity']};d=dict(status='PASS_SCOPED_SOFTWARE_REGRESSIONS' if all(r['pass_scope'] for r in records) and sdk==old['SDK_identity'] else 'FAIL_REGRESSION_OR_SDK_IDENTITY',tests=sum(c for f,c in tests),records=records,SDK_identity=sdk,SDK_equal_previous=sdk==old['SDK_identity'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),physical_validation='NOT QUALIFIED',hardware='NOT MEASURED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(status=d['status'],tests=d['tests'],SDK_equal_previous=d['SDK_equal_previous'])))
if __name__=='__main__':main()
