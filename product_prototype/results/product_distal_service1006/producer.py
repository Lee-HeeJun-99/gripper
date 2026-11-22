"""One distal keeper: local mating diagnostic, nominal key and sampled cover service.

Neither floating CSG nor axial obstruction is a physical retention certificate.
"""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,transform
from assembly_recipe_io import resolve_recipe
from distal_keeper import keeper_shapes,axial

def intersections(body,obstacles):
 found=[]
 for name,other in obstacles:
  if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
  h=trimesh.boolean.intersection([body,other],engine='manifold')
  if len(h.faces):found.append(dict(part=name,faces=len(h.faces),signed_volume_mm3=float(h.volume)))
 return found

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);cfgpath=BASE/'config/distal_keeper_v52.json';cfg=json.loads(cfgpath.read_text());G=np.asarray(json.loads((src.parent/'keeper_frame.json').read_text()));prefix='f0_c0_s5_';lookup={p['name']:p for p in parts};oldparts,_=resolve_recipe(BASE/'results/product_distal_basal1000/assembly_delta_recipe.json');old=next(p for p in oldparts if p['name']==prefix+'support');local=keeper_shapes(transform(old['shape'],np.linalg.inv(G)),cfg);names=[prefix+s for s in ('support','keeper_cover','keeper_screw0','keeper_screw1','keeper_nut0','keeper_nut1')];bodies=[evaluate(s) for s in local]
 localpairs=[]
 for i,j in ((0,1),(1,2),(1,3)):
  localpairs.append(dict(parts=[names[i],names[j]],intersections=intersections(bodies[i],[(names[j],bodies[j])])) )
 obstacles=[(p['name'],evaluate(p['shape'])) for p in parts];records=[];d=cfg['design'];top=d['cap_wing_top_Z_mm'];head=max(cfg['screw']['head_height_mm']);depth=cfg['screw']['nominal_drive_depth_mm'];radius=(cfg['screw']['hex_AF_mm']/np.sqrt(3))/np.cos(np.pi/64)
 for i,(x,y) in enumerate(d['bolt_centres_XY_mm']):
  # Circumscribed circular envelope contains every roll of nominal AF key.
  key=evaluate(transform(cyl(radius,top+head-depth,top+head+15,(x,y)),G));excluded={names[2+i]};records.append(dict(operation='NOMINAL_KEY_SHANK_CONTINUOUS_AXIAL_ENVELOPE',bolt=i,intersections=intersections(key,[(n,b) for n,b in obstacles if n not in excluded]),key_AF_mm=cfg['screw']['hex_AF_mm'],key_reach_mm=15,whole_tool_and_hand_qualified=False))
 # Screws and nuts removed before cover withdrawal. Actual concave part, not hull.
 for dz in (0,.1,.5,1,2,4,8):
  T=np.eye(4);T[2,3]=dz;cover=evaluate(transform(transform(local[1],T),G));records.append(dict(operation='COVER_WITHDRAWAL_SAMPLED_ONLY',translation_local_Z_mm=dz,intersections=intersections(cover,[(n,b) for n,b in obstacles if n not in set(names[1:])])) )
 axialtests=[]
 # Closed housing obstruction against two catalog length extremes; no 6DOF proof.
 housing=[(names[0],bodies[0]),(names[1],bodies[1])]
 for length in (3,5):
  for dx in (0,.1,.3,2.3):
   terminal=evaluate(axial(1.4,1+dx,1+length+dx));axialtests.append(dict(terminal_length_mm=length,axial_translation_mm=dx,intersections=intersections(terminal,housing)))
 for f in (Path(__file__),BASE/'cad/distal_keeper.py',cfgpath):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DISTAL_KEEPER_SERVICE_REVIEW' if any(r['intersections'] for r in records) else 'ONE_KEEPER_NOMINAL_KEY_AND_SAMPLED_COVER_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,local_mating_diagnostics=localpairs,service_records=records,axial_terminal_obstruction_samples=axialtests,actual_preload_N=None,actual_retention_N=None,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='1005 original world CSG hits preserved; local-frame diagnostics do not replace them. Nominal key shank only, no head/hand/bent-key clearance. Cover translation seven samples, screws/nuts already removed; not continuous sweep or complete assembly sequence. Axial stop samples are NOT general slack/rotation retention, thread fit, strength, tolerance, physical material or Native qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s']),indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_keeper1005');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_DISTAL_SERVICE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
