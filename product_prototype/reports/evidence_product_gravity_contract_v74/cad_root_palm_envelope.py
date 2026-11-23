"""Conservative leaf-envelope exclusion of Palm open interior;no epsilon."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,transform,sector,sha

def additive_leaves(op,M=None):
 M=np.eye(4) if M is None else M
 if op['op']=='difference':yield from additive_leaves(op['items'][0],M)
 elif op['op']=='union':
  for x in op['items']:yield from additive_leaves(x,M)
 elif op['op']=='transform':yield from additive_leaves(op['shape'],M@np.array(op['matrix']))
 else:yield transform(op,M)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'meshes'/a.candidate/'assembly_recipe.json';records=[]
 for part in json.loads(src.read_text())['parts']:
  if part['group']!='root_integral_bridge':continue
  S=np.linalg.inv(sector(120*part['finger']));w=[]
  for op in additive_leaves(part['shape']):
   body=evaluate(op);body.apply_transform(S);lo,hi=body.bounds;rad=float(np.linalg.norm(np.maximum(np.maximum(lo[:2],-hi[:2]),0)))
   w.append(dict(min_z_mm=float(lo[2]),max_z_mm=float(hi[2]),AABB_radial_lower_mm=rad,strict_excludes_palm_open_interior=bool(hi[2]<=5 or lo[2]>=13 or rad>64)))
  records.append(dict(part=part['name'],witnesses=w,sufficient_exclusion=all(x['strict_excludes_palm_open_interior'] for x in w)))
 d=dict(status='SUFFICIENT_ENVELOPE_DIAGNOSTIC_NOT_BREP_OR_TOLERANCE_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (src,Path(__file__),BASE/'cad/manufacturing_assembly.py')},records=records,scope='Palmopeninterior5<z<13,r<=64. Unionleavesbefore subtractivecuts overapproximate solid. Strict leaf bound belowbottom OR abovetop OR outside radialAABB suffices. No rounding/floor or priorstatus overwrite. Finite mesh envelope only,not BRep/contactpreload/physicalclearance.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(bridges=len(records),unproved=sum(not r['sufficient_exclusion'] for r in records)),indent=2))
if __name__=='__main__':main()
