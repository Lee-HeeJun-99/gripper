"""Read-only detector-point clock test in actual orientation-fixture runs.
Free translation reconstructed from measured impulse and verified mass law.
Only layer vertex/PointCollisionModel points used,not arbitrary line points.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};files=[]
 for case in ('layer_fixture_slip1206','layer_fixture_friction1207'):
  src=BASE/'results'/case;rows=list(csv.DictReader((src/'rigid.csv').open()));mass=json.loads((src/'rigid.csv.mass.json').read_text())['elements'][0]['mass_kg'];states=[];previous=np.array([0,0,.000102]);kinematic=0
  for r in rows:
   q=np.fromstring(r['rigid_q'],sep=' ');v=np.fromstring(r['rigid_v'],sep=' ');I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3];assert np.linalg.norm(v[3:])==0;freev=v[:3]-I/(mass*1.0002);freeq=previous+.0002*freev;kinematic=max(kinematic,float(abs(q[:3]-previous-.0002*v[:3]).max()));states.append(dict(time=float(r['time_s']),previous_z=previous[2],free_z=freeq[2],accepted_z=q[2]));previous=q[:3]
  error={k:[] for k in ('previous_z','free_z','accepted_z')};first=[]
  for r in csv.DictReader((src/'layer_pairs.csv').open()):
   side=0 if r['model0'].startswith('/layer/') and 'PointCollisionModel' in r['model0'] else 1 if r['model1'].startswith('/layer/') and 'PointCollisionModel' in r['model1'] else None
   if side is None:continue
   t=float(r['accepted_time_s']);i=round(t/.0002)-1;assert abs(states[i]['time']-t)<1e-12;point=np.fromstring(r[f'detected_point{side}'],sep=' ');entry={'time_s':t}
   for k in error:
    e=min(abs(point[2]-(states[i][k]-.0001)),abs(point[2]-(states[i][k]+.0001)));error[k].append(e);entry[k+'_point_error_m']=float(e)
   if .0003<t<.0005:first.append(entry)
  records[case]=dict(vertex_samples=len(error['previous_z']),RMS_vertex_Z_error_m={k:float(np.sqrt(np.mean(np.array(v)**2))) for k,v in error.items()},maximum_accepted_kinematic_error_m=kinematic,first_loaded_step_samples=first[:2],scope='Coordinate-time association only;not unique detector/solver defect or a contact repair')
  files.extend([src/'rigid.csv',src/'rigid.csv.mass.json',src/'layer_pairs.csv'])
 d=dict(status='DETECTOR_PHASE_ASSOCIATION_ONLY',records=records,physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
