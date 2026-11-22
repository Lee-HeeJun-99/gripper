"""ONE remaining Root placement hypothesis,not automatic six-module adoption."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector,transform

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/'full_assembly_recipe.json';routefile=BASE/'meshes/b3_supplier_root_mount_v42/route_mm.json';parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};S=sector(120*a.finger);source_names=['f0_c0_root_redirect','f0_c0_root_mounted_bridge','f0_c0_root_headed_pin','f0_c0_s0_eyelet','f0_c0_s0_support','f0_c0_s0_bondline_RESEARCH'];target=f'f{a.finger}_c0';new=[];solids=[];records=[]
 for name in source_names:
  p=lookup[name];q=dict(p,name=name.replace('f0_c0',target,1),shape=transform(p['shape'],S),finger=a.finger,role='UNQUALIFIED_SINGLE_ROOT_PLACEMENT_SCREEN')
  body=evaluate(q['shape']);file=out/(q['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid saved remainingRoot solid:'+q['name'])
  new.append(q);solids.append(body);records.append(dict(source_part=name,target_part=q['name'],volume_mm3=float(saved.volume),STL_SHA256=sha(file)))
 names={p['name'] for p in new};fixed=[p for p in parts if p['name'] not in names];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,solids)):
  for q,other in [*zip(fixed,fixedsolids),*zip(new[i+1:],solids[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],faces=len(h.faces),signed_volume_mm3=float(h.volume),classification='UNSELECTED_BOND_INTERFACE_REVIEW' if any('bondline' in n for n in (p['name'],q['name'])) else 'SOLID_INTERFERENCE_REVIEW'))
 route=np.array(json.loads(routefile.read_text()));route=route@S[:3,:3].T+S[:3,3];(out/'route_mm.json').write_text(json.dumps(route.tolist(),indent=2));(out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2))
 result=dict(status='REMAINING_ROOT_LAYOUT_REVIEW_REQUIRED' if hits else 'ONE_ROOT_STATIC_PLACEMENT_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,routefile,BASE/'cad/manufacturing_assembly.py')},target_finger=a.finger,target_cable=0,records=records,solid_intersections=hits,replaced_existing_names=sorted(names&set(lookup)),retained_other_parts=len(fixed),full_part_count=len(fixed+new),runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONLYone remainingf1/f2c0Root layout hypothesis.6supplier-sized sourceparts rigidlyplaced atdeclared120/240deg,5legacy targetparts replaced,othersretained;allnewvsactualassembly CSG checked. ThisisNOTblindpropagationorqualifiedjoint/adopted3Fingerassembly. Otherturns/lead/Rootc1 remain legacy;wirepath and service MUST be checked independently. Unselectedbond/translatedRailSkinattachment/actualmaterials/mass/joints/Native/movinginterference/holding/STEP remain unqualified.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_captive_nut941');p.add_argument('--finger',type=int,choices=(1,2),required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_REMAINING_ROOT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
