"""Refine ONLY actual convex-hull hit pairs with existing surface translation tool."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe
from rail_continuous_service import surface_sweep
from distal_keeper_service import intersections

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;prior=BASE/'results'/a.sweep_case/'summary.json';sweep=json.loads(prior.read_text());src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src)
 if not sweep.get('continuous_convex_envelopes'):raise ValueError('requires actual envelope study')
 if sweep['input_hashes'].get(str(src.relative_to(BASE)))!=sha(src):raise ValueError('same recipe identity required')
 lookup={p['name']:p for p in parts};records=[];delta=20*np.asarray(sweep['extraction_axis_world']);pairs=sweep['records'][0]['intersections']
 for pair in pairs:
  moving=pair['moving_part'];fixed=pair['part']
  if moving not in sweep['moving_names'] or fixed not in sweep['fixed_names']:raise ValueError('prior pair outside cut-set')
  m=evaluate(lookup[moving]['shape']);obstacles=[(fixed,evaluate(lookup[fixed]['shape']))];detail=surface_sweep(m,delta,obstacles);detail['initial_intersections']=intersections(m,obstacles);records.append(dict(moving=moving,fixed=fixed,detail=detail))
 unresolved=any(r['detail']['intersections'] or r['detail']['initial_intersections'] or r['detail']['unresolved_prisms'] for r in records)
 for f in (Path(__file__),prior,BASE/'cad/rail_continuous_service.py',BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='CARTRIDGE_SURFACE_SWEEP_REVIEW' if unresolved else 'NO_POSITIVE_VOLUME_HIT_IN_HULL_PAIR_SURFACE_REFINEMENT_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,prior_hit_pairs=len(pairs),physical_service_qualified=False,actual_joint_cut_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Refines only existing1022hull-hitpairs with actual original solid and per-triangle continuous translation prisms. Concave convex-hull warning not reclassified without evidence. Zero-volume collapsed swept faces counted,not thickened;unresolved numerical prisms preserved. NOT exact/no-touch CCD certificate or full cartridge sequence/Root joint disconnect/Native/physical retention/STEP qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],pairs=len(pairs))))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--sweep-case',default='product_distal_cartridge_sweep1022');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case,a.sweep_case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--sweep-case',a.sweep_case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CARTRIDGE_REFINEMENT_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
