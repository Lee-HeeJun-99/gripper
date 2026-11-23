"""Compare original versus new distal mating,not prior PASS reclassification."""
import argparse,json,subprocess
from pathlib import Path
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/product_remaining_f2lead975/assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};records=[]
 for finger in range(3):
  for cable in range(2):
   names=[f'f{finger}_c{cable}_s5_'+k for k in ('support','eyelet')];bodies=[evaluate(lookup[n]['shape']) for n in names];h=trimesh.boolean.intersection(bodies,engine='manifold');records.append(dict(parts=names,original_intersection_faces=len(h.faces),original_intersection_mm3=float(h.volume)))
 hashes[str(Path(__file__).relative_to(BASE))]=sha(__file__);hashes['cad/assembly_recipe_io.py']=sha(BASE/'cad/assembly_recipe_io.py');hashes['cad/manufacturing_assembly.py']=sha(BASE/'cad/manufacturing_assembly.py')
 result=dict(status='ORIGINAL_DISTAL_INTERFACE_OVERLAP_DIAGNOSTIC',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,fabrication_ready=False,scope='Original975distalEyelet/Support volumes intersect~2.13mm3 beforeterminalchange. This isNOT newlyintroduced by990exitcut. Sourcegroups neverclaimedactualjointapproval. Preserve allpriorimmutable scopes;no reinterpretation asphysicalbond/pressfit/retention or guidecontactholding. Newseat/keeper/bondwithrealprocessrequired.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
