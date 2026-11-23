"""Sampled root pin extraction screen, not retained assembly qualification."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--outboard-sweep',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic()
 sources=[BASE/'meshes/b3_thrust_shims_v29/full_assembly_recipe.json',BASE/'meshes/b3_root_fork_v31/assembly_recipe.json'];parts=sum((json.loads(s.read_text())['parts'] for s in sources),[]);solids={x['name']:evaluate(x['shape']) for x in parts};records=[]
 for part in parts:
  if part['group']!='unmounted_root_pin':continue
  name=part['name'];axis=np.array(part['shape']['matrix'])[:3,2]
  signs=((1 if '_c0_' in name else -1),) if a.outboard_sweep else (-1,1)
  for sign in signs:
   for distance in ((10.,) if a.outboard_sweep else (2.,5.,10.)):
    moving=solids[name].copy();moving.apply_translation(sign*distance*axis);hits=[]
    if a.outboard_sweep:moving=trimesh.convex.convex_hull(np.vstack((solids[name].vertices,moving.vertices)))
    for other,body in solids.items():
     if other==name:continue
     if np.any(np.minimum(moving.bounds[1],body.bounds[1])-np.maximum(moving.bounds[0],body.bounds[0])<=0):continue
     hit=trimesh.boolean.intersection([moving,body],engine='manifold')
     if len(hit.faces):hits.append(dict(part=other,volume_mm3=float(hit.volume)))
    records.append(dict(pin=name,axis_sign=sign,withdrawal_mm=distance,intersections=hits))
 result=dict(status='SERVICE_BLOCKED' if any(r['intersections'] for r in records) else 'UNRETAINED_PIN_EXTRACTION_CLEAR_NOT_ASSEMBLY_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(s.relative_to(BASE)):sha(s) for s in sources+[Path(__file__)]},records=records,runtime_s=time.monotonic()-start,conservative_linear_swept_volume=a.outboard_sweep,scope='Finite pins vs298parts including own fork/wheel. Optional outboard sweep is convex hull of original/translated convex pin,containing entire10mm straight translation;otherwise only36samples. No tools,hand access,loose washer capture,retainer removal or load-bearing Palm mount. Current pins unretained;clearance is NOT final assembly/service qualification.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],samples=len(records),blocked=sum(bool(r['intersections']) for r in records),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
