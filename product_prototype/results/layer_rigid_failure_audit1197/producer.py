import argparse,csv,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};files=[];corners=np.array([[x,y,z] for x in (-.02,.02) for y in (-.005,.005) for z in (-.0001,.0001)])
 for case in ('layer_rigid_slip1195','layer_rigid_friction1196'):
  file=BASE/'results'/case/'rigid.csv';rows=list(csv.DictReader(file.open()));first=None
  for r in rows:
   q=np.fromstring(r['rigid_q'],sep=' ');world=Rotation.from_quat(q[3:]).apply(corners)+q[:3]
   if world[:,2].max()<-.002 and first is None:first=float(r['time_s'])
  records[case]=dict(status='FAIL_RIGID_SUPPORT_TUNNELING',first_entire_body_below_support_bottom_s=first,final_centre_z_m=float(np.fromstring(rows[-1]['rigid_q'],sep=' ')[2]),friction_law_validation='BLOCKED_BY_CONTACT_GEOMETRY',layer_jamming='NOT VALIDATED');files.append(file)
 d=dict(status='FAIL_COMPONENT_CONTACT_GEOMETRY',records=records,scope='Actual eight transformed box corners entirely below fixed2mm support. No arbitrary displacement floor. No solver-exit-to-physical-PASS promotion.',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
