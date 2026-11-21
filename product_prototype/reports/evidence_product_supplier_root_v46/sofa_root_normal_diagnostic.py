"""Read-only first-nonfinite contact provenance;no normal/velocity repairs."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in a.cases:
  source=BASE/'results'/case;dest=out/case;dest.mkdir()
  # Snapshot exactly the observed prefix. This does not stop/change running SOFA.
  for name in ('wheel.csv','direct.csv','response.csv','detector.csv'):shutil.copyfile(source/name,dest/name)
  rows=list(csv.DictReader((dest/'direct.csv').open()));bad=[r for r in rows if not np.isfinite(np.fromstring(r['J'],sep=' ')).all()];responses=list(csv.DictReader((dest/'response.csv').open()));detections=list(csv.DictReader((dest/'detector.csv').open()));states=list(csv.DictReader((dest/'wheel.csv').open()));events=[]
  if bad:
   first=min(float(r['time_s']) for r in bad)
   for row in [r for r in bad if float(r['time_s'])==first]:
    owners=[r for r in responses if r['time_s']==row['time_s'] and r['row_id']==row['row_id']]
    if len(owners)!=1:raise ValueError('nonunique physicalrowowner')
    owner=owners[0];pairs=[r for r in detections if float(r['accepted_time_s'])==first and r['model0']==owner['model0'] and r['model1']==owner['model1']];distances=[float(np.linalg.norm(np.fromstring(r['detected_point0'],sep=' ')-np.fromstring(r['detected_point1'],sep=' '))) for r in pairs]
    events.append(dict(time_s=first,row_id=int(row['row_id']),model_pair=[owner['model0'],owner['model1']],free_position_finite=bool(np.isfinite(np.fromstring(row['free_q'],sep=' ')).all()),free_velocity_finite=bool(np.isfinite(np.fromstring(row['free_v'],sep=' ')).all()),matching_pair_detections=len(pairs),exactly_coincident_detected_pairs=sum(x==0 for x in distances),minimum_detected_distance_m=min(distances) if distances else None))
  invalid=[float(r['time_s']) for r in states if not np.isfinite(np.fromstring(r['rigid_q']+' '+r['rigid_v'],sep=' ')).all()]
  records.append(dict(case=case,observed_state_rows=len(states),first_nonfinite_state_time_s=min(invalid) if invalid else None,first_nonfinite_J_events=events,prefix_hashes={f.name:sha(f) for f in dest.iterdir()},process_result_available_at_observation=(source/'process/result.json').exists()))
 d=dict(status='OBSERVED_NONFINITE_CONTACT_ROW_NOT_REPAIRED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(Path(__file__)),records=records,scope='Observedimmutableprefix snapshots,notfinalruncompletion. Nonfiniteacceptedstate andJ withfinitefreeq/v identifiescontactrowassembly path,notproofthatiterativesolveralonecausedfailure. Samepair containscoincidentpositions,butdetectorindex isNOTclaimed1to1withrowID;undefinednormalisCAUSEHYPOTHESIS,notdirectnormalmeasurement. NoSDK/state/force/tolerancechanges.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
