"""Purchased-thread designation + finite nut cage candidate;NOT helical fit/strength."""
import argparse,json,subprocess,sys,time,math
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,box,cyl,cut,union,transform,poly

def adjuster(length=3.,end_diameter=.8):
 if not 2.8<=length<=3.2 or not .55<=end_diameter<=.8:raise ValueError('outside catalog dimensional crosscheck')
 z=.42;r=end_diameter/2;profile=[[0,z],[r,z],[.8,z+.8-r],[.8,z+length],[0,z+length],[0,z]]
 body=trimesh.creation.revolve(profile,sections=64);body.apply_translation([12,11.5,0])
 return cut(poly(body),cyl(.7/math.sqrt(3),z+length-1.5,z+length+.1,(12,11.5),6))

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();source=BASE/'results/product_rail_pressure_shoe926';src=source/'full_assembly_recipe.json';frame=source/'root_frame.json';spec=BASE/'config/pressure_shoe_fastener_v47.json';M=np.asarray(json.loads(frame.read_text()));parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};support=lookup['f0_c1_s0_support'];old=evaluate(support['shape']);old.apply_transform(np.linalg.inv(M))
 # Remove only old upper boss. Skin/Rail/pad/keeper/remaining assemblies untouched.
 old=cut(poly(old),box([10.8,10.3,.82],[13.2,12.7,2.0]))
 pocket=cyl(3.3/math.sqrt(3),1.25,2.65,(12,11.5),6)
 cage=cut(box([9.4,9.0,.82],[14.6,14.0,3.2]),pocket,box([8,9.85,1.25],[12,13.15,2.65]),cyl(.85,.3,3.4,(12,11.5)))
 mounted=transform(union(old,cage),M)
 screw=transform(adjuster(a.screw_length),M)
 nut=transform(cut(cyl(3.2/math.sqrt(3),1.3,2.6,(12,11.5),6),cyl(.81,1.2,2.7,(12,11.5))),M)
 new=[dict(support,shape=mounted),dict(name='f0_c1_s0_pressure_adjuster_M1p6',group='catalog_thread_ENVELOPE',shape=screw,thread='M1.6x0.35 RH',candidate_part='Accu SSF-M1.6-3-A2',thread_geometry='NOMINAL_MAJOR_ENVELOPE_NOT_HELIX_OR_FIT'),dict(name='f0_c1_s0_pressure_captive_nut_M1p6',group='catalog_thread_ENVELOPE',shape=nut,thread='M1.6x0.35 RH',candidate_part='Aspen ME177-016035',thread_geometry='CONSERVATIVE_SHARP_HEX_AND_CLEAR_BORE_NOT_FIT')]
 shapes=[];records=[]
 for p in new:
  body=evaluate(p['shape']);f=out/(p['name']+'.stl');f.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(f)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid saved solid:'+p['name'])
  shapes.append(body);records.append(dict(part=p['name'],volume_mm3=float(saved.volume),singlebody=True,STL_SHA256=sha(f)))
 fixed=[p for p in parts if p['name'] not in ('f0_c1_s0_support','f0_c1_s0_rail_clamp_screw_PROXY')];fixedshapes=[evaluate(p['shape']) for p in fixed];collisions=[]
 for i,(p,body) in enumerate(zip(new,shapes)):
  for q,other in [*zip(fixed,fixedshapes),*zip(new[i+1:],shapes[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(hit.faces):collisions.append(dict(parts=[p['name'],q['name']],faces=len(hit.faces),signed_volume_mm3=float(hit.volume)))
 (out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(out/'root_frame.json').write_text(json.dumps(M.tolist()))
 result=dict(status='CAPTIVE_NUT_CAD_REVIEW_REQUIRED' if collisions else 'CAPTIVE_NUT_STATIC_ENVELOPES_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,frame,spec,BASE/'cad/manufacturing_assembly.py')},records=records,solid_intersections=collisions,full_part_count=len(fixed+new),screw_length_crosscheck_mm=a.screw_length,pocket_AF_mm=3.3,pocket_height_mm=1.4,design_upper_wall_mm=.55,design_lower_wall_mm=.43,actual_thread_fit_qualified=False,actual_preload_N=None,actual_joint_strength_N=None,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE NEWsecondRoot:captive purchased M1.6nut and headless compressive adjuster instead of D1headed proxy. Major-diameter screw envelope plus catalog flatpoint/hexsocket;nut sharphex/bore are ENVELOPES,NOT helical flank/tolerance fit CAD. Side insertion after screw removal;upper/lower walls and side flats geometrically retain nut only when screw installed. No frictionlocking/preload/strength/realprocess or Native/holding qualification. No washer added:separate .30mmpressure shoe retains footprint;it isNOT pressure measurement. Wall dimensions are local design intervals,NOT wholepart minimum wall.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=collisions,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--screw-length',type=float,default=3);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag or not 2.8<=a.screw_length<=3.2:p.error('local tag/catalog interval required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--screw-length',str(a.screw_length),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CAPTIVE_NUT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
