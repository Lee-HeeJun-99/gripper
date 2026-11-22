"""Sufficient mesh bounds for placed Root/Palm, not a joint or tolerance proof."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sector,transform,sha

def positive_operands(shape):
 if shape['op']=='union':
  for child in shape['items']:yield from positive_operands(child)
 elif shape['op']=='difference':yield from positive_operands(shape['items'][0])
 else:yield shape

def exclusion(bounds):
 lo,hi=np.asarray(bounds,dtype=float)
 if lo.shape!=(3,) or hi.shape!=(3,) or not np.all(np.isfinite([lo,hi])) or np.any(lo>hi):raise ValueError('finite ordered bounds required')
 r=float(np.linalg.norm(np.maximum(np.maximum(lo[:2],-hi[:2]),0)))
 return dict(above=bool(lo[2]>=13),below=bool(hi[2]<=5),outside=bool(r>64),radial_lower_mm=r,
             excludes_open_palm=bool(lo[2]>=13 or hi[2]<=5 or r>64))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic()
 donor=BASE/'results/product_captive_nut941/full_assembly_recipe.json';placed=BASE/'results/product_remaining_lead953/full_assembly_recipe.json'
 d={r['name']:r for r in json.loads(donor.read_text())['parts']};t={r['name']:r for r in json.loads(placed.read_text())['parts']}
 source=d['f0_c0_root_mounted_bridge']['shape'];S=sector(120)
 if t['f1_c0_root_mounted_bridge']['shape']!=transform(source,S):raise ValueError('source/placed CSG identity mismatch')
 if t['palm_bridge_bores']['shape']!=d['palm_bridge_bores']['shape']:raise ValueError('Palm changed')
 palm=t['palm_bridge_bores']['shape']
 while palm['op']=='difference':palm=palm['items'][0]
 if palm!={'op':'cylinder','radius':64,'z':[5,13],'xy':[0,0],'sections':64}:raise ValueError('declared subtractive Palm envelope not proved')
 records=[]
 for i,shape in enumerate(positive_operands(source)):
  b=evaluate(shape).bounds;r=exclusion(b);records.append(dict(operand=i,bounds_mm=b.tolist(),**r))
 result=dict(status='PALM_OPEN_INTERIOR_EXCLUDED_BY_SOURCE_BOUNDS' if all(r['excludes_open_palm'] for r in records) else 'PALM_CERTIFICATE_UNRESOLVED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),donor,placed,BASE/'cad/manufacturing_assembly.py')},records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,actual_joint_strength=None,scope='Declared source CSG exact structural equality before120degsectorplacement. Palm declared cylinderR64/z5..13 has only subtractions. Rotation aboutZ preserves z and radius; each positive operand bound excludes Palm open interior via z>=13 OR z<=5 OR radial lower>64. Difference operands only subtract. Bounds apply to evaluated source operands against declared Palm envelope,NOT floatCSGartifact exclusion/analytic BRep/tolerance/strength/fastenerfit. No zero-volume face deletion,epsilon or old951 status change. Bondline issues remain open.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],operands=len(records)),indent=2))
if __name__=='__main__':main()
