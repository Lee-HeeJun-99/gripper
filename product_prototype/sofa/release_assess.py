"""Full native hold/unload separation/recovery inventory,not a numerical PASS."""
import argparse,csv,json,xml.etree.ElementTree as ET,hashlib
import numpy as np
import trimesh
from mechanism_candidates import BASE
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());mesh=json.loads((src/'mesh.json').read_text());tree=ET.parse(src/'scene.scn');obj=read(src/'object.csv');t=np.array([float(r['time_s']) for r in obj]);index={x:k for k,x in enumerate(t)};qobj=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in obj]);R=cfg['simulation']['sphere_radius_mm']*.001;skin=np.zeros(len(t));guide=np.zeros_like(skin);support=np.zeros_like(skin);last=(t>=2.9-1e-12)&(t<=3.+1e-12)
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED' or t[-1]<3-1e-12:raise ValueError('completed3s actual sequence required')
 for row in read(src/'response_rows.csv'):
  if not any('/object/' in row[k] for k in ('model0','model1')):continue
  value=np.linalg.norm(np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')[:3])/m['dt_s'];k=index[float(row['time_s'])]
  if any('/skinCollision/' in row[x] for x in ('model0','model1')):skin[k]+=value
  elif any('/guides' in row[x] for x in ('model0','model1')):guide[k]+=value
  elif any('/floor/' in row[x] for x in ('model0','model1')):support[k]+=value
 local=np.array(mesh['local_positions_mm']);faces=np.array(mesh['triangles']);faces=faces[np.all(local[faces,2]>=0,axis=1)];records=[];mingap=1e9
 for f in range(m['fingers']):
  rows=read(src/f'finger{f}.csv');q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);v=np.array([np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);tip=local[:,0]==100;cp=trimesh.triangles.closest_point(q[-1,faces],np.repeat(qobj[-1,None,:3],len(faces),axis=0));gap=float(np.linalg.norm(cp-qobj[-1,:3],axis=1).min()-R);mingap=min(mingap,gap);records.append(dict(finger=f,final_command_m=rows[-1]['command_m'],final_actual_cable_force_N=[float(rows[-1][f'cable{j}_force_raw'])/m['dt_s'] for j in (0,1)],final_tip_reference_error_mm=float(np.linalg.norm(q[-1,tip].mean(axis=0)-rest[tip].mean(axis=0))*1000),final_rms_reference_error_mm=float(np.sqrt(np.mean((q[-1]-rest)**2))*1000),final_nodal_speed_max_mm_s=float(np.linalg.norm(v[-1],axis=1).max()*1000),final_skin_object_gap_mm=gap*1000))
 selected=np.flatnonzero((t>=2)&(skin>0));result=dict(status='RELEASE_INVENTORY_NOT_QUALIFIED_RESULT',case=a.case,scope='actual gravity-driven support withdrawal,unload and separation;not lift,time/mesh/whole energy or complete recovery certification',final_time_s=float(t[-1]),last_nonzero_skin_contact_time_after_2s=float(t[selected[-1]]) if len(selected) else None,last_window_max_skin_row_force_norm_sum_N=float(skin[last].max()),last_window_max_guide_object_force_norm_sum_N=float(guide[last].max()),last_window_support_force_norm_sum_range_N=[float(support[last].min()),float(support[last].max())],final_minimum_skin_object_gap_mm=mingap*1000,late_contact_separation_observed=bool(skin[last].max()==0 and guide[last].max()==0 and mingap>=cfg['simulation']['contact_distance_mm']*.001),final_object_vertical_change_from_initial_mm=float((qobj[-1,2]-cfg['simulation']['sphere_center_mm'][2]*.001)*1000),fingers=records,recovery='NOT QUALIFIED:reference is manufactured rest;gravity remains applied and zero-input gravity equilibrium unmeasured',source_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest(),input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src/'summary.json',src/'response_rows.csv',src/'object.csv')})
 post=t>=2-1e-12
 result['maximum_post_hold_support_row_force_norm_sum_N']=float(support[post].max())
 result['maximum_post_hold_guide_object_force_norm_sum_N']=float(guide[post].max())
 result['functional_contact_release']='OBSERVED_SEPARATION_NOT_PHYSICS_CERTIFIED' if result['late_contact_separation_observed'] else 'FAIL_CONTACT_SEPARATION'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
