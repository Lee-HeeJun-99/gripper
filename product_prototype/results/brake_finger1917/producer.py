"""One actuator-loss assumption on actual registered single Finger, no sweep."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from winch_transfer_assess import unique_row,read

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/registered_winch_full1892';brake=BASE/'results/winch_brake1916';contract=json.loads((brake/'summary.json').read_text());assert contract['status']=='PASS_NATIVE_MAPPED_ROTOR_VISCOUS_CONTRACT_ONLY';c=json.loads((brake/'preflight.json').read_text())['coefficient_Nms_per_rad'];out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());root=ET.parse(src/'scene.scn').getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
 for j in range(2):ET.SubElement(root.find(f"Node[@name='winch{j}']/Node[@name='body3']"),'UniformVelocityDampingForceField',template='Rigid3d',name='motorViscousLoss',dampingCoefficient=str(c),implicit='1')
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),base_scene_sha256=sha(src/'scene.scn'),brake_contract_sha256=sha(brake/'summary.json'),scene_sha256=sha(out/'scene.scn'),coefficient_Nms_per_rad=c,changed_variable='Only constant local rotor viscous loss, always active. Same actualSkin/Rail/Guide/geometries/allcollisions/Cable1.5Ncap/dt/closing profile. Coefficient is research actuator torque-loss assumption, not measured friction or global damping fit.',binary_sha256={e.get('pluginName'):sha(Path(e.get('pluginName'))) for e in root.iter('RequiredPlugin') if e.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ['stdout.log','stderr.log']);metrics={};ok=proc['exit_code']==0 and '[ERROR]'not in logs
 if ok:
  rows=read(out/'skin.csv');assert len(rows)==240;tet=np.array(json.loads((BASE/'results/winch_finger1882/mesh.json').read_text())['tetrahedra']);q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);quality=min(float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows);contacts=[r for r in read(out/'contact_provenance.csv') if float(r['lambda_Ns'])!=0];records=[];dt=float(root.get('dt'))
  for j in range(2):
   phases=[r for r in read(out/f'winch{j}_input_phases.csv') if r['phase']=='accepted_end'];commands=read(out/f'winch{j}_commands.csv');ports=root.find(f"Node[@name='winch{j}']/Node[@name='ports']");pull=np.fromstring(ports.find('CableConstraint').get('pullPoint'),sep=' ');q=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(q[0]-pull);forces=[];errors=[]
   for r,cmd in zip(phases,commands):
    force=np.fromstring(r['lambda_Ns'],sep=' ')[unique_row(r['J'],0)]/dt;forces.append(force);point=np.fromstring(r['q'],sep=' ').reshape(-1,3)[0];errors.append(abs(L0-np.linalg.norm(point-pull)-float(cmd['command_m'])))
   records.append(dict(tendon=j,maximum_input_N=float(max(forces)),force_cap_samples=sum(f>=1.5-1e-9 for f in forces),late_stroke_error_m=float(max(errors[-20:]))))
  metrics=dict(minimum_saved_volume_ratio=quality,nonzero_contact_rows=len(contacts),tendons=records);ok=quality>0 and not contacts and all(r['maximum_input_N']<=1.5+1e-12 and r['late_stroke_error_m']<=1e-6 for r in records)
 d=dict(status='PASS_LOCAL_BRAKE_SINGLE_CLOSING_ONLY' if ok else 'REJECT_ALWAYS_ON_BRAKE_CLOSING',process=proc,metrics=metrics,preflight_sha256=sha(out/'preflight.json'),source_sha256=sha(Path(__file__)),scope='Actual single no-object Native closing with one local actuator-loss assumption. Unchanged1um tracking/FEM/contact/force cap gates. NOT physical motor data,100gHolding, switched brake or physical/numerical qualification. Failed candidate must not escalate full grasp or force increase.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
