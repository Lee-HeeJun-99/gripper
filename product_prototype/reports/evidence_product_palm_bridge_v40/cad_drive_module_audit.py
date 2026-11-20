"""Complete pair check across54finite unmounted modules,not product qualification."""
import argparse,csv,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();names=['b3_lead_pulley_modules_v22','b3_pulley_fork_modules_v23'];parts=[];shapes=[];inputs={};saved=[]
 for name in names:
  folder=BASE/'meshes'/name;src=folder/'assembly_recipe.json';inputs[str(src.relative_to(BASE.parent))]=sha(src)
  for part in json.loads(src.read_text())['parts']:
   shape=evaluate(part['shape']);parts.append(part);shapes.append(shape);file=folder/(part['name']+'.stl');read=trimesh.load_mesh(file)
   if not read.is_volume or read.body_count!=1:raise ValueError('actual module STLreadback invalid')
   saved.append(dict(part=part['name'],source_STL_sha256=sha(file),closed_positive_singlebody=True))
 hits=[];evaluated=0
 for i,left in enumerate(shapes):
  for j in range(i+1,len(shapes)):
   right=shapes[j]
   if np.any(np.minimum(left.bounds[1],right.bounds[1])-np.maximum(left.bounds[0],right.bounds[0])<=0):continue
   evaluated+=1;hit=trimesh.boolean.intersection([left,right],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[parts[i]['name'],parts[j]['name']],signed_volume_mm3=float(hit.volume)))
 with (out/'MODULE_BOM.csv').open('w') as stream:
  w=csv.writer(stream);w.writerow(['part','quantity','material','status','mass_kg','unit_cost_KRW']);w.writerow(['turn pulley',18,'UNSELECTED','UNMOUNTED_DESIGN','NULL','NULL']);w.writerow(['fork',18,'UNSELECTED','UNMOUNTED_DESIGN','NULL','NULL']);w.writerow(['pin proxy',18,'UNSELECTED','RETENTION_BEARING_UNVERIFIED','NULL','NULL']);w.writerow(['Palm mounting bridges / fasteners','TBD','UNSELECTED','NOT_MODELED','NULL','NULL'])
 result=dict(status='UNMOUNTED_MODULE_PAIR_SCREEN_NOT_PRODUCT_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes=inputs,actual_STL_readbacks=saved,module_count=len(parts),possible_pairs=len(parts)*(len(parts)-1)//2,Boolean_evaluated_pairs=evaluated,nonempty_intersections=hits,runtime_s=time.monotonic()-start,full_drive_assembly=False,scope='Fills wheel-wheel pair gap left by751/754;also cross-checks all finite54modules andsavedSTLs. Unmounted manufactured reference pose only. No Palmbridges/rootredirect/retention/bearings,continuousCCD,tolerances,materialstrength or physicalassemblyPASS.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(modules=len(parts),possible_pairs=result['possible_pairs'],nonempty=len(hits),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
