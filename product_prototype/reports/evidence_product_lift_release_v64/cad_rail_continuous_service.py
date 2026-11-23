"""Conservative continuous translation envelopes; hull hits are NOT proven collisions."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from bridge_assembly_audit import hits

def envelope(mesh,delta):
 delta=np.asarray(delta,dtype=float)
 if delta.shape!=(3,) or not np.all(np.isfinite(delta)):
  raise ValueError('finite translation required')
 # conv(S union (S+d)) contains every S+t*d, 0<=t<=1.
 # Exact only for a convex S. Concave parts may give false positives.
 return trimesh.convex.convex_hull(np.vstack((mesh.vertices,mesh.vertices+delta)))

def surface_sweep(mesh,delta,obstacles):
 """Exact per-triangle translation prisms, no concave whole-body hull fill.

 Initial volume must be checked separately. Zero-volume swept faces are
 counted, not thickened. This is a positive-volume interference diagnostic,
 NOT a no-touch/clearance proof or floating-point certified CCD.
 """
 found=[];collapsed=0;tested=0;unresolved=[]
 for index,triangle in enumerate(mesh.triangles):
  points=np.vstack((triangle,triangle+delta));lo=points.min(axis=0);hi=points.max(axis=0)
  candidates=[(name,body) for name,body in obstacles if np.all(np.minimum(hi,body.bounds[1])-np.maximum(lo,body.bounds[0])>0)]
  if not candidates:continue
  if np.dot(np.cross(triangle[1]-triangle[0],triangle[2]-triangle[0]),delta)==0:
   collapsed+=1;continue
  prism=trimesh.convex.convex_hull(points)
  if not prism.is_volume:
   unresolved.append(dict(triangle=index,reason='NONVOLUME_NUMERICAL_PRISM',obstacles=[name for name,_ in candidates],signed_volume_mm3=float(prism.volume)))
   continue
  for name,body in candidates:
   tested+=1;hit=trimesh.boolean.intersection([prism,body],engine='manifold')
   if len(hit.faces):found.append(dict(triangle=index,part=name,faces=len(hit.faces),signed_volume_mm3=float(hit.volume)))
 return dict(intersections=found,unresolved_prisms=unresolved,collapsed_candidate_faces=collapsed,CSG_tests=tested,triangle_count=len(mesh.faces))

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic()
 src=BASE/'results'/a.case/'full_assembly_recipe.json';frame=src.parent/'root_frame.json'
 parts=json.loads(src.read_text())['parts'];solids=[evaluate(p['shape']) for p in parts]
 M=np.asarray(json.loads(frame.read_text()));screw='f0_c1_s0_rail_clamp_screw_PROXY';pad='f0_c1_s0_rail_pressure_pad_RESEARCH'
 moving=[p['name'] for p in parts if p['name'].startswith('f0_c1_s0_') and p['name'] not in (screw,pad)]
 records=[]
 for p,solid in zip(parts,solids):
  name=p['name']
  if name!=pad and name not in moving:continue
  delta=-4*M[:3,1] if name==pad else 8*(M[:3,1]+M[:3,0])
  sweep=envelope(solid,delta);excluded=[pad,screw] if name==pad else [pad,screw,*moving]
  found=hits(sweep,parts,solids,excluded)
  records.append(dict(part=name,translation_mm=delta.tolist(),path_length_mm=float(np.linalg.norm(delta)),convex_source=bool(solid.is_convex),envelope_volume_mm3=float(sweep.volume),intersections=found,verdict='UNRESOLVED_ENVELOPE_INTERSECTION' if found else 'CONTINUOUS_TRANSLATION_ENVELOPE_CLEAR'))
 result=dict(status='CONSERVATIVE_SERVICE_UNRESOLVED' if any(r['intersections'] for r in records) else 'CONTINUOUS_TRANSLATION_ENVELOPES_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,frame,BASE/'cad/manufacturing_assembly.py',BASE/'cad/bridge_assembly_audit.py')},records=records,assembly_part_count=len(parts),runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Unloaded nominal CAD only. Screw already removed; pad slides inboard4mm then seven-part subassembly moves outboard8mm+longitudinal8mm. Each whole-body convex hull bounds ALL intermediate translations, not just samples. Hull intersections on concave solids are unresolved, NOT actual collision evidence. No rotation, tolerance, wire threading, real tools, preload, moving gripper or Native dynamics qualification.')
 if a.surface_support:
  name='f0_c1_s0_support';i=next(i for i,p in enumerate(parts) if p['name']==name);r=next(r for r in records if r['part']==name)
  obstacles=[(p['name'],s) for p,s in zip(parts,solids) if p['name'] in {h['part'] for h in r['intersections']}]
  detail=surface_sweep(solids[i],np.asarray(r['translation_mm']),obstacles)
  detail['initial_intersections']=hits(solids[i],parts,solids,[screw,pad,*moving])
  result['support_surface_refinement']=detail
  result['status']='SURFACE_SWEEP_REVIEW_REQUIRED' if detail['intersections'] or detail['initial_intersections'] or detail['unresolved_prisms'] else 'NO_POSITIVE_VOLUME_SUPPORT_SWEEP_HIT_ONLY'
  result['scope']+=' Optional Support refinement checks actual swept triangle prisms against hull-hit obstacles and initial Support solid. Zero-volume/near-coplanar/tangent contacts and numerical certification remain unqualified; no invented face thickness.'
 result['runtime_s']=time.monotonic()-start
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_rail_clamp908');p.add_argument('--worker',action='store_true');p.add_argument('--surface-support',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag or Path(a.case).name!=a.case:p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker']+(['--surface-support'] if a.surface_support else []);proc=guarded(cmd,out/'process',420)
 (out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CONTINUOUS_SERVICE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
