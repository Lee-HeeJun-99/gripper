"""Actual rigid guide sector margin split into body translation/swing/twist.
Counterfactual orientations are geometric attribution ONLY, never Native states
or a proof that a torsional stiffener will retain the actual grasp trajectory.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def swing_twist(quaternion,axis):
 axis=np.asarray(axis,dtype=float);axis/=np.linalg.norm(axis);q=np.asarray(quaternion,dtype=float);q/=np.linalg.norm(q)
 v=axis*(q[:3]@axis);twist=np.r_[v,q[3]];norm=np.linalg.norm(twist)
 if norm<=64*np.finfo(float).eps:raise ValueError('180degree swing singularity; cannot infer twist')
 twist/=norm;swing=Rotation.from_quat(q)*Rotation.from_quat(twist).inv()
 angle=2*np.arctan2(twist[:3]@axis,twist[3]);angle=(angle+np.pi)%(2*np.pi)-np.pi
 assert np.max(abs((swing*Rotation.from_quat(twist)).as_matrix()-Rotation.from_quat(q).as_matrix()))<=1e-12
 return swing,float(angle)

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();records=[]
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);assert np.all(q0[:,3:]==[0,0,0,1]);frames=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));anchors=np.fromstring(parent.find("Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);theta=np.deg2rad(i*120);er=np.array([np.cos(theta),np.sin(theta),0]);et=np.array([-er[1],er[0],0])
  for j in range(2):
   node=parent.find(f"Node[@name='cable{j}']/Node[@name='eyelet5']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);local=v-q0[owner,:3];foot=anchors[j*18+15:j*18+18];axis=foot[2]-foot[0];axis/=np.linalg.norm(axis);normal=(-np.sqrt(3)*er+(-1 if j==0 else 1)*et)/2
   # Actual cable0 is positive local tangent-side in world geometry; determine
   # the geometric side rather than trusting the abstract cable label.
   side=np.sign(v.mean(0)@et);normal=(-np.sqrt(3)*er+side*et)/2
   for row in frames:
    q=np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7)[owner];rotation=Rotation.from_quat(q[3:]);swing,angle=swing_twist(q[3:],axis)
    gap=lambda centre,rot:float(-((rot.apply(local)+centre)@normal).max())
    records.append(dict(time_s=float(row['time_s']),finger=i,cable=j,twist_deg=float(np.degrees(angle)),actual_sector_gap_mm=gap(q[:3],rotation)*1000,remove_twist_same_COM_gap_mm=gap(q[:3],swing)*1000,fixed_initial_orientation_same_COM_gap_mm=gap(q[:3],Rotation.identity())*1000,actual_orientation_initial_COM_gap_mm=gap(q0[owner,:3],rotation)*1000))
 worst=min(records,key=lambda r:r['actual_sector_gap_mm']);unsafe=[r for r in records if r['actual_sector_gap_mm']<.1];improve=[r['remove_twist_same_COM_gap_mm']-r['actual_sector_gap_mm'] for r in unsafe]
 d=dict(status='ACTUAL_GUIDE_TRANSLATION_SWING_TWIST_ATTRIBUTION_NOT_DESIGN_PASS',case=a.case,samples=len(records),own_sector_half_buffer_unsafe_samples=len(unsafe),maximum_abs_twist_deg=max(abs(r['twist_deg']) for r in records),worst_actual_margin=worst,minimum_remove_twist_gap_mm=min(r['remove_twist_same_COM_gap_mm'] for r in records),minimum_fixed_initial_orientation_gap_mm=min(r['fixed_initial_orientation_same_COM_gap_mm'] for r in records),unsafe_samples_made_safe_by_twist_removal=sum(r['remove_twist_same_COM_gap_mm']>=.1 for r in unsafe),minimum_twist_removal_margin_gain_mm=min(improve,default=None),maximum_twist_removal_margin_gain_mm=max(improve,default=None),scope='Exact quaternion swing/twist around original bonded-triangle longitudinal axis, reconstructed every sample to1e-12. Hypothetical orientation removal holds actual COM fixed and violates actual attachment motion; not a physical trajectory, no claimed reaction or grasp improvement. Necessary geometric attribution to decide whether torsion-only mechanism is worth a new physical coupon; sector-plane certificate is sufficient not necessary for pair clearance.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn']+[f'guide_frames{i}.csv' for i in range(3)]})
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'history.json').write_text(json.dumps(records));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
