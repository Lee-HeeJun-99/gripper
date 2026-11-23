"""Actual current cartridge cut-set diagnostic,not operating gripper motion.

An unqualified joint cut cannot certify physical disassembly even if CAD clears.
"""
import argparse,json,re,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def classify(parts,finger):
 prefix=f'f{finger}';moving=[];removed=[];fixed=[]
 for p in parts:
  n=p['name']
  if n in {prefix+'_retaining_bolt_-14',prefix+'_retaining_bolt_14'}:removed.append(n)
  elif n in {prefix+s for s in ('_carrier','_root_clamp','_skin','_rail_left','_rail_right')} or re.fullmatch(prefix+r'_c[01]_s[0-5]_.+',n) or re.fullmatch(prefix+r'_c[01]_distal_.+',n) or re.fullmatch(prefix+r'_(clamp_(bolt|nut)|retaining_nut)_(-14|14)',n):moving.append(n)
  else:fixed.append(n)
 if len(removed)!=2 or prefix+'_carrier' not in moving:raise ValueError('explicit carrier/retaining hardware absent')
 return moving,removed,fixed

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);moving,removed,fixed=classify(parts,a.finger);lookup={p['name']:p for p in parts};carrier=lookup[f'f{a.finger}_carrier']['shape']
 if carrier['op']!='transform':raise ValueError('actual carrier datum required')
 G=np.asarray(carrier['matrix']);axis=G[:3,0]
 if not np.isclose(np.linalg.norm(axis),1,atol=1e-12):raise ValueError('invalid extraction axis')
 solids={p['name']:evaluate(p['shape']) for p in parts};obstacles=[(n,solids[n]) for n in fixed];records=[]
 for distance in ((20,) if a.continuous_envelope else (0,.1,.5,1,2,5,10,20)):
  hits=[]
  for name in moving:
   if a.continuous_envelope:
    from rail_continuous_service import envelope
    body=envelope(solids[name],distance*axis)
   else:
    body=solids[name].copy();body.apply_translation(distance*axis)
   for h in intersections(body,obstacles):hits.append(dict(moving_part=name,**h))
  records.append(dict(distance_mm=distance,translation_world_mm=(distance*axis).tolist(),intersections=hits))
 for f in (Path(__file__),BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='CARTRIDGE_SERVICE_SAMPLED_OBSTRUCTION' if any(r['intersections'] for r in records) else 'CARTRIDGE_SERVICE_SAMPLES_CLEAR_JOINT_CUT_UNQUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,moving_names=moving,removed_names=removed,fixed_names=fixed,assembly_part_count=len(parts),extraction_axis_world=axis.tolist(),actual_joint_cut_qualified=False,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Separate UNLOADED SERVICE diagnostic: object absent,wire disconnected,two retaining bolts assumed removed. All other CAD parts retained and explicitly partitioned. Guide stations/retaining nuts travel with cartridge;Root bridges/pins/turns/motor/Palm and other fingers remain fixed. Pressure-clamp/bond/Root disconnect operations NOT validated. Uses actual carrier longitudinal axis,not moving object or disabling operating collision. Eight actual rigid CAD positions,not continuous CCD/Native deformation or certified assembly order. Any hit retained including coplanar artifacts.')
 result['continuous_convex_envelopes']=a.continuous_envelope
 if a.continuous_envelope:
  result['status']='CARTRIDGE_CONVEX_SWEEP_REVIEW' if any(r['intersections'] for r in records) else 'CARTRIDGE_CONVEX_SWEEP_CLEAR_JOINT_CUT_UNQUALIFIED'
  result['scope']='Same explicit UNLOADED SERVICE cut-set;20mm continuous conservative convex envelopes,not eight samples. Each hull contains all intermediate rigid translations but fills concavities: hits unresolved,not actual collision proof. CAD floating CSG is not exact no-touch certification. Physical joint disconnect/retaining screw access/wire disconnection and tool/grasp capability NOT qualified. Not Native/holding/fabrication approval.'
  result['input_hashes']['cad/rail_continuous_service.py']=sha(BASE/'cad/rail_continuous_service.py')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],hit_counts=[len(r['intersections']) for r in records])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--finger',type=int,choices=(0,1,2),default=0);p.add_argument('--continuous-envelope',action='store_true');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--worker']+(['--continuous-envelope'] if a.continuous_envelope else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CARTRIDGE_SERVICE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
