"""Actual Cable multiplier + previous accepted geometry terminal load budget.
No invented crimp capacity, bond allowable or material certification.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from winch_transfer_assess import unique_row

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;summary=json.loads((src/'summary.json').read_text());assert summary['process']['exit_code']==0;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));read=lambda p:list(csv.DictReader(p.open()));records=[];inputs=[src/'summary.json',src/'scene.scn'];area=np.pi*.0005*.001
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");q0=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);file=src/f'guide_frames{i}.csv';frames=read(file);inputs.append(file);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);prev=np.concatenate([q0[None],q[:-1]]);wrench=np.zeros((len(q),6))
  for j in range(2):
   node=parent.find(f"Node[@name='cable{j}']");points=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[-2:];owners=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)[-2:];assert owners[-1]==5;motion=[]
   for point,owner in zip(points,owners):
    local=Rotation.from_quat(q0[owner,3:]).inv().apply(point-q0[owner,:3]);motion.append(Rotation.from_quat(prev[:,owner,3:]).apply(np.repeat(local[None],len(q),axis=0))+prev[:,owner,:3])
   phasefile=src/f'drive_{i}_{j}_phases.csv';inputs.append(phasefile);phases=[r for r in read(phasefile) if r['phase']=='accepted_end'];assert len(phases)==len(q);T=np.array([np.fromstring(r['lambda_Ns'],sep=' ')[unique_row(r['J'],1)]/dt for r in phases]);direction=motion[0]-motion[1];direction/=np.linalg.norm(direction,axis=1)[:,None];force=T[:,None]*direction;moment=np.cross(motion[1]-prev[:,5,:3],force);wrench+=np.hstack([force,moment]);records.append(dict(finger=i,tendon=j,maximum_terminal_tension_N=float(T.max()),maximum_uniform_pullout_interface_shear_requirement_Pa=float(T.max()/area),assumed_pullout_cylindrical_area_m2=float(area)))
  records.append(dict(finger=i,combined_body5_maximum_terminal_resultant_N=float(np.linalg.norm(wrench[:,:3],axis=1).max()),combined_body5_maximum_terminal_moment_Nm=float(np.linalg.norm(wrench[:,3:],axis=1).max()),note='Only endpoint tendon load, not all body5 external forces, inertia, gravity or attachment reactions'))
 d=dict(status='PASS_RECONSTRUCTED_TERMINAL_LOAD_BUDGET_ONLY',case=a.case,records=records,measured_pullout_strength_N=None,measured_bond_allowable_Pa=None,measured_wire_bend_fatigue=None,measured_material=None,source_sha256=sha(Path(__file__)),input_hashes={str(f.relative_to(BASE)):sha(f) for f in inputs},scope='Actual full-precision Cable row impulse/dt, endpoint direction from previous accepted mapped Guide geometry (same delayed geometric contract already observed1831). Reconstructed endpoint wrench, NOT independent Native parent-J proof or hardware sensor. Uniform cylindrical shear is a nominal REQUIRED stress for0.5mm wire/1mm engaged length, not predicted retention or actual stress distribution. Requires real pull-out, bond, fatigue and material tests; no new physical capacity PASS.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='input_hashes'},indent=2))
if __name__=='__main__':main()
