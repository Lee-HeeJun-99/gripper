"""Complete ONE placed lead's finite wheel/axle set;not qualified propagation."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,sector,transform

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/'full_assembly_recipe.json';donor=BASE/'results/product_captive_nut941/full_assembly_recipe.json';routefile=BASE/'results/product_supplier_first_recheck890/summary.json';parts=json.loads(src.read_text())['parts'];source=json.loads(donor.read_text())['parts'];lookup={p['name']:p for p in parts};sup={p['name']:p for p in source};S=sector(120*a.finger);prefix=f'f{a.finger}_c0';expected=transform(sup['f0_c0_root_mounted_bridge']['shape'],S)
 if lookup[prefix+'_root_mounted_bridge']['shape']!=expected:raise ValueError('placed backbone/source identity mismatch;do not blindly extract')
 new=[];shapes=[];records=[];obsolete=[]
 for k in (1,2,3):
  for suffix in ('','_headed_pin','_axle_nut'):
   name=f'f0_c0_turn{k}'+suffix;p=sup[name];q=dict(p,name=name.replace('f0_c0',prefix,1),shape=transform(p['shape'],S),finger=a.finger,role='UNQUALIFIED_SINGLE_LEAD_COMPLETION')
   body=evaluate(q['shape']);f=out/(q['name']+'.stl');f.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(f)
   if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid saved turn:'+q['name'])
   new.append(q);shapes.append(body);records.append(dict(part=q['name'],STL_SHA256=sha(f),volume_mm3=float(saved.volume)))
  obsolete.extend([prefix+f'_turn{k}_thrust_shim{j}' for j in (0,1)])
 if not all(name in lookup for name in obsolete):raise ValueError('obsolete shim set mismatch')
 removed=set(obsolete)|{p['name'] for p in new};fixed=[p for p in parts if p['name'] not in removed];fixedshapes=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,shapes)):
  for q,other in [*zip(fixed,fixedshapes),*zip(new[i+1:],shapes[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],faces=len(h.faces),signed_volume_mm3=float(h.volume)))
 route=np.asarray(json.loads(routefile.read_text())['route_mm']);route=route@S[:3,:3].T+S[:3,3]
 (out/'route_mm.json').write_text(json.dumps(route.tolist(),indent=2));(out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2))
 result=dict(status='REMAINING_LEAD_COMPLETION_REVIEW_REQUIRED' if hits else 'ONE_LEAD_NEW_TURN_SET_STATIC_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,donor,routefile,BASE/'cad/manufacturing_assembly.py')},records=records,solid_intersections=hits,replaced_parts=sorted(removed),obsolete_loose_shims_replaced_by_source_integral_thrust_lands=obsolete,full_part_count=len(fixed+new),target_finger=1,target_cable=0,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONLYf1c0placedlead mechanicalconsistencyrepair after951explicitbackboneinspection.9actualnewwheel/pin/nut parts replace9legacy parts;6looseshims replacedbyexisting951sourceintegralthrustlands,notdeletedwithoutsubstitute. Actual9changedvsallfixed/newCSG. Original951Palmseam/bondissuesunchanged. Route includesROOT+3TURNS+DRUM,butfinitewire clearance/service MUST be independently checked. OtherRoot/c1branches remainlegacy;notwholeassembly/moving/Native/strength/holding/STEPapproval.')
 result['target_finger']=a.finger
 result['scope']=f'ONLYf{a.finger}c0 placed lead completion,source identity checked;9wheel/pin/nut parts replace legacy and6loose shims replaced by actual integral lands. Other placed channels retained unchanged. All changed-part CSG tested;old Palm/bond issues remain unqualified. Not whole assembly,wire/contactlaw,movingclearance,Native,holding,threadfit,materialstrength or STEP approval.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_remaining_root951');p.add_argument('--finger',type=int,choices=(1,2),default=1);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_REMAINING_LEAD_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
