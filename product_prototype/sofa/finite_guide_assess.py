"""Saved finite-eyelet surface/contact pullback audit;NOT swept clearance."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
def read(p):return list(csv.DictReader(p.open()))
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());mesh,geometry=eyelet(cfg,meta['geometry']['segments']);faces=mesh.faces;records=[]
 for alarm in ('1','5'):
  d=src/alarm;states=[read(d/f'guide{i}.csv') for i in (0,1)];direct=[read(d/f'direct{i}.csv') for i in (0,1)];response=read(d/'response0.csv');detector=read(d/'detector.csv');M=[np.array(json.loads((d/f'guide{i}.csv.mass.json').read_text())['elements'][0]['matrix']) for i in (0,1)];local=[np.array(m['body_local_vertices_m']) for m in meta['models']]
  for mass in M:
   if not np.array_equal(mass,np.diag(np.diag(mass))) or not np.all(np.diag(mass)[3:]==mass[3,3]):raise ValueError('isotropic mass only')
  for k,s in enumerate(states[0]):
   t=float(s['time_s']);oldq=[np.array(meta['initial_rigid_q'][i]) if k==0 else vec(states[i][k-1]['rigid_q']) for i in (0,1)];oldv=[np.array(meta['initial_rigid_v'][i]) if k==0 else vec(states[i][k-1]['rigid_v']) for i in (0,1)];newq=[vec(states[i][k]['rigid_q']) for i in (0,1)];newv=[vec(states[i][k]['rigid_v']) for i in (0,1)];imp=[vec(states[i][k]['object_impulse_Ns_Nms']) for i in (0,1)]
   rows=[{int(r['row_id']):r for r in data if float(r['time_s'])==t} for data in direct];blocks=sorted({int(r['first_row']) for r in response if float(r['time_s'])==t});pullback=[];reconstruction=0.;momentum=0.
   for i in (0,1):
    total=sum((vec(r['J'])*float(r['lambda_Ns']) for r in rows[i].values()),np.zeros(6));reconstruction=max(reconstruction,float(np.max(abs(total-imp[i]))));momentum=max(momentum,float(np.max(abs(M[i]@(newv[i]-oldv[i])-imp[i]))))
   for b in blocks:
    for i in (0,1):
     ids=[b+j for j in range(3)]
     if any(idx not in rows[i] for idx in ids):raise ValueError('incomplete actual friction block')
     j=np.array([vec(rows[i][idx]['J']) for idx in ids]);lever=.5*sum((np.cross(x[:3],x[3:]) for x in j),np.zeros(3));point=oldq[i][:3]+lever;distances={}
     for label,qstage in [('previous',oldq[i]),('free_predictor',vec(rows[i][b]['free_q'])),('accepted',newq[i])]:
      stagepoint=qstage[:3]+lever;verts=local[i]@rotation(qstage[3:]).T+qstage[:3];tri=verts[faces];closest=trimesh.triangles.closest_point(tri,np.repeat(stagepoint[None,:],len(tri),axis=0));distances[label]=float(np.linalg.norm(closest-stagepoint,axis=1).min())
     provenance=next(r for r in response if float(r['time_s'])==t and int(r['first_row'])==b);same=[r for r in detector if float(r['accepted_time_s'])==t and r['model0']==provenance['model0'] and r['model1']==provenance['model1']];key='detected_point0' if f'/guide{i}/' in provenance['model0'] else 'detected_point1';deterror=min((np.linalg.norm(vec(r[key])-point) for r in same),default=None)
     pullback.append(dict(body=i,first_row=b,normal_impulse_Ns=float(rows[i][b]['lambda_Ns']),point_using_previous_origin_m=point.tolist(),model0=provenance['model0'],model1=provenance['model1'],nearest_same_response_detector_point_error_m=None if deterror is None else float(deterror),surface_distances_by_explicit_stage_m=distances,lever_fit_error_m=float(max(np.linalg.norm(np.cross(lever,x[:3])-x[3:]) for x in j))))
   def angular(q,v):return sum((np.cross(x[:3],m[:3,:3]@y[:3])+m[3:,3:]@y[3:] for x,y,m in zip(q,v,M)),np.zeros(3))
   delta=angular(newq,newv)-angular(oldq,oldv);couple=sum((np.cross(q[:3],f[:3])+f[3:] for q,f in zip(oldq,imp)),np.zeros(3));advection=sum((np.cross(q[:3]-r[:3],m[:3,:3]@v[:3]) for q,r,m,v in zip(newq,oldq,M,newv)),np.zeros(3))
   # Vertex containment is a lower-cost signed diagnostic,NOT complete surface CCD.
   vertices=[local[i]@rotation(newq[i][3:]).T+newq[i][:3] for i in (0,1)];inside=[]
   for i in (0,1):
    other=1-i
    tri=vertices[other][faces];distances=[]
    for point in vertices[i]:distances.append(float(np.linalg.norm(trimesh.triangles.closest_point(tri,np.repeat(point[None,:],len(tri),axis=0))-point,axis=1).min()))
    inside.append(min(distances))
   records.append(dict(alarm_mm=int(alarm),time_s=t,contact_blocks=len(blocks),contact_rows=len(rows[0]),row_impulse_reconstruction_error_Ns_Nms=reconstruction,mass_velocity_impulse_error_Ns_Nms=momentum,net_internal_angular_impulse_Nms=couple.tolist(),angular_inventory_error_Nms=float(np.max(abs(delta-couple-advection))),contact_point_pullbacks=pullback,minimum_vertex_to_other_surface_distance_m=min(inside),whole_surface_clearance='NOT CERTIFIED(vertex distances do not exclude crossing triangles)',solver_error=float(s['solver_error']),solver_iterations=int(s['solver_iterations'])))
 result=dict(status='FINITE_GUIDE_PULLBACK_AUDIT_ONLY',scope='Actual Native saved states and direct row points on finite CAD eyelet mesh. Stages compared separately,not selected to hide mismatch. Support absent;no holding/swept clearance/time PASS.',producer_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),geometry=geometry,records=records,maximum_contact_surface_distance_by_stage_m={label:max((p['surface_distances_by_explicit_stage_m'][label] for r in records for p in r['contact_point_pullbacks']),default=None) for label in ('previous','free_predictor','accepted')},maximum_mass_velocity_impulse_error_Ns_Nms=max(r['mass_velocity_impulse_error_Ns_Nms'] for r in records),maximum_angular_inventory_error_Nms=max(r['angular_inventory_error_Nms'] for r in records))
 result['maximum_ACTIVE_contact_surface_distance_by_stage_m']={label:max((p['surface_distances_by_explicit_stage_m'][label] for r in records for p in r['contact_point_pullbacks'] if p['normal_impulse_Ns']>0),default=None) for label in ('previous','free_predictor','accepted')}
 result['maximum_point_pullback_to_same_response_detector_error_m']=max((p['nearest_same_response_detector_point_error_m'] for r in records for p in r['contact_point_pullbacks'] if p['nearest_same_response_detector_point_error_m'] is not None),default=None)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('records','geometry')},indent=2))
if __name__=='__main__':main()
