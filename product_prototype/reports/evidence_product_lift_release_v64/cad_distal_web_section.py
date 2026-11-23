"""Local line-section material thickness,not global minimum wall/strength."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def line_intervals(body,x):
 s=body.section(plane_origin=[x,0,0],plane_normal=[1,0,0])
 if s is None:return []
 z=[]
 for loop in s.discrete:
  for a,b in zip(loop[:-1],loop[1:]):
   if (a[1]<=0<b[1]) or (b[1]<=0<a[1]):
    t=-a[1]/(b[1]-a[1]);z.append(float(a[2]+t*(b[2]-a[2])))
 z.sort()
 if len(z)%2:raise ValueError('unresolved odd section intersections')
 return [z[i:i+2] for i in range(0,len(z),2)]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_seat992');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);original=BASE/'results/product_remaining_f2lead975/assembly_delta_recipe.json';candidate=BASE/'results'/a.case/'assembly_delta_recipe.json';records=[];hashes={}
 for label,src in [('original',original),('candidate',candidate)]:
  parts,hh=resolve_recipe(src);hashes.update(hh);lookup={r['name']:r for r in parts};op=lookup['f0_c0_s5_eyelet']['shape'];G=np.eye(4)
  while op['op']=='transform':G=G@np.asarray(op['matrix']);op=op['shape']
  body=evaluate(lookup['f0_c0_s5_support']['shape']);body.apply_transform(np.linalg.inv(G))
  for x in (-.5,0.,.5,1.5):
   intervals=line_intervals(body,x);records.append(dict(model=label,Eyelet_local_X_mm=x,Eyelet_local_Y_mm=0,z_intervals_mm=intervals,total_Z_material_thickness_mm=sum(b-a for a,b in intervals)))
 for f in (Path(__file__),BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='LOCAL_WEB_SECTION_REFERENCE_NOT_STRENGTH',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,fabrication_ready=False,actual_strength_N=None,scope='ActualRESTf0c0Supportsections4linesONLYinEyeletframe,Y0,Zmaterialintervals. NOTminimumoverwholepart/mesherrorbound/manufacturingcapability or load/stressqualification. Originalinterpenetration isNOTrealbearing/supportstrength. Newsocketunselectedbond/keeperstillrequired;NOabsolute-thicknessPASSthreshold invented.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
