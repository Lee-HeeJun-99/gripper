"""Resolve union-component collision provenance without changing candidate solids."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'results/product_supplier_mount873/assembly_recipe.json';parts=json.loads(src.read_text())['parts'];wheel=evaluate(next(p['shape'] for p in parts if p['name']=='f0_c0_turn2'));bridge=next(p['shape'] for p in parts if p['name']=='f0_c0_root_mounted_bridge');branch=bridge['items'][0]
 while branch['op']=='difference':branch=branch['items'][0]
 if branch['op']!='union':raise ValueError('unexpected branch structure')
 hits=[]
 for label,op in [(f'new_branch_component_{i}',op) for i,op in enumerate(branch['items'])]+[(f'retained_root_component_{i}',op) for i,op in enumerate(bridge['items'][1:])]:
  body=evaluate(op)
  if np.any(np.minimum(wheel.bounds[1],body.bounds[1])-np.maximum(wheel.bounds[0],body.bounds[0])<=0):continue
  h=trimesh.boolean.intersection([wheel,body],engine='manifold')
  if len(h.faces):hits.append(dict(component=label,volume_mm3=float(h.volume),bounds_mm=body.bounds.tolist(),shape=op))
 result=dict(status='COMPONENT_PROVENANCE_DIAGNOSTIC_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src)},hits=hits,runtime_s=time.monotonic()-start,scope='Union components before original bore cuts;no geometry changed,no contact/force/product qualification')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(hits,indent=2))
if __name__=='__main__':main()
