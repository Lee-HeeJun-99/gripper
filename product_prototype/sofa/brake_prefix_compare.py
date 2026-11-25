"""Actual pre-engagement state purity and configured passive-port loss only."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;old=BASE/'results/crimp_hold1904';meta=json.loads((src/'summary.json').read_text());assert meta['process']['exit_code']==0;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));paths=[src/'scene.scn',src/'summary.json'];read=lambda f:list(csv.DictReader(f.open()));errors=[]
 for name,fields in [('object.csv',['rigid_q','rigid_v','object_impulse_Ns_Nms'])]+[(f'skin{i}.csv',['q','v']) for i in range(3)]:
  active=read(src/name);baseline=read(old/name);assert len(active)>=200;assert len(baseline)>=200;err=max(float(abs(np.fromstring(active[k][f],sep=' ')-np.fromstring(baseline[k][f],sep=' ')).max()) for k in range(200) for f in fields);errors.append(dict(file=name,maximum_numeric_prefix_error=err));paths.extend([src/name,old/name])
 losses=[]
 for i in range(3):
  for j in range(2):
   name=f'drive_{i}_{j}';drive=root.find(f"Node[@name='{name}']");frame=np.fromstring(drive.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)[2,:3];point=np.fromstring(drive.find("Node[@name='ports']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)[0];radius=np.linalg.norm((point-frame)[1:]);phasefile=src/f'{name}_phases.csv';schedulefile=src/f'{name}_brake_schedule.csv';phases=[r for r in read(phasefile) if r['phase']=='accepted_end'];schedule=read(schedulefile);assert len(phases)==len(schedule);loss=0.;torque=[]
   for row,cr in zip(phases,schedule):
    c=float(cr['coefficient']);assert c>=0;omega=np.linalg.norm(np.fromstring(row['v'],sep=' ').reshape(-1,3)[0])/radius;loss+=dt*c*omega**2;torque.append(c*omega)
   losses.append(dict(finger=i,tendon=j,reconstructed_configured_viscous_loss_J=float(loss),maximum_reconstructed_torque_Nm=float(max(torque))));paths.extend([phasefile,schedulefile])
 ok=max(r['maximum_numeric_prefix_error'] for r in errors)<=1e-12 and all(r['maximum_reconstructed_torque_Nm']<=.015+1e-12 and r['reconstructed_configured_viscous_loss_J']>=0 for r in losses);d=dict(status='PASS_PREBRAKE_STATE_PURITY_AND_CONFIGURED_LOSS_ONLY' if ok else 'FAIL_PREBRAKE_PURITY_OR_LOSS_BUDGET',case=a.case,prefix_samples=200,prefix_end_s=.5,errors=errors,passive_ports=losses,total_reconstructed_loss_J=sum(r['reconstructed_configured_viscous_loss_J'] for r in losses),source_sha256=sha(Path(__file__)),input_hashes={str(f.relative_to(BASE)):sha(f) for f in paths},scope='Actual unbraked1904 versus new candidate before engagement; Native object/Skin q/v/impulse purity. Loss is reconstructed configured viscous model backward-Euler endpoint quadrature on ideal principal-axis rotor, not hardware calorimetry, actual force-array API or whole gripper energy. No physical/material/time/mesh PASS.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='input_hashes'},indent=2))
if __name__=='__main__':main()
