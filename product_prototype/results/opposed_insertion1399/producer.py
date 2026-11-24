"""Virtual R30 insertion-envelope check on actual no-object Native trajectory.
No sphere/contact exists in this experiment. Never a Holding/contact verdict.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='opposed_nonuniform_mid1398');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());assert meta['status']=='BOUNDED_NO_OBJECT_ACTUATION_ONLY';root=ET.parse(src/'scene.scn').getroot();assert root.find("Node[@name='object']") is None;finger=root.find("Node[@name='finger0']");skin=finger.find("Node[@name='skinCollision']");ids=np.fromstring(skin.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tri=ids[np.fromstring(skin.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)];g=root.find("Node[@name='guides0']");q0=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);routes=[]
 for cable in range(2):
  n=g.find(f"Node[@name='cable{cable}']");route=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owner=np.fromstring(n.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);local=Rotation.from_quat(q0[owner,3:]).inv().apply(route-q0[owner,:3]);pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ');routes.append((owner,local,pull))
 film=list(csv.DictReader((src/'finger0.csv').open()));guides=list(csv.DictReader((src/'guide_frames0.csv').open()));assert len(film)==len(guides);centre=np.array([0.,0.,-.065]);R=.03;history=[]
 for r,gg in zip(film,guides):
  assert r['time_s']==gg['time_s'];q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);near=trimesh.triangles.closest_point(q[tri],np.repeat(centre[None],len(tri),axis=0));gap=float((np.linalg.norm(near-centre,axis=1)-R).min());fq=np.fromstring(gg['rigid_q'],sep=' ').reshape(-1,7);wire=[];hardware=[]
  for owner,local,pull in routes:
   route=fq[owner,:3]+Rotation.from_quat(fq[owner,3:]).apply(local);hardware.append(float((np.linalg.norm(route-centre,axis=1)-R-np.hypot(.0015,.001)).min()));path=np.vstack([pull,route]);A=path[:-1];D=np.diff(path,axis=0);s=np.clip(np.einsum('ij,ij->i',centre-A,D)/np.einsum('ij,ij->i',D,D),0,1);wire.append(float((np.linalg.norm(A+s[:,None]*D-centre,axis=1)-R-.00025).min()))
  history.append(dict(time_s=float(r['time_s']),virtual_sphere_skin_gap_m=gap,virtual_sphere_wire_gap_m=min(wire),virtual_sphere_guide_proxy_gap_m=min(hardware)))
 window=[r for r in history if r['time_s']>=.5-1e-12];safe=lambda r:r['virtual_sphere_skin_gap_m']>=.0002 and min(r['virtual_sphere_wire_gap_m'],r['virtual_sphere_guide_proxy_gap_m'])>0;valid=bool(window) and all(safe(r) for r in window);d=dict(status='PASS_SINGLE_FINGER_VIRTUAL_INSERTION_ENVELOPE_ONLY' if valid else 'FAIL_VIRTUAL_INSERTION_ENVELOPE',case=a.case,criterion='All actual saved .5–.6s samples:Skin gap>=.2mm,finitewire/guideproxygap>0 against virtualR30at(0,0,-65mm)',endpoint=history[-1],window_outputs=len(window),window_minimum_skin_gap_m=min((r['virtual_sphere_skin_gap_m'] for r in window),default=None),first_saved_clear_time_s=next((r['time_s'] for r in history if safe(r)),None),history=history,scope='Actual no-object NativeSkin+RigidGuide states vsvirtual sphere. NOT actualinsertion/contact/3Finger synchronization/sweptclearance orHolding. Supportcapsule/actualbored eyelet clearance and fullCAD mass/joints NOTQUALIFIED.',physical_validation='NOT QUALIFIED',input_hashes={f:sha(src/f) for f in ('scene.scn','finger0.csv','guide_frames0.csv','summary.json')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('history','input_hashes')}))
if __name__=='__main__':main()
