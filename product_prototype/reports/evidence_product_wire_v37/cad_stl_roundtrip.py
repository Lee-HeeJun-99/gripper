"""STL representation candidate after724/725 found export/topology failures.

NO near-vertex merge,area tolerance,geometry perturbation or hole filling. Remove
only exactly zero-cross-product triangles after EXACT coordinate deduplication.
Canonical repeated mount modules and ASCII serialization are explicit representation
changes,not digital geometry identity. Nominal dimensions/Native scenes unchanged.
All historical failed STL files remain immutable. Not BRep/strength qualification.
"""
import argparse,json,shutil,subprocess
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector

def exact_cleanup(shape):
 vertices,inverse=np.unique(shape.vertices,axis=0,return_inverse=True);faces=inverse[shape.faces];triangles=vertices[faces];cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);keep=np.any(cross!=0.,axis=1)
 clean=trimesh.Trimesh(vertices,faces[keep],process=False)
 if not clean.is_watertight or clean.volume<=0 or clean.body_count!=1:raise ValueError('exact-only cleanup failed:do not fill holes or loosen tolerance')
 return clean,dict(exact_duplicate_vertices_removed=len(shape.vertices)-len(vertices),exact_zero_area_triangles_removed=int((~keep).sum()),volume_difference_mm3=float(clean.volume-shape.volume),vertex_coordinate_set_unchanged=bool(np.array_equal(vertices,np.unique(shape.vertices,axis=0))))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--candidate',default='b3_manufacturing_service_v19');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 if Path(a.name).name!=a.name:raise ValueError('unique local design name required')
 target=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;target.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);source=BASE/'meshes'/a.candidate;recipe=json.loads((source/'assembly_recipe.json').read_text());records=[]
 canonical=evaluate(next(p['shape'] for p in recipe['parts'] if p['name']=='f0_mount'))
 for part in recipe['parts']:
  original=evaluate(part['shape'])
  # Manufacturing mount is ONE nominal part instantiated at120deg,not three
  # independently rounded Boolean evaluations. New explicit tessellation rule.
  source_shape=canonical if part['group']=='mount' else original
  clean,metrics=exact_cleanup(source_shape)
  if part['group']=='mount':clean.apply_transform(sector(recipe['baseline_config']['palm']['angles_deg'][part['finger']]))
  metrics['old_independent_world_CSG_volume_difference_mm3']=float(clean.volume-original.volume)
  metrics['canonical_mount_module_instance']=part['group']=='mount'
  path=target/(part['name']+'.stl');path.write_text(clean.export(file_type='stl_ascii'));reread=trimesh.load_mesh(path)
  if not reread.is_watertight or reread.volume<=0 or reread.body_count!=1:raise ValueError('saved STL roundtrip failed:'+part['name'])
  old=trimesh.load_mesh(source/path.name);records.append(dict(part=part['name'],original_saved_STL_watertight=bool(old.is_watertight),new_saved_STL_watertight=bool(reread.is_watertight),new_saved_STL_body_count=int(reread.body_count),source_stl_sha256=sha(source/path.name),new_stl_sha256=sha(path),**metrics))
 for name in ('config.json','assembly_recipe.json'):shutil.copy2(source/name,target/name)
 result=dict(status='PASS_CANONICAL_MODULE_ASCII_STL_READBACK_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_recipe_sha256=sha(source/'assembly_recipe.json'),records=records,scope='160individualsolids with actual ASCII-STL reload tests. Exactvertexdedup/exactzero-area-face removal;ONEcanonical mount module rotated0/120/240deg avoids independent float32 CSG divergences. This CHANGES the tessellation/serialized numeric representation,not nominal manufacturing dimensions. Old independent CSG discrepancies measured,not silently zeroed. No near-vertex merge/holefilling/Native change. NOT BRep/assembly/moving-clearance/material/strength/fabrication qualification.',STEP_generated=False,fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));(target/'checks.json').write_text(json.dumps(result,indent=2));(draw/'checks.json').write_text(json.dumps(result,indent=2));(draw/'config.json').write_bytes((source/'config.json').read_bytes());(draw/'STL_READBACK_SCOPE.json').write_text(json.dumps(dict(source_drawings='product_prototype/drawings/b3_manufacturing_service_v19',nominal_geometry_configuration_unchanged=True,digital_geometry_identity_verified=False,representation_changed=True,source_STLs_three_failures_preserved=True,STEP=False,fabrication_ready=False),indent=2));print(json.dumps(dict(parts=len(records),old_saved_STL_failures=sum(not r['original_saved_STL_watertight'] for r in records),new_saved_STL_failures=sum(not r['new_saved_STL_watertight'] for r in records),exact_zero_area_triangles_removed=sum(r['exact_zero_area_triangles_removed'] for r in records),maximum_volume_difference_mm3=max(abs(r['volume_difference_mm3']) for r in records)),indent=2))
 # Preserve the legacy scope file but explicitly correct its old hardcoded label.
 (draw/'SOURCE_SCOPE.json').write_text(json.dumps(dict(actual_source_drawings=str((BASE/'drawings'/a.candidate).relative_to(BASE.parent)),actual_source_candidate=a.candidate,source_recipe_sha256=sha(source/'assembly_recipe.json'),legacy_scope_source_drawings_label_is_not_authoritative=True,STEP_generated=False,fabrication_ready=False),indent=2))
if __name__=='__main__':main()
