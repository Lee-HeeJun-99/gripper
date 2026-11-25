"""Join actual child/rigid cable rows with explicitly phase-matched lever arms."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from b3_cable_phase_pilot import parse

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);results=[]
 for case in a.cases:
  src=BASE/'results'/case;assessment=json.loads((src/'phase_assessment.json').read_text());assert assessment['purity_q_v_impulse_difference']==0 and assessment['maximum_previous_J_error']==0
  root=ET.parse(src/'scene.scn').getroot();node=root.find("Node[@name='guides0']");initial=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);c=node.find("Node[@name='cable0']");ids=np.fromstring(c.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);x=np.fromstring(c.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);local=Rotation.from_quat(initial[ids,3:]).inv().apply(x-initial[ids,:3]);rows=list(csv.DictReader((src/'phases.csv').open()));metrics=[]
  for k in range(assessment['actual_steps']):
   phases={r['phase']:r for r in rows if int(r['step'])==k};b=phases['build_end'];e=phases['accepted_end'];J,row=parse(b['J'],6,3);P,pr=parse(b['parent_J'],11,6);assert row==pr
   frame={n:np.fromstring(text,sep=' ').reshape(-1,7) for n,text in [('previous',b['parent_q']),('free',b['parent_free_q']),('accepted',e['parent_q'])]};vp=np.fromstring(e['parent_v'],sep=' ').reshape(-1,6);vc=np.fromstring(e['v'],sep=' ').reshape(-1,3);qc=np.fromstring(e['q'],sep=' ').reshape(-1,3)
   errors={};vel_errors={};position_errors={}
   for name,q in frame.items():
    arm=Rotation.from_quat(q[ids,3:]).apply(local);expected=np.zeros((11,6));np.add.at(expected[:,:3],ids,J);np.add.at(expected[:,3:],ids,np.cross(arm,J));errors[name]=float(abs(expected-P).max());vel_errors[name]=float(abs(vp[ids,:3]+np.cross(vp[ids,3:],arm)-vc).max());position_errors[name]=float(abs(q[ids,:3]+arm-qc).max())
   metrics.append(dict(step=k,parent_J_lever_error_by_geometry=errors,accepted_child_velocity_error_by_lever=vel_errors,accepted_child_position_error_by_geometry=position_errors,actual_parent_vs_child_row_rate_difference_m_s=float((P*vp).sum()-(J*vc).sum())))
  results.append(dict(case=case,original_phase_assessment_status=assessment['status'],steps=len(metrics),maximum_parent_J_error_by_geometry={n:max(m['parent_J_lever_error_by_geometry'][n] for m in metrics) for n in frame},maximum_child_velocity_error_by_lever={n:max(m['accepted_child_velocity_error_by_lever'][n] for m in metrics) for n in frame},maximum_child_position_error_by_geometry={n:max(m['accepted_child_position_error_by_geometry'][n] for m in metrics) for n in frame},maximum_parent_child_rate_difference_m_s=max(abs(m['actual_parent_vs_child_row_rate_difference_m_s']) for m in metrics),metrics=metrics,input_sha256={f:sha(src/f) for f in ('phases.csv','scene.scn','phase_assessment.json')}))
 d=dict(status='MEASURED_CHILD_PARENT_PHASE_CONTRACT_ONLY',results=results,source_sha256=sha(Path(__file__)),scope='Actual selected row, independent rigid cross-product pullback at each explicitly named geometry. Reports differences without assuming matching caches. No physical-state correction, work/global energy/contact or grasp qualification. Parent may be projectively reduced; a mismatch is not automatically a missing external load.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**d,'results':[{k:v for k,v in r.items() if k!='metrics'} for r in results]},indent=2))
if __name__=='__main__':main()
