"""Actual mapped B3 cable phase observation, unchanged physical prefix."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_hardware_grasp_pilot import run_three
from cable_phase_coupon import jac

def read(p):return list(csv.DictReader(p.open()))
def parse(text,n,width):
 out=np.zeros((n,width));ids=set()
 for part in text.split(';'):
  if part:
   row,col,value=part.split(':');ids.add(int(row));out[int(col)]=np.fromstring(value,sep=' ')
 assert len(ids)==1;return out,next(iter(ids))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=(.01,.25,.6),default=.01);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 src=BASE/'results/yoke_hold_diagnostic1741';root=ET.parse(src/'scene.scn').getroot();pre=json.loads((src/'preflight.json').read_text());binary=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so'
 compiled=BASE/'results/b3_cable_typed1831';meta=json.loads((compiled/'phase_assessment.json').read_text())
 assert sha(binary)==meta['binary_sha256'] and sha(BASE/'sofa/native_cable_phase/Observer.cpp')==sha(compiled/'Observer.cpp'),'frozen compiled observer identity mismatch'
 ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));ET.SubElement(root,'NativeCablePhase',body='@guides0/cable0/points',rigidBody='@guides0/frames',solver='@constraints',cable='@guides0/cable0/actuator',filename=str(out/'phases.csv'))
 origin=np.fromstring(root.find("Node[@name='guides0']/Node[@name='cable0']/CableConstraint").get('pullPoint'),sep=' ')
 for e in root.iter():
  for k,v in list(e.attrib.items()):e.set(k,v.replace(str(src),str(out)))
 steps=round(a.duration/.0025);run_three(root,out,src,pre['eyelet'],pre['parts'],steps,a.duration,87.2*a.duration/.6);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'Observer.cpp').write_bytes((BASE/'sofa/native_cable_phase/Observer.cpp').read_bytes())
 purity=0.
 for name,fields in [('object.csv',('rigid_q','rigid_v','object_impulse_Ns_Nms'))]+[(f'guide_frames{i}.csv',('rigid_q','rigid_v')) for i in range(3)]+[(f'finger{i}.csv',('q_m','v_m_s')) for i in range(3)]:
  old=read(src/name);new=read(out/name);assert len(new)==steps
  for x,y in zip(old,new):
   assert float(x['time_s'])==float(y['time_s'])
   for key in fields:purity=max(purity,float(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')).max()))
 rows=read(out/'phases.csv');metrics=[];finger=read(out/'finger0.csv')
 for k in range(steps):
  d={r['phase']:r for r in rows if int(r['step'])==k};assert set(d)=={'build_end','solve_end','accepted_end'};b,s,e=(d[n] for n in ('build_end','solve_end','accepted_end'))
  q=np.fromstring(b['q'],sep=' ').reshape(-1,3);fq=np.fromstring(b['free_q'],sep=' ').reshape(-1,3);qe=np.fromstring(e['q'],sep=' ').reshape(-1,3);ve=np.fromstring(e['v'],sep=' ').reshape(-1,3)
  J,row=parse(b['J'],len(q),3);P,rp=parse(b['parent_J'],11,6);assert rp==row;lam=np.fromstring(s['lambda_Ns'],sep=' ')[row];pv=np.fromstring(e['parent_v'],sep=' ').reshape(-1,6)
  metrics.append(dict(step=k,previous_J_error=float(abs(J-jac(q,origin)).max()),free_J_difference=float(abs(J-jac(fq,origin)).max()),accepted_J_difference=float(abs(J-jac(qe,origin)).max()),actual_impulse_Ns=float(lam),force_command_impulse_error_Ns=abs(float(lam)-float(finger[k]['command_Ns'])),accepted_force_data_error_Ns=abs(float(lam)-float(e['cable_force_raw'])),accepted_child_frozen_row_product_W=float(lam/.0025*(J*ve).sum()),accepted_parent_frozen_row_product_W=float(lam/.0025*(P*pv).sum()),accepted_geometric_rate_m_s=float(-(jac(qe,origin)*ve).sum())))
 ok=purity==0 and all(max(m['previous_J_error'],m['force_command_impulse_error_Ns'],m['accepted_force_data_error_Ns'])<=1e-12 for m in metrics)
 result=dict(status='PASS_PURE_B3_CHILD_ROW_PHASE_PREFIX' if ok else 'FAIL_B3_ROW_PHASE_OR_PURITY',actual_steps=steps,actual_duration_s=a.duration,purity_q_v_impulse_difference=purity,maximum_previous_J_error=max(m['previous_J_error'] for m in metrics),maximum_free_J_difference=max(m['free_J_difference'] for m in metrics),maximum_accepted_J_difference=max(m['accepted_J_difference'] for m in metrics),maximum_child_parent_accepted_row_product_difference_W=max(abs(m['accepted_child_frozen_row_product_W']-m['accepted_parent_frozen_row_product_W']) for m in metrics),metrics=metrics,source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),observer_source_sha256=sha(BASE/'sofa/native_cable_phase/Observer.cpp'),scope='Actual1741 physical inputs unchanged; read-only phase observation. Parent selected row can be projectively reduced; child/parent accepted row products are diagnostics, not integrated actuator work/global energy. No passive feedback or improved grasp claimed.')
 (out/'phase_assessment.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='metrics'},indent=2))
if __name__=='__main__':main()
