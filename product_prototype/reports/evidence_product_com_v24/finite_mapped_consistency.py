"""Read actual Native mapped geometry,not only parent rigid reconstruction."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
from closest_geometry import closest
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='b3_finite_mapped552');p.add_argument('--reference',default='b3_finite_compound550');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());shape,_=eyelet(cfg,meta['geometry']['segments']);records=[];purity=0.;q_error=0.;v_error=0.;active_point_error=0.
 for alarm in ('1','5'):
  states=[read(src/alarm/f'guide{i}.csv') for i in (0,1)];direct=[read(src/alarm/f'direct{i}.csv') for i in (0,1)];response=read(src/alarm/'response0.csv')
  for i in (0,1):
   reference=read(BASE/'results'/a.reference/alarm/f'guide{i}.csv');assert len(reference)==len(states[i])
   for x,y in zip(states[i],reference):
    for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(vec(x[key])-vec(y[key])))))
   for part in ('eyelet','support'):
    mapped=read(src/alarm/f'mapped{i}_{part}.csv');assert len(mapped)==len(states[i]);model=meta['models'][i];local=np.array(model['body_local_vertices_m'] if part=='eyelet' else model['support_body_local_vertices_m']);faces=shape.faces if part=='eyelet' else np.array(model['support_faces']);initial=np.array(model['vertices_m'] if part=='eyelet' else model['support_vertices_m'])
    for k,(s,child) in enumerate(zip(states[i],mapped)):
     t=float(s['time_s']);assert t==float(child['time_s']);q=vec(s['rigid_q']);v=vec(s['rigid_v']);offset=local@rotation(q[3:]).T;actual=vec(child['q']).reshape(-1,3);actual_v=vec(child['v']).reshape(-1,3);qe=float(np.max(abs(actual-offset-q[:3])));ve=float(np.max(abs(actual_v-v[:3]-np.cross(v[3:],offset))));q_error=max(q_error,qe);v_error=max(v_error,ve);oldq=np.array(meta['initial_rigid_q'][i]) if k==0 else vec(states[i][k-1]['rigid_q']);previous=initial if k==0 else vec(mapped[k-1]['q']).reshape(-1,3);current_rows={int(r['row_id']):r for r in direct[i] if float(r['time_s'])==t};blocks=sorted({int(r['first_row']) for r in response if float(r['time_s'])==t});points=[]
     for b in blocks:
      provenance=next(r for r in response if float(r['time_s'])==t and int(r['first_row'])==b);this=provenance['model0'] if f'/guide{i}/' in provenance['model0'] else provenance['model1'];correct_part='support' if '/supportCollision/' in this else 'eyelet'
      if correct_part!=part:continue
      J=np.array([vec(current_rows[b+j]['J']) for j in range(3)]);lever=.5*sum((np.cross(x[:3],x[3:]) for x in J),np.zeros(3));point=oldq[:3]+lever;tri=previous[faces];near=closest(tri,np.repeat(point[None,:],len(tri),axis=0));distance=float(np.linalg.norm(near-point,axis=1).min());lam=float(current_rows[b]['lambda_Ns']);points.append(dict(first_row=b,normal_impulse_Ns=lam,point_distance_to_ACTUAL_previous_mapped_mesh_m=distance,model0=provenance['model0'],model1=provenance['model1']))
      if lam>0:active_point_error=max(active_point_error,distance)
     records.append(dict(alarm_mm=int(alarm),body=i,part=part,time_s=t,parent_to_actual_child_position_error_m=qe,parent_to_actual_child_velocity_error_m_s=ve,contact_points=points))
 result=dict(status='MAPPED_NATIVE_STATE_DIAGNOSTIC_ONLY',source_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),scope='Actual public parent/child API and actual previous mapped triangles. No map.apply correction or state edits. Nonzero force points retained;not discarded or clamped.',strict_API_gate=1e-12,observer_state_error=purity,observer_state_pass=purity<=1e-12,parent_child_position_max_error_m=q_error,parent_child_velocity_max_error_m_s=v_error,parent_child_API_pass=q_error<=1e-12 and v_error<=1e-12,maximum_ACTIVE_point_distance_to_actual_mapped_mesh_m=active_point_error,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
