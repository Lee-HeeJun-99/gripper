"""Actual release/free fall and residual shape;NOT full Recovery certification."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
def read(path):return list(csv.DictReader(path.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;old=BASE/'results/b3_lift50_explore1077';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('complete run required')
 rows=read(src/'object.csv');t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);late=t>=2.8-1e-12;index={x:k for k,x in enumerate(t)};forces={name:np.zeros((len(t),3)) for name in ('skin','rail','guide','support','other')};last={}
 for r in csv.DictReader((src/'response_rows.csv').open()):
  pair=[r['model0'],r['model1']]
  if not any('/object/' in x for x in pair):continue
  other=next(x for x in pair if '/object/' not in x);name='skin' if '/skinCollision/' in other else 'rail' if '/railCollision/' in other else 'guide' if '/guides' in other else 'support' if '/floor/' in other else 'other';imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3];time=float(r['time_s']);forces[name][index[time]]+=imp/meta['dt_s']
  if np.linalg.norm(imp)>0:last[name]=time
 mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);tip=local[:,0]==100;tree=ET.parse(src/'scene.scn');records=[];prefix=0
 for f in range(3):
  actual=read(src/f'finger{f}.csv');previous=read(old/f'finger{f}.csv')
  for r,s in zip(actual,previous):
   for field in ('q_m','v_m_s','guide0_q_m','guide1_q_m'):prefix=max(prefix,float(abs(np.fromstring(r[field],sep=' ')-np.fromstring(s[field],sep=' ')).max()))
  final=np.fromstring(actual[-1]['q_m'],sep=' ').reshape(-1,3);speed=np.fromstring(actual[-1]['v_m_s'],sep=' ').reshape(-1,3);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);translated=rest+np.array([0,0,.005])
  records.append(dict(finger=f,final_tendon_command_N=float(actual[-1]['command_N']),final_width_mean_tip_residual_mm=float(np.linalg.norm((final-translated)[tip].mean(axis=0))*1000),final_maximum_shape_residual_mm=float(np.linalg.norm(final-translated,axis=1).max()*1000),final_maximum_node_speed_mm_s=float(np.linalg.norm(speed,axis=1).max()*1000),reference='stress-free manufactured geometry translated with Root,NOT independently validated gravity equilibrium'))
 lateforces={name:float(np.linalg.norm(value[late],axis=1).max()) for name,value in forces.items()};late_ids=np.flatnonzero(late);dv=np.diff(v[late,:3],axis=0);ballistic=float(abs(dv-np.array([0,0,-9.81])*meta['dt_s']).max());reference=int(np.argmin(abs(t-2.0)))
 d=dict(status='RELEASE_OBSERVED_FULL_RECOVERY_NOT_QUALIFIED' if all(x==0 for x in lateforces.values()) and q[-1,2]<q[reference,2] else 'RELEASE_REVIEW',object_drop_after2s_mm=float((q[reference,2]-q[-1,2])*1000),last_nonzero_object_contact_s=last,late_maximum_contact_resultants_N=lateforces,late_velocity_gravity_step_error_m_s=ballistic,first800_finger_guide_state_prefix_vs1077_error=prefix,prefix_API_1e12_pass=prefix<=1e-12,records=records,full_recovery='NOT QUALIFIED_GRAVITY_EQUILIBRIUM_REFERENCE_MISSING',physical_validation='NOT QUALIFIED',scope='Observed actual Native object separation/gravity motion and shape residuals,not pressure,energy,fatigue,repeat-cycle or hardware Recovery certification.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'summary.json',src/'object.csv',src/'response_rows.csv',old/'summary.json',Path(__file__)]})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
