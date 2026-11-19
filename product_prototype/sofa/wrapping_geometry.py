"""Connected accepted Skin proximity regions and curvature;NOT pressure/area/holding."""
import argparse,json,csv
from pathlib import Path
import numpy as np
import trimesh
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);faces=np.array(mesh['triangles']);faces=faces[np.all(local[faces,2]>=0,axis=1)]
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('completed actual states required')
 edge_faces={}
 for k,face in enumerate(faces):
  for j in range(3):edge_faces.setdefault(tuple(sorted((int(face[j]),int(face[(j+1)%3])))),[]).append(k)
 adjacency={k:set() for k in range(len(faces))}
 for group in edge_faces.values():
  for k in group:adjacency[k].update(set(group)-{k})
 objects=read(src/'object.csv');centre=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in objects]);R=cfg['simulation']['sphere_radius_mm']*.001;threshold=cfg['simulation']['contact_distance_mm']*.001;records=[]
 for f in range(meta['fingers']):
  rows=read(src/f'finger{f}.csv');times=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);angle=np.deg2rad(cfg['palm']['angles_deg'][f]);radial=np.array([np.cos(angle),np.sin(angle),0]);stations=sorted(set(local[:,0]));centres=[]
  for x in stations:
   ids=np.flatnonzero((local[:,0]==x)&(local[:,2]==.1));ids=ids[np.argsort(local[ids,1])];y=local[ids,1];weights=np.zeros(len(ids));weights[:-1]+=np.diff(y)/2;weights[1:]+=np.diff(y)/2;weights/=weights.sum();centres.append((q[:,ids]*weights[None,:,None]).sum(axis=1))
  line=np.stack(centres,axis=1);d=np.diff(line,axis=1);length=np.linalg.norm(d,axis=2);unit=d/length[:,:,None];curvature=np.arccos(np.clip(np.sum(unit[:,:-1]*unit[:,1:],axis=2),-1,1))/((length[:,:-1]+length[:,1:])/2)
  for target in sorted(set([.5,1.,1.6,2.,float(times[-1])])):
   if target>times[-1]+1e-12:continue
   k=int(np.argmin(abs(times-target)));closest=trimesh.triangles.closest_point(q[k,faces],np.repeat(centre[k,None,:],len(faces),axis=0));delta=closest-centre[k];gap=np.linalg.norm(delta,axis=1)-R;selected=set(np.flatnonzero(gap<=threshold).tolist());components=[]
   while selected:
    stack=[selected.pop()];group=[]
    while stack:
     face=stack.pop();group.append(face);neighbors=adjacency[face]&selected;selected-=neighbors;stack.extend(neighbors)
    theta=np.arctan2(delta[group,2],delta[group]@radial);components.append(dict(faces=len(group),projected_arc_range_deg=np.rad2deg([theta.min(),theta.max()]).tolist(),projected_arc_span_deg=float(np.rad2deg(np.ptp(theta))),minimum_gap_mm=float(gap[group].min()*1000)))
   tip_angle=float(np.rad2deg(np.arccos(np.clip(np.dot(unit[k,0],unit[k,-1]),-1,1))))
   records.append(dict(finger=f,time_s=float(times[k]),proximity_components=components,maximum_width_mean_skin_curvature_per_mm=float(curvature[k].max()/1000),root_to_tip_angle_deg=tip_angle,minimum_skin_gap_mm=float(gap.min()*1000)))
 result=dict(status='GEOMETRY_METRICS_ONLY_NOT_WRAPPING_PASS',scope='connected accepted mesh proximity regions using declared contact buffer;projected arc is not pressure-bearing coverage or actual contact area;no deformation scaling',case=a.case,records=records,contact_area=None,pressure=None,source_sha256=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'mesh.json',src/'object.csv')});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
