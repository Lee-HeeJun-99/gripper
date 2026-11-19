"""Independent actual-state rigid guide attachment and cable tracking audit."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import rotation,cable_node
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text());tree=ET.parse(src/'scene.scn');result=dict(scope='saved-state guide attachment/actuation audit;NOT time/energy/grasp approval',case=a.case,source_sha256=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'scene.scn')},fingers=[])
 for f in range(m['fingers']):
  rows=read(src/f'finger{f}.csv');frames=read(src/f'guide_frames{f}.csv');q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);anchor=np.fromstring(tree.find(f"./Node[@name='guides{f}']/Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);initial=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);attachment=m['rigid_guides'][f]['attachment_nodes'];mapped=[]
  owners=np.fromstring(tree.find(f"./Node[@name='guides{f}']/Node[@name='anchors']/RigidMapping").get('rigidIndexPerPoint'),sep=' ',dtype=int)
  for k in range(len(rows)):
   mapped.append(np.array([rigid[k,owners[j],:3]+rotation(rigid[k,owners[j],3:])@(x-initial[owners[j],:3]) for j,x in enumerate(anchor)]))
  gap=float(np.max(np.abs(q[:,attachment]-np.array(mapped))));tracking=[];control=tree.find(f"./Node[@name='finger{f}']/NativeCableSequence");hold_end=float(control.get('hold','1'));closing=float(control.get('closing','.5'))
  for j in (0,1):
   cable=cable_node(tree,f,j);pull=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');rest=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(np.vstack([pull,rest]),axis=0),axis=1).sum();t=np.array([float(r['time_s']) for r in rows]);command=np.array([float(r['command_m']) for r in rows]);actual=np.array([L0-np.linalg.norm(np.diff(np.vstack([pull,np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]),axis=0),axis=1).sum() for r in rows]);force=np.array([float(r[f'cable{j}_force_raw'])/m['dt_s'] for r in rows]);hold=(t>=closing+.1)&(t<=hold_end+1e-12);dx=np.diff(np.r_[0.,actual]);dc=np.diff(np.r_[0.,command]);Favg=(np.r_[0.,force[:-1]]+force)/2;tracking.append(dict(cable=j,max_error_mm=float(np.max(abs(actual-command))*1000),max_hold_error_mm=float(np.max(abs(actual[hold]-command[hold]))*1000) if hold.any() else None,peak_force_N=float(force.max()),sampled_actual_path_work_J=float(np.sum(Favg*dx)),sampled_command_work_J=float(np.sum(Favg*dc)),work_scope='sampled trapezoid proxy,NOT stage-consistent or whole energy identity'))
  result['fingers'].append(dict(max_attachment_component_error_m=gap,attachment_api_status='PASS' if gap<=1e-12 else 'FAIL',quaternion_norm_error=float(np.max(abs(np.linalg.norm(rigid[:,:,3:],axis=2)-1))),tracking=tracking))
 solver=read(src/'constraints.csv');result['solver']=dict(maximum_reported_error=max(float(x['error']) for x in solver),max_iterations=max(int(x['iterations']) for x in solver));(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
