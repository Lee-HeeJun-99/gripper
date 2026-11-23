"""Actual Root nut axial obstruction samples,not measured retention strength."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';frame=src.parent/'root_frame.json';parts,hashes=resolve_recipe(src);meta=json.loads((src.parent/'summary.json').read_text())
 if meta['target_finger']!=a.finger:raise ValueError('case Root frame and target finger mismatch')
 prefix=f'f{a.finger}';lookup={p['name']:p for p in parts};G=np.asarray(json.loads(frame.read_text()));clamp=evaluate(lookup[prefix+'_root_clamp']['shape']);carrier=evaluate(lookup[prefix+'_carrier']['shape']);records=[]
 for y in (-14,14):
  name=prefix+f'_retaining_nut_{y}';source=evaluate(lookup[name]['shape'])
  for dz in (0,.025,.05,.1,.2,1,3,-.1):
   nut=source.copy();nut.apply_translation(dz*G[:3,2]);records.append(dict(nut=name,translation_root_Z_mm=dz,intersections=intersections(nut,[(prefix+'_root_clamp',clamp),(prefix+'_carrier',carrier)])))
 for f in (Path(__file__),frame,src.parent/'summary.json',BASE/'config/root_nut_hood_v57.json',BASE/'cad/manufacturing_assembly.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='ROOT_NUT_AXIAL_OBSTRUCTION_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,actual_nut_retention_N=None,actual_preload_N=None,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Two original finite unthreaded nominal M3nut proxies translated relative to actual modified Root Clamp/carrier. Screws assumed removed for this axial escape diagnostic. Obstructions are geometric samples,not 6DOF retention/material flexure/tolerance/thread selflocking/strength/dynamic safety or a force test. Unchanged Skin/Rail joins remain intact;hood not adopted in Native. All faces/volumes retained,including nominal boundary artifacts.')
 result['target_finger']=a.finger
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_root_nut_hood1032');p.add_argument('--finger',type=int,choices=(0,1,2),default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_ROOT_NUT_CAPTURE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
