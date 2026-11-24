"""Bounded exploration of a same-finger terminal structural loop.
Requires an actually verified mass assembly and initial finite-geometry gate.
No collision removal, imposed object state or fitted material stiffness.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
from scipy.spatial.transform import Rotation

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--design',default='dorsal_yoke1723');p.add_argument('--mass-contract');p.add_argument('--duration',type=float,choices=(.6,1.2,2.),default=.6);p.add_argument('--pilot');p.add_argument('--pair-case');a=p.parse_args()
 design=BASE/'results'/a.design;src=BASE/'results/capillary_hold1700';d=json.loads((design/'summary.json').read_text());assert d['status']=='READY_DORSAL_YOKE_NATIVE_PILOT';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(design/'scene.scn').getroot();forecast=180.
 if a.design!='dorsal_yoke1723':
  assert a.mass_contract;m=json.loads((BASE/'results'/a.mass_contract/'summary.json').read_text());assert m['case']==a.design and m['status']=='PASS_ACTUAL_YOKE_INITIAL_TENSOR_ASSEMBLY_ONLY'
 if a.duration>.6:
  assert a.pilot and a.pair_case;pilot=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pairs=json.loads((BASE/'results'/a.pair_case/'summary.json').read_text());inter=json.loads((BASE/'results'/a.pilot/'intervention.json').read_text());assert inter.get('design_case','dorsal_yoke1723')==a.design;assert pilot['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pairs['case']==a.pilot and pairs['nonzero_rows']==0
  forecast=pilot['process']['runtime_s']*a.duration/pilot['duration_s']*2;assert forecast<420
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(design),str(out)))
 tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);checks=[]
 for i in range(3):
  q=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);vol=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/6;assert np.isfinite(vol).all() and np.all(vol!=0)
  old=np.fromstring(ET.parse(src/'scene.scn').getroot().find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);assert np.array_equal(q,old)
  checks.append(dict(finger=i,initial_FEM_coordinate_difference_m=0,minimum_absolute_tet_volume_m3=float(abs(vol).min())))
 pre=json.loads((src/'preflight.json').read_text());inter=dict(source_sha256=sha(Path(__file__)),design_case=a.design,geometry_summary_sha256=sha(design/'summary.json'),indexed_mass_contract_sha256=sha(BASE/'results/indexed_mass1720/summary.json'),initial_FEM=checks,scope=d['scope'],density_assumption_kg_m3=d['density_kg_m3'],variable='Physical terminal same-finger rung, shared6foot rigid body, added finite geometry and correct assumed mass/COM/inertia; not material/force/solver changes')
 (out/'intervention.json').write_text(json.dumps(inter,indent=2));run_three(root,out,src,pre['eyelet'],d['all_parts'],round(a.duration/.0025),a.duration,forecast,configuration_source=design);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 mapping_error=0.;distance_error=0.
 for i in range(3):
  q0=np.fromstring(root.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);points=[]
  for j in range(2):
   n=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/MechanicalObject");p0=np.fromstring(n.get('position'),sep=' ').reshape(-1,3)[5];points.append(p0-q0[5,:3])
  expected_distance=np.linalg.norm(points[0]-points[1])
  for fr,fl in zip(csv.DictReader((out/f'guide_frames{i}.csv').open()),csv.DictReader((out/f'finger{i}.csv').open())):
   assert fr['time_s']==fl['time_s'];q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7);assert len(q)==11;rot=Rotation.from_quat(q[5,3:]);actual=[]
   for j in range(2):
    x=np.fromstring(fl[f'guide{j}_q_m'],sep=' ').reshape(-1,3)[5];mapping_error=max(mapping_error,float(abs(x-(q[5,:3]+rot.apply(points[j]))).max()));actual.append(x)
   distance_error=max(distance_error,abs(np.linalg.norm(actual[0]-actual[1])-expected_distance))
 result=dict(status='PASS_SHARED_TERMINAL_MAPPING_ONLY' if max(mapping_error,distance_error)<=1e-12 else 'FAIL_SHARED_TERMINAL_MAPPING',maximum_mapped_cable_point_error_m=mapping_error,maximum_opposed_terminal_distance_error_m=distance_error,scope='Actual new Native11-body guide state, both cable terminals on one yoke and original six FEM feet. Not grasp, full energy or real joint strength PASS.');(out/'mapping_assessment.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
