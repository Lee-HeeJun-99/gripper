"""Finite proposed wire/hardware on OLD accepted frames;NOT candidate SOFA dynamics."""
import argparse,csv,json,math,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from rounded_wire_path import fillet
from generate import mesh as fem_mesh
sys.path.insert(0,str(BASE/'sofa'))
from analyse import rotation

def probes(route,radius):
 sphere=trimesh.creation.icosphere(subdivisions=2);distance=np.min(np.abs(np.einsum('ij,ij->i',sphere.face_normals,sphere.triangles[:,0])));sphere.apply_scale(radius/distance)
 for k,p in enumerate(route):
  ball=sphere.copy();ball.apply_translation(p);yield k,ball
  if k and np.linalg.norm(route[k]-route[k-1])>0:yield k,trimesh.creation.cylinder(radius=radius/math.cos(math.pi/64),segment=route[k-1:k+1],sections=64)

def segment_sphere_gap(route,centre,sphere_radius,wire_radius,sag):
 a=route[:-1];d=np.diff(route,axis=0);valid=np.einsum('ij,ij->i',d,d)>0;a=a[valid];d=d[valid]
 if not len(d):raise ValueError('undefined wire path')
 t=np.clip(np.einsum('ij,ij->i',centre-a,d)/np.einsum('ij,ij->i',d,d),0,1)
 return float(np.linalg.norm(a+t[:,None]*d-centre,axis=1).min()-sphere_radius-wire_radius-sag)

