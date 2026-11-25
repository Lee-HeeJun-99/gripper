"""Matched input-only contrast and real tendon provenance for new supported-winch Finger."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',default='winch_finger1882');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results'/a.source;root=ET.parse(src/'scene.scn').getroot()
 for e in root.findall('NativeCableSequence'):e.set('stroke','0')
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));d0=det(q0);process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',out/'scene.scn'],out/'process',120);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));metrics={};ok=process['exit_code']==0 and '[ERROR]'not in logs
 if ok:
  control=read(out/'skin.csv');active=read(src/'skin.csv');assert len(control)==len(active)==100;qc=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in control]);qa=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in active]);ratio=min(float((det(q)/d0).min()) for q in qc);tip=int(q0[:,2].argmin());delta=qa[-1,tip]-qc[-1,tip];gap=float(np.linalg.norm(qa-qc,axis=2).max());dt=float(root.get('dt'));tendons=[];forces=read(src/'constraints.csv');output_sets=[set() for _ in active]
  for j in range(2):
   phase=[r for r in read(src/f'tendon{j}_phases.csv') if r['phase']=='accepted_end'];assert len(phase)==100;point0=np.fromstring(root.find(f"Node[@name='fingerTendon{j}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);initialL=float(np.linalg.norm(np.diff(point0,axis=0),axis=1).sum());tension=[];length_errors=[];rowids=[]
   for k,r in enumerate(phase):
    rows={int(p.split(':')[0]) for p in r['J'].split(';') if p};assert len(rows)==1;row=next(iter(rows));output_sets[k].add(row);lam=np.fromstring(r['lambda_Ns'],sep=' ');q=np.fromstring(r['q'],sep=' ').reshape(-1,3);tension.append(float(lam[row]/dt));length_errors.append(abs(float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum())-initialL));rowids.append(row)
   tendons.append(dict(tendon=j,actual_row_ids=sorted(set(rowids)),maximum_tension_N=max(tension),final_tension_N=tension[-1],minimum_tension_N=min(tension),maximum_geometric_length_error_m=max(length_errors)))
  input_force=[];row_counts=[]
  for k,r in enumerate(forces):
   lam=np.fromstring(r['impulses_Ns'],sep=' ');row_counts.append(len(lam));assert len(lam)==4,'Unexpected non-cable rows require separate attribution';ids=set(range(4))-output_sets[k];assert len(ids)==2;input_force.extend(float(lam[i]/dt) for i in ids)
  input_errors=[]
  for j in range(2):
   ports=read(src/f'winch{j}_ports.csv');commands=read(src/f'winch{j}_commands.csv');assert len(ports)==len(commands)==100;winch=root.find(f"Node[@name='winch{j}']/Node[@name='ports']");pull=np.fromstring(winch.find('CableConstraint').get('pullPoint'),sep=' ');initial=np.fromstring(winch.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)[0];L0=np.linalg.norm(pull-initial);input_errors.append(max(abs((L0-np.linalg.norm(pull-np.fromstring(r['q'],sep=' ').reshape(-1,3)[0]))-float(c['command_m'])) for r,c in zip(ports,commands)))
  metrics=dict(control_minimum_saved_volume_ratio=ratio,maximum_active_control_nodal_difference_m=gap,reference_minimum_z_vertex_id=tip,reference_vertex_active_minus_control_m=delta.tolist(),maximum_input_tension_N=max(input_force),minimum_input_tension_N=min(input_force),maximum_input_geometric_command_error_m=max(input_errors),tendons=tendons,native_constraint_row_counts=sorted(set(row_counts)));ok=ratio>0 and gap>1e-6 and delta[0]<0 and max(input_force)<=1.5+1e-12 and min(input_force)>=-1e-12
 d=dict(status='PASS_INCREMENTAL_SINGLE_FINGER_INWARD_ACTUATION_ONLY' if ok else 'FAIL_INCREMENTAL_SINGLE_FINGER_ACTUATION',process=process,metrics=metrics,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='Matched zero-stroke new-mechanism control, all other mass/fixture/geometry/material/dt unchanged. Native C2 rest-length constraint remains: control is NOT slack/force-free gravity reference. Active output rows attributed from actual child J; exactly4actual Cable rows, other2are bounded inputs. Actual Skin incremental displacement, no object/Support/100g test, no complete wrapping/curvature/energy/time/mesh/material qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
