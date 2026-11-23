"""Integral Root clamp hood candidate;not measured nut retention or stiffness."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,box,cyl,union,cut,transform
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def hood_shape(original_local,cfg):
 roof=box(cfg['roof_lower_mm'],cfg['roof_upper_mm']);connection=box(cfg['connection_lower_mm'],cfg['connection_upper_mm'])
 shape=union(original_local,roof,connection)
 return cut(shape,*[cyl(cfg['through_hole_radius_mm'],-1,4,(x,y)) for x,y in cfg['retaining_nut_XY_mm']])

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';spec=BASE/'config/root_nut_hood_v57.json';cfg=json.loads(spec.read_text());parts,hashes=resolve_recipe(src);name=f'f{a.finger}_root_clamp';old=next(p for p in parts if p['name']==name);carrier=next(p for p in parts if p['name']==f'f{a.finger}_carrier');G=np.asarray(carrier['shape']['matrix']);local=hood_shape(transform(old['shape'],np.linalg.inv(G)),cfg);new=dict(old,shape=transform(local,G),role='UNQUALIFIED_INTEGRAL_NUT_HOOD');body=evaluate(new['shape']);file=out/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
 if not saved.is_volume or saved.body_count!=1:raise ValueError('actual saved hood disconnected or invalid')
 fixed=[p for p in parts if p['name']!=name];hits=intersections(body,[(p['name'],evaluate(p['shape'])) for p in fixed])
 (out/'assembly_delta_recipe.json').write_text(json.dumps(dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=[name],add_parts=[new]),indent=2));(out/'root_frame.json').write_text(json.dumps(G.tolist(),indent=2))
 for f in (Path(__file__),spec,BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='ROOT_NUT_HOOD_STATIC_REVIEW' if hits else 'ONE_INTEGRAL_ROOT_NUT_HOOD_STATIC_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,target_finger=a.finger,records=[dict(part=name,STL_SHA256=sha(file),CAD_volume_mm3=float(saved.volume))],solid_intersections=hits,candidate_part_count=len(parts),actual_preload_N=None,actual_nut_retention_N=None,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='One integral Root Clamp roof replaces one actual part,not omission of nuts or other hardware. Original Skin bearing/clamp bolts retained. New roof behind root edge covers nominal nut pockets with same bolt passages;extra volume/mass/stiffness not adopted in Native. Static no-hit is not capture/strength/thread/retaining-bolt removal/full service certification. All mating artifacts kept without threshold. Actual material/tolerance/preload/roof flexure and retention force unmeasured.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],hits=hits)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--finger',type=int,choices=(0,1,2),default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_ROOT_HOOD_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s','solid_intersections') if k in d}))
if __name__=='__main__':main()
