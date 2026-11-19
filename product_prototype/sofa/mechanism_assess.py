"""Actual-state single-finger mechanism comparison;fixed reaction != free grasp."""
import argparse,csv,json,sys,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from mechanism_candidates import BASE,world,width,guide_normal
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());c=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());local=np.array(m['local_positions_mm']);tet=np.array(m['tetrahedra']);faces=np.array(m['triangles']);faces=faces[np.all(local[faces,2]>=0,axis=1)];rows=read(src/'finger0.csv');t=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);dt=meta['dt_s'];centre=np.array(c['simulation']['sphere_center_mm'])*.001;R=c['simulation']['sphere_radius_mm']*.001;time_index={x:k for k,x in enumerate(t)};vectors={k:np.zeros((len(t),6)) for k in ('skin','guide','rail','other')};normal=[[] for _ in t];blocks={};onset={}
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED' or meta['fingers']!=1 or meta['object']!='fixed':raise ValueError('completed fixed-object single-finger comparison required')
 for row in read(src/'response_rows.csv'):
  pair=(row['model0'],row['model1'])
  if not any('/object/' in x for x in pair):continue
  other=next(x for x in pair if '/object/' not in x);kind='skin' if '/skinCollision/' in other else 'guide' if '/guides' in other else 'rail' if '/railCollision/' in other else 'other';k=time_index[float(row['time_s'])];v=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ');vectors[kind][k]+=v;lam=float(row['lambda_Ns']);offset=(int(row['row_id'])-int(row['first_row']))%3
  if np.linalg.norm(v)>0:onset.setdefault(kind,float(t[k]))
  if kind=='skin' and offset==0 and lam>0:
   n=v[:3]/lam;length=np.linalg.norm(n)
   if length>0:normal[k].append(dict(n=(n/length).tolist(),normal_N=lam*length/dt,upward_cone=float(n[2]/length+c['simulation']['friction']*np.sqrt(max(0,1-(n[2]/length)**2)))))
 fixed=read(src/'collision_object.csv');inventory=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in fixed]);partition_error=float(np.max(abs(sum(vectors.values())-inventory)))
 hold=(t>=.6-1e-12)&(t<=.9+1e-12);normal_records=[x for k in np.flatnonzero(hold) for x in normal[k]];forces={kind:dict(mean_N=(v[hold,:3]/dt).mean(axis=0).tolist(),maximum_N=float(np.linalg.norm(v[:,:3]/dt,axis=1).max())) for kind,v in vectors.items()}
 stations=sorted(set(local[:,0]));line=np.array([q[:,(local[:,0]==x)&(local[:,2]==c['finger']['skin_thickness'])].mean(axis=1) for x in stations]).transpose(1,0,2);d=np.diff(line,axis=1);length=np.linalg.norm(d,axis=2);unit=d/length[:,:,None];turn=np.arccos(np.clip(np.sum(unit[:,1:]*unit[:,:-1],axis=2),-1,1));curv=turn/((length[:,1:]+length[:,:-1])/2);tipangle=np.rad2deg(np.arccos(np.clip(np.sum(unit[:,0]*unit[:,-1],axis=1),-1,1)));rest=np.array([world(c,p,0) for p in local])*.001;tip=local[:,0]==100
 det=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2));rest_det=np.linalg.det((rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1));guide_gap=1e9;wire_gap=1e9;cable_errors=[];root=ET.parse(src/'scene.scn')
 for j in (0,1):
  guides=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in rows]);pull=np.fromstring(root.find(f"./Node[@name='guides0']/Node[@name='cable{j}']/CableConstraint").get('pullPoint'),sep=' ');initial=np.fromstring(root.find(f"./Node[@name='guides0']/Node[@name='cable{j}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(np.vstack([pull,initial]),axis=0),axis=1).sum();segments=np.diff(np.concatenate([np.broadcast_to(pull,(len(t),1,3)),guides],axis=1),axis=1);short=L0-np.linalg.norm(segments,axis=2).sum(axis=1);error=short-np.array([float(r['command_m']) for r in rows]);cable_errors.append(dict(max_error_mm=float(abs(error).max()*1000),hold_max_error_mm=float(abs(error[hold]).max()*1000),final_error_mm=float(error[-1]*1000)))
  guide_gap=min(guide_gap,float((np.linalg.norm(guides-centre,axis=2)-R-np.hypot(c['tendon']['guide_outer_radius'],1)*.001).min()*1000));start=np.concatenate([np.broadcast_to(pull,(len(t),1,3)),guides[:,:-1]],axis=1);u=np.clip(np.sum((centre-start)*segments,axis=2)/np.sum(segments*segments,axis=2),0,1);wire_gap=min(wire_gap,float((np.linalg.norm(start+u[:,:,None]*segments-centre,axis=2)-R-c['tendon']['wire_radius']*.001).min()*1000))
 geometry=[]
 for target in (.25,.5,.6,.75,.9,1.,1.5,2.):
  if target>t[-1]+1e-12:continue
  k=int(np.argmin(abs(t-target)));cp=trimesh.triangles.closest_point(q[k,faces],np.repeat(centre[None],len(faces),axis=0));gap=np.linalg.norm(cp-centre,axis=1)-R;chosen=cp[gap<=c['simulation']['contact_distance_mm']*.001];geometry.append(dict(time_s=float(t[k]),minimum_skin_gap_mm=float(gap.min()*1000),proximity_z_relative_mm=[float((chosen-centre)[:,2].min()*1000),float((chosen-centre)[:,2].max()*1000)] if len(chosen) else None,root_to_tip_deg=float(tipangle[k]),peak_curvature_per_mm=float(curv[k].max()/1000),tip_displacement_mm=((q[k,tip].mean(axis=0)-rest[tip].mean(axis=0))*1000).tolist()))
 # Unit-tension guide moments in the actual manufactured reference,not FEM response.
 route=[]
 for side in (-1,1):
  route.append(np.array([world(c,[x,side*(width(c,x)/2+c['tendon']['outboard']),guide_normal(c,x)]) for x in [0]+c['tendon']['guide_stations']]))
 moment=[]
 for route_side,side in zip(route,(-1,1)):
  ds=np.diff(route_side,axis=0);u=ds/np.linalg.norm(ds,axis=1)[:,None];force=-u.copy();force[:-1]+=u[1:]
  for k,x in enumerate(c['tendon']['guide_stations']):
   base=np.array(world(c,[x,side*width(c,x)/2,0]));moment.append(dict(side=side,station_mm=x,moment_per_unit_tension_mm=np.cross(route_side[k+1]-base,force[k]).tolist()))
 result=dict(status='MECHANISM_DIAGNOSTIC_NOT_GRASP_PASS',case=a.case,actual_contact_source=onset,fixed_reaction_partition_error_Ns_Nms=partition_error,hold_window_s=[.6,.9],hold_forces=forces,hold_active_normal_rows=len(normal_records),normal_z_range=[min(x['n'][2] for x in normal_records),max(x['n'][2] for x in normal_records)] if normal_records else None,upward_cone_range=[min(x['upward_cone'] for x in normal_records),max(x['upward_cone'] for x in normal_records)] if normal_records else None,hold_frames_with_positive_upward_cone=sum(any(x['upward_cone']>0 for x in normal[k]) for k in np.flatnonzero(hold)),hold_frames=int(hold.sum()),cable_errors=cable_errors,minimum_guide_object_gap_mm=guide_gap,minimum_wire_object_gap_mm=wire_gap,minimum_tet_determinant_ratio=float((det/rest_det).min()),inverted_element_samples=int((det<=0).sum()),final_tip_return_error_mm=float(np.linalg.norm(q[-1,tip].mean(axis=0)-rest[tip].mean(axis=0))*1000),geometry=geometry,unit_tension_guide_moments=moment,self_intersection=None,contact_area=None,pressure=None,root_reaction=None,energy=None,wrench_capacity='NOT MEASURED;direction bound not capacity;single fixed sphere reaction not unsupported holding',source_hash=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in src.glob('*.csv')})
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ('input_hashes','unit_tension_guide_moments','geometry')}))
if __name__=='__main__':main()
