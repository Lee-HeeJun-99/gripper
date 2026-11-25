"""Read-only recovery of1917postprocessor failure; never reruns Native."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from winch_transfer_assess import read,unique_row

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/brake_finger1917';process=json.loads((src/'process/result.json').read_text());assert process['exit_code']==0;assert '[ERROR]'not in (src/'process/stdout.log').read_text();root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));rows=read(src/'skin.csv');assert len(rows)==240;tet=np.array(json.loads((BASE/'results/winch_finger1882/mesh.json').read_text())['tetrahedra']);q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);quality=min(float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows);contacts=[r for r in read(src/'contact_provenance.csv') if float(r['lambda_Ns'])!=0];records=[]
 for j in range(2):
  phases=[r for r in read(src/f'winch{j}_input_phases.csv') if r['phase']=='accepted_end'];commands=read(src/f'winch{j}_commands.csv');ports=root.find(f"Node[@name='winch{j}']/Node[@name='ports']");pull=np.fromstring(ports.find('CableConstraint').get('pullPoint'),sep=' ');point0=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[0];L0=np.linalg.norm(point0-pull);forces=[];errors=[]
  for r,cmd in zip(phases,commands):
   forces.append(float(np.fromstring(r['lambda_Ns'],sep=' ')[unique_row(r['J'],0)]/dt));point=np.fromstring(r['q'],sep=' ').reshape(-1,3)[0];errors.append(float(abs(L0-np.linalg.norm(point-pull)-float(cmd['command_m']))))
  records.append(dict(tendon=j,maximum_input_N=max(forces),force_cap_samples=int(sum(f>=1.5-1e-9 for f in forces)),late_stroke_error_m=max(errors[-20:])))
 ok=quality>0 and not contacts and all(r['maximum_input_N']<=1.5+1e-12 and r['late_stroke_error_m']<=1e-6 for r in records);d=dict(status='PASS_LOCAL_BRAKE_SINGLE_CLOSING_ONLY' if ok else 'REJECT_ALWAYS_ON_BRAKE_CLOSING',source_case=src.name,process=process,minimum_saved_volume_ratio=quality,nonzero_contact_rows=len(contacts),tendons=records,source_sha256=sha(Path(__file__)),input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'producer.py',src/'preflight.json',src/'scene.scn',src/'process/result.json',src/'skin.csv',src/'contact_provenance.csv']},scope='Actual completed1917Raw only; original postprocessing failed serializing numpy.int64, no Native rerun. Same1um closing gate, no force/dt/parameter change. Actuator-loss assumption, NOT actual motor data or100g PASS.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='input_hashes'},indent=2))
if __name__=='__main__':main()
