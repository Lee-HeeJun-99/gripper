"""Explicit common-frame shoulder-plane proof;not floating CSG or load certification."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_distal_seat992/assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};records=[]
 for finger in range(3):
  for cable in range(2):
   prefix=f'f{finger}_c{cable}';eye=lookup[prefix+'_s5_eyelet']['shape'];G=np.eye(4)
   while eye['op']=='transform':G=G@np.asarray(eye['matrix']);eye=eye['shape']
   end=float(evaluate(eye).bounds[1,0]);term=lookup[prefix+'_distal_NI000001_MAX_ENVELOPE']['shape'];R=np.eye(4);R[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]]
   if term['op']!='transform' or not np.array_equal(term['matrix'],G@R):raise ValueError('common frame identity mismatch')
   op=term['shape']
   if op['op']!='cylinder' or op['z'][0]!=end or op['xy']!=[0,0]:raise ValueError('shoulder cylinder identity mismatch')
   records.append(dict(pair=[prefix+'_s5_eyelet',prefix+'_distal_NI000001_MAX_ENVELOPE'],Eyelet_local_X_upper_mm=end,terminal_local_X_lower_mm=op['z'][0],open_interiors_excluded=bool(op['z'][0]>=end)))
 hashes['cad/terminal_mating_certificate.py']=sha(__file__);hashes['cad/assembly_recipe_io.py']=sha(BASE/'cad/assembly_recipe_io.py');hashes['cad/manufacturing_assembly.py']=sha(BASE/'cad/manufacturing_assembly.py')
 result=dict(status='COMMON_SHOULDER_PLANE_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,fabrication_ready=False,scope='Same declaredGframe,Eyelet source meshx<=1 andcylinder constructx>=1 exclude OPENinteriors in exact rigidmath. DoesNOT erase actualfloatingCSGsmallvolume/faces from989/992,prove numericalBRep/actualfit/matingforce/strength/preload/tolerance or adoption. No force/contactarea/physicalswagecapacity invented.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],pairs=len(records)),indent=2))
if __name__=='__main__':main()
