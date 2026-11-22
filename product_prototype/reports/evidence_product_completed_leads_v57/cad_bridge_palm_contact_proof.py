"""Strict sufficient mesh-envelope bounds for Palm/bridge mating;no tolerance floor."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sector,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes'/a.candidate/'assembly_recipe.json';parts=json.loads(src.read_text())['parts'];records=[]
 for part in parts:
  if part['group']!='integral_bridge_forks':continue
  f=int(part['name'].split('_')[0][1:]);S=np.linalg.inv(sector(f*120));op=part['shape']
  while op['op']=='difference':op=op['items'][0]
  if op['op']!='union':raise ValueError('unsupported bridge decomposition:do not assume proof')
  witnesses=[]
  for i,bit in enumerate(op['items']):
   shape=evaluate(bit);shape.apply_transform(S);lo,hi=shape.bounds;nearest=np.maximum(np.maximum(lo[:2],-hi[:2]),0);radial_lower=float(np.linalg.norm(nearest));above=bool(lo[2]>=13.);outside=bool(radial_lower>64.)
   witnesses.append(dict(bit=i,min_z_mm=float(lo[2]),radial_AABB_lower_mm=radial_lower,above_or_at_palm_top=above,outside_outer_radius=outside,sufficient_exclusion=above or outside))
  records.append(dict(bridge=part['name'],all_bits_exclude_palm_open_interior=all(r['sufficient_exclusion'] for r in witnesses),witnesses=witnesses))
 result=dict(status='SUFFICIENT_MESH_ENVELOPE_MATING_DIAGNOSTIC_NOT_ASSEMBLY_GATE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),source_recipe_sha256=sha(src),records=records,scope='OriginalPalm open interior lies z<13 and radius<=64;holes only subtract matter. For EACH union operand before bore subtraction,strict minz>=13 OR sector-localAABB radial lower>64 suffices to exclude interior. Zero-volume coplanar mating is not positive penetration. No epsilon,geometry change,priorstatus overwrite,BRep/tolerance/strength/preload qualification.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(bridges=len(records),unproved=sum(not r['all_bits_exclude_palm_open_interior'] for r in records)),indent=2))
if __name__=='__main__':main()
