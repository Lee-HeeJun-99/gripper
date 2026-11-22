"""Independent static CAD audits; do not relabel old positive intersections.

Tests common-frame mesh-kernel sensitivity and actual deck-to-palm hole passage.
No motion/strength/fastener/STEP qualification. Historical candidate results stay.
"""
import argparse,inspect,json,subprocess,sys
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,root_frame,cyl,transform,sector,sha,standoff_positions

def intersection_volume(a,b):
 s=trimesh.boolean.intersection([a,b],engine='manifold',check_volume=True)
 return float(s.volume) if not s.is_empty else 0.

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='b3_manufacturing_mount_v14');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes'/a.candidate;assembly=json.loads((src/'assembly_recipe.json').read_text());cfg=assembly['baseline_config'];design=assembly['manufacturing_config'];byname={p['name']:p for p in assembly['parts']};shapes={};seams=[]
 def shape(name):
  if name not in shapes:shapes[name]=evaluate(byname[name]['shape'])
  return shapes[name]
 for i,angle in enumerate(cfg['palm']['angles_deg']):
  inv=np.linalg.inv(root_frame(cfg,angle))
  for name in (f'f{i}_carrier',f'f{i}_root_clamp'):
   first,second=shape(name).copy(),shape(f'f{i}_skin').copy();global_volume=intersection_volume(first,second);first.apply_transform(inv);second.apply_transform(inv);local_volume=intersection_volume(first,second)
   seams.append(dict(parts=[name,f'f{i}_skin'],world_frame_intersection_mm3=global_volume,common_root_frame_intersection_mm3=local_volume,frame_difference_mm3=abs(global_volume-local_volume),classification='CONTACT_SEAM_MESH_KERNEL_SENSITIVITY_NOT_BREP_CLEARANCE_PASS'))
 holes=[];drive=design['drive']
 for i,angle in enumerate(cfg['palm']['angles_deg']):
  for r,y in standoff_positions(drive):
    # Smaller-than-clearance gauge cylinder checks actual through material.
   tool=evaluate(transform(cyl(1.5,5.01,12.99,(r,y)),sector(angle)));blocked=intersection_volume(shape('palm'),tool)
   holes.append(dict(finger=i,radial_mm=r,tangential_mm=y,palm_material_blocking_gauge_mm3=blocked,status='BLOCKED_PALM_HOLE' if blocked>1e-6 else 'MESH_HOLE_PASSAGE_SCOPE_ONLY'))
 kernel=Path(inspect.getfile(trimesh.boolean));(out/'kernel_function.txt').write_text(inspect.getsource(trimesh.boolean.boolean_manifold))
 result=dict(status='CAD_STATIC_DIAGNOSTIC_NOT_ASSEMBLY_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),candidate=a.candidate,input_recipe_sha256=sha(src/'assembly_recipe.json'),kernel_source=str(kernel),kernel_sha256=sha(kernel),seams=seams,deck_hole_gauges=holes,
             interpretation='Installed trimesh Boolean conversion explicitly casts vertices to float32. Old world intersections remain evidence;local-frame comparison diagnoses basis sensitivity only. No volume threshold is a physical clearance tolerance. Throughbolt shared axes require one continuous fastener,not stacked head plus standoff.',
             BRep_clearance_verified=False,fastener_and_tool_access_verified=False,moving_clearance_verified=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