def material_boundary_faces(cfg):
 vertices,tets,_=fem_mesh(cfg);v=np.asarray(vertices);t=np.asarray(tets);groups={'skin':np.all(v[t,2]>=0,axis=1),'rails':np.all(v[t,2]<=0,axis=1)};result={}
 for name,mask in groups.items():
  faces={}
  for a,b,c,d in t[mask]:
   for face in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(face)),[]).append(face)
  result[name]=np.asarray([f[0] for f in faces.values() if len(f)==1])
 return len(v),result

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);p.add_argument('--radius-mm',type=float,default=2.);p.add_argument('--include-film',action='store_true');p.add_argument('--object-only-all-frames',action='store_true');p.add_argument('--all-event-worst',action='store_true');p.add_argument('--hardware-pairs',action='store_true');args=p.parse_args();out=BASE/'results'/args.tag;out.mkdir(exist_ok=False);start=time.monotonic();source=BASE/'meshes'/args.candidate/'assembly_recipe.json';assembly=json.loads(source.read_text());cfg=assembly['baseline_config'];old=BASE/'results/b3_alarm_window485';files=[source,old/'scene.scn',old/'config.json',old/'object.csv',old/'motion_commands.json',*[old/f'guide_frames{f}.csv' for f in range(3)]]
 if sha(old/'config.json')!=sha(BASE/assembly['manufacturing_config']['baseline_geometry']):raise ValueError('baseline identity mismatch')
 if any(c['node']!='floor' for c in json.loads((old/'motion_commands.json').read_text())['commands']):raise ValueError('actual moving pullpoint path required')
 tree=ET.parse(old/'scene.scn');objects=list(csv.DictReader((old/'object.csv').open()));times=np.array([float(r['time_s']) for r in objects]);reference=json.loads((BASE/'results/product_wire_replay742/summary.json').read_text());worst=max(reference['records'],key=lambda r:r['maximum_required_bore_radius_mm'])['worst_time_s'];files.append(BASE/'results/product_wire_replay742/summary.json');indices=sorted(set(int(np.argmin(abs(times-t))) for t in (worst,1.6,2.,2.355)));frames={};rests={};pulls={}
 for f in range(3):
  rows=list(csv.DictReader((old/f'guide_frames{f}.csv').open()))
  if not np.array_equal(times,[float(r['time_s']) for r in rows]):raise ValueError('unsynchronized body/object frames')
  frames[f]=[np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows];node=tree.find(f"./Node[@name='guides{f}']");rests[f]=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);pulls[f]=[np.fromstring(c.get('pullPoint'),sep=' ')*1000 for c in node.iter('CableConstraint')]
 if args.all_event_worst:
  candidates=[r['worst_time_s'] for r in reference['records']]+[1.6,2.,2.355,.4775];indices=sorted(set(int(np.argmin(abs(times-t))) for t in candidates))
 if args.object_only_all_frames:
  if args.include_film:raise ValueError('object-only mode must not imply film collision checking')
  indices=list(range(len(times)))
 parts=assembly['parts'];meshes={} if args.object_only_all_frames else {p['name']:evaluate(p['shape']) for p in parts};records=[];nodal={};film_quality=[];hardware_hits=[]
 if args.include_film:
  node_count,boundaries=material_boundary_faces(cfg)
  for f in range(3):
   file=old/f'finger{f}.csv';files.append(file);rows=list(csv.DictReader(file.open()))
   if not np.array_equal(times,[float(r['time_s']) for r in rows]):raise ValueError('unsynchronized nodal output')
   nodal[f]={idx:np.fromstring(rows[idx]['q_m'],sep=' ').reshape(-1,3)*1000 for idx in indices}
   if any(len(q)!=node_count for q in nodal[f].values()):raise ValueError('FEM nodal ordering size mismatch')
   original=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000
   from generate import world
   expected=np.asarray([world(cfg,v,cfg['palm']['angles_deg'][f]) for v in fem_mesh(cfg)[0]])
   if not np.allclose(original,expected,rtol=0,atol=1e-10):raise ValueError('actual scene FEM reference ordering mismatch')
 for idx in indices:
  solids=[];centres={}
  for part in parts:
   name=part['name'];mesh=None if args.object_only_all_frames else meshes[name].copy()
   if part['group'] in ('eyelet','support'):
    f=part['finger'];c=int(name.split('_')[1][1:]);k=int(name.split('_')[2][1:]);i=c*6+k;q=frames[f][idx][i];rest=rests[f][i];m=np.eye(4);m[:3,:3]=rotation(q[3:])@rotation(rest[3:]).T;m[:3,3]=q[:3]*1000-m[:3,:3]@(rest[:3]*1000)
    if mesh is not None:mesh.apply_transform(m)
    if part['group']=='eyelet':centres[f,c,k]=m[:3,:3]@np.asarray(part['shape']['matrix'])[:3,3]+m[:3,3]
   elif part['group']=='finger':continue # deformable Skin/Rails need actual nodal surface,not frozen rest mesh
   if mesh is not None:solids.append((name,mesh))
  centre=np.fromstring(objects[idx]['rigid_q'],sep=' ')[:3]*1000
  if args.hardware_pairs:
   metadata={p['name']:p for p in parts};hardware=[(name,solid) for name,solid in solids if metadata[name]['group'] in ('eyelet','support')]
   for i,(name,left) in enumerate(hardware):
    for other,right in hardware[i+1:]:
     if metadata[name]['finger']==metadata[other]['finger']:continue
     if np.any(np.minimum(left.bounds[1],right.bounds[1])-np.maximum(left.bounds[0],right.bounds[0])<=0):continue
     hit=trimesh.boolean.intersection([left,right],engine='manifold')
     if len(hit.faces):hardware_hits.append(dict(time_s=float(times[idx]),parts=[name,other],signed_volume_mm3=float(hit.volume)))
  if args.include_film:
   for f in range(3):
    for group,faces in boundaries.items():
     solid=trimesh.Trimesh(nodal[f][idx],faces,process=True);valid=bool(solid.is_volume);film_quality.append(dict(time_s=float(times[idx]),finger=f,group=group,closed_positive_winding=valid))
     if not valid:raise ValueError('invalid deformed FEM solid:cannot claim Boolean clearance')
     solids.append((f'f{f}_actual_{group}',solid))
  for f in range(3):
   for c in range(2):
    points=np.array([pulls[f][c],*[centres[f,c,k] for k in range(6)]]);record=dict(time_s=float(times[idx]),finger=f,cable=c)
    try:route,sag,trim=fillet(points,args.radius_mm)
    except ValueError as exc:record.update(status='REJECT_INVALID_FILLET',reason=str(exc));records.append(record);continue
    hits=[]
    for sample,probe in (() if args.object_only_all_frames else probes(route,cfg['tendon']['wire_radius']+sag)):
     for name,solid in solids:
      if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
      hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
      if len(hit.faces):hits.append(dict(sample=sample,part=name,signed_volume_mm3=float(hit.volume)))
    gap=segment_sphere_gap(route,centre,cfg['simulation']['sphere_radius_mm'],cfg['tendon']['wire_radius'],sag)
    record.update(status='SCREEN_REQUIRES_REFINEMENT_OR_REDESIGN' if hits or gap<=0 else 'NO_INTERSECTION_IN_THIS_FROZEN_SAMPLE_NOT_CCD_PASS',sphere_gap_lower_bound_mm=gap,intersections=hits,arc_sagitta_bound_mm=sag)
    if not args.object_only_all_frames:record['route_mm']=route.tolist()
    records.append(record)
 result=dict(status='SAMPLED_DEFORMED_WIRE_SCREEN_NOT_NEW_DYNAMICS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(f.relative_to(BASE.parent)):sha(f) for f in files},selected_times_s=times[indices].tolist(),proposed_radius_mm=args.radius_mm,records=records,runtime_s=time.monotonic()-start,scope='OLD485 accepted rigid frames/object motion plus NEW finite CAD. Actual attachment offsets/rotations retained. Skin/Rail deformable surfaces EXCLUDED,lead-in to motor absent. Circumscribed probes retain signed volumes;negative/zero sphere lower bound is not proof of collision. Not continuous CCD,new SOFA run,friction/material/strength qualification.')
 result['film_included']=args.include_film;result['deformed_surface_quality']=film_quality
 result['hardware_pair_check']=args.hardware_pairs;result['interfinger_hardware_intersections']=hardware_hits
 result['object_only_all_frames']=args.object_only_all_frames
 if args.object_only_all_frames:result['scope']+=' OBJECT-ONLY mode:all saved frames tested,but hardware intersections NOT TESTED in this run. No continuous-time guarantee.'
 if args.include_film:result['scope']=result['scope'].replace('Skin/Rail deformable surfaces EXCLUDED,','Actual saved Skin/Rail boundary surfaces INCLUDED with reference ordering verified;')+' Closed positive mesh does NOT certify absence of element inversion/self-intersection.'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(samples=len(records),rejected=sum(r['status']=='REJECT_INVALID_FILLET' for r in records),samples_needing_review=sum(r['status']=='SCREEN_REQUIRES_REFINEMENT_OR_REDESIGN' for r in records),minimum_sphere_gap_lower_bound_mm=min((r['sphere_gap_lower_bound_mm'] for r in records if 'sphere_gap_lower_bound_mm' in r),default=None),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
