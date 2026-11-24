"""Read-only section control/reference and static-response comparison."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_face_load import tip_load
from layer_bending_reference import reference
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',default='layer_section_native1288');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in ('layer_traction_native1282',a.source):
  src=BASE/'results'/name;m=json.loads((src/'mesh.json').read_text());q=np.array(m['q0']);t=np.array(m['tetrahedra']);F,_,_=tip_load(q,t,[0,0,-5e-5]);r=reference(q,t,F);rows=list(csv.DictReader((src/'layer0.csv').open()));states=np.array([np.fromstring(v['q'],sep=' ').reshape(-1,3) for v in rows]);vel=np.array([np.fromstring(v['v'],sep=' ').reshape(-1,3) for v in rows]);u=states[-1]-q;tip=(states[:,q[:,0]==.04,2]-q[q[:,0]==.04,2]).mean(axis=1)
  records.append(dict(source=name,outputs=len(rows),max_reference_displacement_error_m=float(abs(u-r['u']).max()),tip_m=float(tip[-1]),last50_tip_drift_m=float(np.ptp(tip[-50:])),last50_max_speed_m_s=float(np.linalg.norm(vel[-50:],axis=2).max()),reference_tip_m=r['reference_tip_m'],reference_energy_J=r['reference_energy_J'],reference_shear_fraction=r['reference_tip_shear_energy_fraction'],work_conjugate_displacement_m=float((F*u).sum()/-5e-5),input_hashes={f:sha(src/f) for f in ('scene.scn','preflight.json','mesh.json','layer0.csv')}))
 pair=abs(records[0]['tip_m']-records[1]['tip_m'])/max(abs(v['tip_m']) for v in records)
 d=dict(status='PASS_ENDPOINT_REFERENCE_ONLY' if all(v['max_reference_displacement_error_m']<=1e-12 for v in records) else 'FAIL_REFERENCE',records=records,section_tip_relative_difference=pair,section_mesh_gate=.01,section_mesh_verdict='PASS_PAIR_ONLY' if pair<=.01 else 'FAIL',scope='Native endpoint agreement only;one coarse thickness pair is NOT full mesh convergence. UniformMass changes nodal section inertia. No pressure/friction/jamming qualification.',physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
