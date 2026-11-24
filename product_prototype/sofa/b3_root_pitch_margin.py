"""Local rigid mount clearance derivative,NOT a certified angle range."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();cfg=json.loads((src/'config.json').read_text());centre=np.array(cfg['simulation']['sphere_center_mm'])/1000;R=.03;records=[]
 for i,angle in enumerate((0,120,240)):
  q0=np.fromstring(root.find(f"./Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);skin=root.find(f"./Node[@name='finger{i}']/Node[@name='skinCollision']");ids=np.fromstring(skin.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tri=np.fromstring(skin.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);theta=np.deg2rad(angle);origin=.05*np.array([np.cos(theta),np.sin(theta),0]);axis=np.array([-np.sin(theta),np.cos(theta),0])
  def closest(delta):
   q=origin+Rotation.from_rotvec(delta*axis).apply(q0-origin);near=trimesh.triangles.closest_point(q[ids[tri]],np.repeat(centre[None],len(tri),axis=0));gaps=np.linalg.norm(near-centre,axis=1)-R;k=int(np.argmin(gaps));return float(gaps[k]),near[k]
  gap,P=closest(0);radial=(P-centre)/np.linalg.norm(P-centre);derivative=float(np.dot(radial,np.cross(axis,P-origin)));h=1e-6;fd=(closest(h)[0]-closest(-h)[0])/(2*h);estimate=(gap-.0002)/(-derivative)
  records.append(dict(finger=i,baseline_mount_pitch_deg=cfg['palm']['root_angle_deg'],initial_skin_gap_m=gap,local_gap_derivative_m_per_rad=derivative,finite_difference_m_per_rad=fd,derivative_absolute_difference=abs(fd-derivative),first_order_additional_pitch_to_contact_margin_deg=float(np.rad2deg(estimate))))
 d=dict(status='LOCAL_GEOMETRY_DERIVATIVE_ONLY',records=records,scope='Rigid stress-free initialmountvariation,not actuation. First-order estimate only,not certified feasible angle interval. Hardware/wire/assembly clearances remain NOT MEASURED. Root14deg already exists;rejected1323 adds14deg,total28.',physical_validation='NOT QUALIFIED',input_hashes={f:sha(src/f) for f in ('scene.scn','config.json')});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
