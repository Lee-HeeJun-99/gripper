"""Hash-bound matching-input strict API reassessment,NO new SOFA execution."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--proof',required=True);a=p.parse_args();proof=ROOT/'results'/('autonomous_film_'+a.proof);pm=json.loads((proof/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';am=json.loads((actual/'summary.json').read_text());failure=ROOT/'results/autonomous_film_20261118_three_film_absolute_audit1006'
 if pm['status']!='PASS' or pm['state_injection'] or pm['absolute_api_gate']!=1e-12 or pm['modes']['accumulated']['api_status']!='PASS' or pm['modes']['multiplied']['api_status']!='FAIL':raise ValueError('same-binary clock counterfactual proof required')
 if pm['actual_summary_sha256']!=sha(actual/'summary.json') or pm['actual_raw_sha256']!=am['raw_hashes'] or sha(proof/'reference')!=pm['binary_sha256']:raise ValueError('proof/actual identity mismatch')
 checked=[]
 for name,digest in am['sources'].items():
  if name.endswith('.h'):
   if pm['sources'].get(name)!=digest or sha(actual/'sources'/name)!=digest or sha(proof/'sources'/name)!=digest:raise ValueError('actual/reference kernel changed:'+name)
   checked.append(name)
 for name,digest in am['raw_hashes'].items():
  if sha(actual/name)!=digest:raise ValueError('actual raw changed:'+name)
 for name,digest in am['plugins'].items():
  if sha(name)!=digest:raise ValueError('actual plugin changed')
 scene=ET.parse(actual/'scene.scn')
 for field in scene.findall('.//FilmRailTendon'):
  if any(float(field.get(k))!=v for k,v in dict(nx=21,guideIntervals=4,guideOffset=5,bondStiffness=.001,maximumTension=.0001,rampTime=.01,releaseBegin=.02,releaseEnd=.03,c2Control=1,rootGuideSecondOrder=1).items()):raise ValueError('different physical/control inputs')
 path=proof/'accumulated.csv.states.csv'
 if sha(path)!=pm['modes']['accumulated']['states_sha256']:raise ValueError('reference raw changed')
 rows=list(csv.DictReader((actual/'three.states.csv').open()));reference=list(csv.DictReader(path.open()));errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,reference)) for k in ('q','v')};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(rows,reference));valid=len(rows)==len(reference)==50 and max(errors.values())<1e-12 and clock==0
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if valid else 'FAIL',scope='reassessment of SAME actual1002 using exact matching accumulated input clock;NOT new actual run,time/full energy/grasp',actual=actual.name,absolute_api_gate=1e-12,errors=errors,clock_error_s=clock,proof=a.proof,proof_sha256=sha(proof/'summary.json'),prior_strict_FAIL_preserved=sha(failure/'summary.json'),actual_summary_sha256=sha(actual/'summary.json'),checked_kernel_headers=checked,reference_states_sha256=sha(path),original_loose_runner_PASS_not_used=True,explanation='same C2 physical law,public masses,kernel,dt;actual SOFA accumulates t+=dt,old reference used step*dt.Only FP input clock matched;no actual state/force/gate changed',remaining=['full time997 FAIL','first-interval journal/full physical energy','release/re-impact/full cycle','full thickness/friction/self-contact','wrapping/lift/grasp/12wrench/Optuna']);write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','absolute_api_gate','errors','clock_error_s')}))
if __name__=='__main__':main()
