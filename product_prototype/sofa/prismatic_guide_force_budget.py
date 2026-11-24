"""Virtual-work direction for a new translating eyelet; not actual Native J.
Use actual saved path, parent orientation and measured cable multiplier/dt.
Current-geometry ideal string force is an independent mechanical reference,
NOT the lagged Jacobian impulse actually applied by SOFA.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));records=[];input_error=0.
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);frames=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));film=list(csv.DictReader((src/f'finger{i}.csv').open()));theta=np.deg2rad(i*120);er=np.array([np.cos(theta),np.sin(theta),0]);et=np.array([-er[1],er[0],0])
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']");origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');eye=cable.find("Node[@name='eyelet5']");v=np.fromstring(eye.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owner=int(eye.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);local=Rotation.from_quat(q0[owner,3:]).inv().apply(v-q0[owner,:3]);side=np.sign(v.mean(0)@et);normal=(-np.sqrt(3)*er+side*et)/2
   for fr,fl in zip(frames,film):
    assert fr['time_s']==fl['time_s'];time=float(fr['time_s']);q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7)[owner];rot=Rotation.from_quat(q[3:]);path=np.vstack([origin,np.fromstring(fl[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);T=float(fl[f'cable{j}_force_raw'])/dt;input_error=max(input_error,abs(T-float(fl['command_N'])));incoming=path[-2]-path[-1];force=T*incoming/np.linalg.norm(incoming);inward=-side*rot.apply(et);inward/=np.linalg.norm(inward);gap=float(-((rot.apply(local)+q[:3])@normal).max());gain=float(-(normal@inward));travel=max(0.,.0001-gap)/gain if gain>0 else None
    records.append(dict(time_s=time,finger=i,cable=j,actual_measured_tension_N=T,geometric_reference_inward_force_N=float(force@inward),actual_sector_gap_mm=gap*1000,inward_motion_sector_gain=gain,necessary_fixed_pose_travel_mm=travel*1000 if travel is not None else None))
 hold=[r for r in records if 1.6-1e-12<=r['time_s']<=2+1e-12];loaded=[r for r in records if r['actual_measured_tension_N']>0];bad=[r for r in records if r['actual_sector_gap_mm']<.1];assert input_error<=1e-12
 d=dict(status='PASSIVE_TERMINAL_SLIDER_FORCE_DIRECTION_REJECTED' if all(r['geometric_reference_inward_force_N']<0 for r in loaded) else 'MIXED_TERMINAL_SLIDER_FORCE_DIRECTION_REQUIRES_EQUILIBRIUM',case=a.case,samples=len(records),hold_samples=len(hold),maximum_actual_cable_input_error_N=input_error,loaded_samples=len(loaded),loaded_samples_pointing_outward=sum(r['geometric_reference_inward_force_N']<0 for r in loaded),hold_reference_inward_force_range_N=[min(r['geometric_reference_inward_force_N'] for r in hold),max(r['geometric_reference_inward_force_N'] for r in hold)],maximum_reference_outward_load_N=max(max(0.,-r['geometric_reference_inward_force_N']) for r in loaded),unsafe_sector_samples=len(bad),unsafe_samples_with_nonpositive_inward_gain=sum(r['inward_motion_sector_gain']<=0 for r in bad),maximum_necessary_fixed_pose_travel_mm=max(r['necessary_fixed_pose_travel_mm'] for r in bad if r['necessary_fixed_pose_travel_mm'] is not None),scope='Actual stored Cable multipliers/dt and accepted guide positions. F=T*(previousPoint-terminal)/length is an independent ideal-string CURRENT-geometry virtual-work reference; actual Native lagged J and contact redistribution are NOT measured here. A free passive slider cannot simply be presumed to retract against an outward reference load. Active cross-draw/cam/return spring needs a real force source and finite carriage/wire preflight; extra force/friction/strength and dynamic joint integration are not qualified. Necessary fixed-pose travel is not a realizable dynamic route or final chosen stroke.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn']+[f'finger{i}.csv' for i in range(3)]+[f'guide_frames{i}.csv' for i in range(3)]})
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'history.json').write_text(json.dumps(records));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
