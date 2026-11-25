"""Extend qualified outward single-Finger input to its existing full command, no new tuning."""
import argparse,collections,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from winch_transfer_assess import unique_row,read

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/winch_outward1886';root=ET.parse(src/'scene.scn').getroot()
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));metrics={};ok=process['exit_code']==0 and '[ERROR]'not in logs;valid=False
 if ok:
  rows=read(out/'skin.csv');assert len(rows)==240;tet=np.array(json.loads((BASE/'results/winch_finger1882/mesh.json').read_text())['tetrahedra']);q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);ratios=[float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows];contacts=collections.Counter((r['model0'],r['model1']) for r in read(out/'contact_provenance.csv') if float(r['lambda_Ns'])!=0);tendons=[];dt=float(root.get('dt'))
  for j in range(2):
   inp=[r for r in read(out/f'winch{j}_input_phases.csv') if r['phase']=='accepted_end'];output=[r for r in read(out/f'tendon{j}_phases.csv') if r['phase']=='accepted_end'];commands=read(out/f'winch{j}_commands.csv');ports=root.find(f"Node[@name='winch{j}']/Node[@name='ports']");origin=np.fromstring(ports.find('CableConstraint').get('pullPoint'),sep=' ');qinit=np.fromstring(ports.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(origin-qinit[0]);tensions=[];shortening=[];errors=[];outforces=[]
   for p,c,o in zip(inp,commands,output):
    row=unique_row(p['J'],0);lam=np.fromstring(p['lambda_Ns'],sep=' ');point=np.fromstring(p['q'],sep=' ').reshape(-1,3)[0];actual=L0-np.linalg.norm(origin-point);tensions.append(float(lam[row]/dt));shortening.append(float(actual));errors.append(abs(float(c['command_m'])-actual));outforces.append(float(lam[unique_row(o['J'])]/dt))
   tendons.append(dict(tendon=j,maximum_input_tension_N=max(tensions),maximum_output_tension_N=max(outforces),final_output_tension_N=outforces[-1],late_maximum_input_command_error_m=max(errors[220:]),final_input_shortening_m=shortening[-1],final_command_m=float(commands[-1]['command_m']),force_cap_samples=sum(t>=1.5-1e-9 for t in tensions)))
  last=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3);tip=int(q0[:,2].argmin());valid=min(ratios)>0;metrics=dict(saved_steps=240,minimum_saved_volume_ratio=min(ratios),final_minimum_z_reference_vertex_delta_m=(last[tip]-q0[tip]).tolist(),maximum_skin_final_nodal_displacement_m=float(np.linalg.norm(last-q0,axis=1).max()),tendons=tendons,contact_pairs=[dict(model_pair=list(k),nonzero_rows=v) for k,v in contacts.items()]);ok=valid and not contacts and all(t['maximum_input_tension_N']<=1.5+1e-12 and t['late_maximum_input_command_error_m']<=1e-6 for t in tendons)
 d=dict(status='PASS_FULL_SINGLE_FINGER_COMMAND_SCOPE_ONLY' if ok else 'FAIL_FULL_SINGLE_FINGER_CLOSING_GATE',process=process,metrics=metrics,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='Same outward mechanism/mass/material/constraint/dt and same input command/cap; only simulation duration extended. No object, Support or otherFinger. All old hardware and new rotor collisions retained. Initial/finite FEM and actual input/output forces checked; command/saturation and hidden hardware contact gate separate from execution validity. Not100g/wrapping/time/mesh/bearing/strength qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
