"""Independent c1 placement of actual clamp module;delta recipe,not adoption."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector,transform

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_remaining_lead964/full_assembly_recipe.json';donor=BASE/'results/product_captive_nut941/full_assembly_recipe.json';parts=json.loads(src.read_text())['parts'];source=json.loads(donor.read_text())['parts'];target=f'f{a.finger}_c1';S=sector(120*a.finger)
 chosen=[p for p in source if p['name'].startswith('f0_c1_root') or p['name'].startswith('f0_c1_s0_')]
 if len(chosen)!=13:raise ValueError('expected actual13part source clamp,do not omit hardware')
 new=[dict(p,name=p['name'].replace('f0_c1',target,1),shape=transform(p['shape'],S),finger=a.finger,role='UNQUALIFIED_C1_CLAMP_PLACEMENT') for p in chosen];names={p['name'] for p in new};removed=[p['name'] for p in parts if p['name'] in names];fixed=[p for p in parts if p['name'] not in names];bodies=[evaluate(p['shape']) for p in new];obstacles=[evaluate(p['shape']) for p in fixed];hits=[];records=[]
 for i,(p,body) in enumerate(zip(new,bodies)):
  file=out/(p['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid saved clamp solid')
  records.append(dict(part=p['name'],STL_SHA256=sha(file),volume_mm3=float(saved.volume)))
  for q,other in [*zip(fixed,obstacles),*zip(new[i+1:],bodies[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],faces=len(h.faces),signed_volume_mm3=float(h.volume)))
 delta=dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=removed,add_parts=new)
 (out/'assembly_delta_recipe.json').write_text(json.dumps(delta,indent=2))
 result=dict(status='CLAMPED_ROOT_PLACEMENT_REVIEW' if hits else 'ONE_CLAMPED_ROOT_STATIC_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,donor,BASE/'cad/manufacturing_assembly.py')},records=records,solid_intersections=hits,target_finger=a.finger,target_cable=1,retained_part_count=len(fixed),candidate_part_count=len(fixed+new),runtime_s=time.monotonic()-start,fabrication_ready=False,actual_joint_strength=None,scope='ONE13part donor c1Root/clamp independently placed against retained964assembly. All hardware collisions retained. Delta MUST resolve exact parent SHA;not standalone full assembly. Source backbone includes Turn forks,legacy target Turn wheel/axle/shims not yet coherently replaced;wire/service/motion MUST be checked after completion. No bond deletion,Nativeadoption,preload/material/holding/STEPqualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--finger',type=int,choices=(1,2),required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--finger',str(a.finger),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CLAMPED_ROOT_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s','solid_intersections') if k in d},indent=2))
if __name__=='__main__':main()
