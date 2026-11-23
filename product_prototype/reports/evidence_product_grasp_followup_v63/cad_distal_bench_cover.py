"""Actual cover samples after declared whole-cartridge service translation.

This is NOT an operating-gripper clearance or a qualified joint disconnect.
"""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe
from distal_cartridge_service import classify
from distal_keeper_service import intersections

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';prior=BASE/'results'/a.service_case/'summary.json';service=json.loads(prior.read_text());parts,hashes=resolve_recipe(src)
 if any(r['intersections'] for r in service['records']):raise ValueError('prior cartridge samples obstructed')
 if not any(r['distance_mm']==20 for r in service['records']):raise ValueError('20mm cartridge endpoint not recorded')
 if service['input_hashes'].get(str(src.relative_to(BASE)))!=sha(src):raise ValueError('service case does not use same assembly')
 moving,removed,fixed=classify(parts,0)
 if moving!=service['moving_names'] or removed!=service['removed_names']:raise ValueError('service cut-set changed')
 solids={p['name']:evaluate(p['shape']) for p in parts};offset=20*np.asarray(service['extraction_axis_world']);frame=BASE/'results'/a.case/'keeper_frame.json';G=np.asarray(json.loads(frame.read_text()));prefix='f0_c0_s5_';cover=prefix+'keeper_cover';fasteners={prefix+s for s in ('keeper_screw0','keeper_screw1','keeper_nut0','keeper_nut1')}
 for n in moving:solids[n].apply_translation(offset)
 obstacles=[(n,b) for n,b in solids.items() if n not in {cover,*fasteners,*removed}];records=[]
 for distance in (0,.1,.5,1,2,4,8):
  body=solids[cover].copy();body.apply_translation(distance*G[:3,2]);records.append(dict(cover_translation_local_Z_mm=distance,intersections=intersections(body,obstacles)))
 for f in (Path(__file__),prior,frame,BASE/'cad/distal_cartridge_service.py',BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='BENCH_COVER_SAMPLED_REVIEW' if any(r['intersections'] for r in records) else 'BENCH_COVER_SAMPLES_CLEAR_JOINT_SEQUENCE_UNQUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,cartridge_translation_world_mm=offset.tolist(),removed_retaining_bolts=removed,assumed_removed_distal_fasteners=sorted(fasteners),physical_service_qualified=False,actual_joint_cut_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Separate unloaded maintenance geometry: same full cartridge moved20mm along actual carrier axis following1020sampledcut-set. Retained neighbor/Palm/Root hardware all present;only two retaining bolts and four distal fasteners assumed removed by declared sequence. Seven ACTUAL cover positions,not continuous sweep or holding/Native deformation. Root bond/clamp and wire disconnect,physical screws,nut temporary retention,whole tool/hand,and cartridge fixture NOT validated. Original world mating-face hits preserved. No removal of operating collision models.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],hits=[len(r['intersections']) for r in records])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--service-case',default='product_distal_cartridge1020');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case,a.service_case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--service-case',a.service_case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_BENCH_COVER_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
