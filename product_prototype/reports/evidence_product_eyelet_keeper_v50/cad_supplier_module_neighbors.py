"""All existing neighbors retained;explicit replacement/interface classification only."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,transform,sha

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'meshes'/a.candidate/'assembly_recipe.json';parent=BASE/'meshes/b3_root_thrust_v39/full_assembly_recipe.json';new=json.loads(src.read_text())['parts'];old=json.loads(parent.read_text())['parts'];newsolids=[evaluate(p['shape']) for p in new];hits=[];changes=[];extra=[]
 if a.guide_shift_mm:
  if a.guide_shift_mm<=0:raise ValueError('positive distal guide translation required')
  rootwire=BASE/'results/product_root_fork780/summary.json';leadwire=BASE/'results/product_motor_lead748/summary.json';extra=[rootwire,leadwire]
  first=np.array(next(r for r in json.loads(rootwire.read_text())['records'] if r['part']=='f0_c0_root_redirect')['route_mm'][0]);pull=np.array(next(r for r in json.loads(leadwire.read_text())['records'] if r['model']=='perimeter_rounded_candidate' and r['finger']==0 and r['cable']==0)['route_mm'][0]);direction=(first-pull)/np.linalg.norm(first-pull);T=np.eye(4);T[:3,3]=a.guide_shift_mm*direction
  changed=[]
  for part in old:
   if part['name'] in ('f0_c0_s0_eyelet','f0_c0_s0_support'):
    before=evaluate(part['shape']);replacement=dict(part,shape=transform(part['shape'],T));after=evaluate(replacement['shape']);file=out/(part['name']+'_translated.stl');file.write_text(after.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
    if not saved.is_volume or saved.body_count!=1:raise ValueError('translated finite guide readback failed')
    changes.append(dict(part=part['name'],translation_mm=T[:3,3].tolist(),before_volume_mm3=float(before.volume),after_volume_mm3=float(after.volume),STL_sha256=sha(file)));changed.append(replacement)
   else:changed.append(part)
  old=changed;(out/'changed_guides_recipe.json').write_text(json.dumps(dict(units='mm',parts=[p for p in changed if p['name'] in ('f0_c0_s0_eyelet','f0_c0_s0_support')]),indent=2))
 for other in old:
  solid=evaluate(other['shape'])
  for part,body in zip(new,newsolids):
   if np.any(np.minimum(body.bounds[1],solid.bounds[1])-np.maximum(body.bounds[0],solid.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([body,solid],engine='manifold')
   if len(hit.faces):
    if other['name'] in ('f0_c0_root_redirect','f0_c0_root_headed_pin'):kind='REPLACED_PART_OVERLAP_NOT_CLEARANCE'
    elif other['name']=='f0_c0_root_mounted_bridge':kind='OLD_INTEGRAL_MOUNT_REQUIRES_REBUILD'
    else:kind='UNCHANGED_NEIGHBOR_OBSTACLE'
    hits.append(dict(new=part['name'],existing=other['name'],classification=kind,volume_mm3=float(hit.volume),faces=len(hit.faces)))
 hard=[r for r in hits if r['classification']=='UNCHANGED_NEIGHBOR_OBSTACLE' and r['volume_mm3']>0]
 result=dict(status='FAIL_UNCHANGED_NEIGHBOR_CLEARANCE' if hard else 'BLOCKED_PALM_MOUNT_AND_FULL_ASSEMBLY_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in [Path(__file__),BASE/'cad/manufacturing_assembly.py',src,parent,*extra]},new_parts=len(new),existing_parts=len(old),guide_shift_mm=a.guide_shift_mm,changed_guides=changes,intersections=hits,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Actual finite CSG against ALL292 named parts,no collision model/obstacle disabled. Optionalfirstguide+support translation usesSAMEfinitegeometry,NOTshrunk/removedparts;twoSTLs/volumes/recipe preserved. Module-vs-neighbors only,nottranslated-guide-vs-allothers qualification. Replacedwheel/pin andoldintegralbridge are NOT silently excluded:overlaps recorded underseparateclasses. Hardobstacles FAIL;even nohardhit wouldnotqualify newmount,6modules,retention,motion,strength orassembly. NoSOFA adoption.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);p.add_argument('--guide-shift-mm',type=float,default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--candidate',a.candidate,'--guide-shift-mm',str(a.guide_shift_mm),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_NEIGHBOR_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
