"""Separate actual speed failure, vertical load and normal/tangential torques.
No causal claim from kinetic bookkeeping, no signal smoothing/floors.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from finite_contact_row_contract import audit

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);metrics=[]
 for case in ('dispatch_finite_holding1586','capillary_hold1700'):
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();dt=float(root.get('dt'));rr=list(csv.DictReader((src/'object.csv').open()));t=np.array([float(r['time_s']) for r in rr]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rr]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rr]);window=(t>=1.6-1e-12)&(t<=2+1e-12);ids=np.flatnonzero(window);peak=ids[np.linalg.norm(v[window,:3],axis=1).argmax()];previous=np.vstack([np.zeros((1,6)),v[:-1]]);mid=(v+previous)/2;index={x:i for i,x in enumerate(t)};parts={name:np.zeros((len(t),6)) for name in ('normal','tangent')};row_peak=0.
  for r in csv.DictReader((src/'response_rows.csv').open()):
   names=[r[k] for k in ('model0','model1')]
   if not any('/object/'in x for x in names) or not any('/skinCollision/'in x for x in names):continue
   component=(int(r['row_id'])-int(r['first_row']))%3;imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');k=index[float(r['time_s'])];parts['normal' if component==0 else 'tangent'][k]+=imp
   if window[k] and component==0:row_peak=max(row_peak,float(np.linalg.norm(imp[3:]))/dt)
  metrics.append(dict(case=case,peak_speed_time_s=float(t[peak]),velocity_at_peak_mm_s=(v[peak,:3]*1000).tolist(),maximum_speed_mm_s=float(np.linalg.norm(v[window,:3],axis=1).max()*1000),maximum_horizontal_speed_mm_s=float(np.linalg.norm(v[window,:2],axis=1).max()*1000),maximum_abs_vertical_speed_mm_s=float(abs(v[window,2]).max()*1000),maximum_angular_speed_rad_s=float(np.linalg.norm(v[window,3:],axis=1).max()),maximum_single_normal_row_torque_Nm=row_peak,hold_actual_normal_impulse_sum_Ns_Nms=parts['normal'][window].sum(0).tolist(),hold_actual_tangent_impulse_sum_Ns_Nms=parts['tangent'][window].sum(0).tolist(),normal_row_object_angular_midpoint_work_J=float((parts['normal'][window,3:]*mid[window,3:]).sum()),tangent_row_object_angular_midpoint_work_J=float((parts['tangent'][window,3:]*mid[window,3:]).sum()),input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv')}))
 current=audit('capillary_hold1700');reference=BASE/'results/finite_contact_rows1603/summary.json'
 # The original1603 folder name is discovered by its preserved producer, not regenerated.
 oldrefs=[f for f in (BASE/'results').glob('*1603/summary.json')];assert len(oldrefs)==1
 d=dict(status='ACTUAL_SPEED_AND_ROW_TORQUE_FAILURE_INVENTORY_ONLY',metrics=metrics,current_complete_Coulomb_contract=current,old_row_audit_sha256=sha(oldrefs[0]),scope='Normal rows of a radial sphere should have zero object torque. Nonzero measured angular work is object kinetic bookkeeping, NOT global stored energy/friction loss or a sole cause proof. Scalar gravity support near0.981N does not imply dynamic stability. Existing known frozen-normal/free-rotation defect remains; no arbitrary damping/force/mu/solver remedy inferred.',source_sha256=sha(Path(__file__)),dependency_sha256=sha(BASE/'sofa/finite_contact_row_contract.py'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
