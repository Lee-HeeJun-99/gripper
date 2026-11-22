"""Finite hex-pock​​et rotation/bearing geometry only;not preload or torque capacity."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,cut,transform
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);folder=src.parent;meta=json.loads((folder/'summary.json').read_text());cfgpath=BASE/meta['configuration'];cfg=json.loads(cfgpath.read_text());G=np.asarray(json.loads((folder/'keeper_frame.json').read_text()));support=next(p for p in parts if p['name']=='f0_c0_s5_support');body=evaluate(transform(support['shape'],np.linalg.inv(G)));d=cfg['design'];records=[]
 for bolt,(x,y) in enumerate(d['bolt_centres_XY_mm']):
  for AF in cfg['nut']['AF_mm']:
   nb=d['nut_bottom_Z_mm'];nt=nb+max(cfg['nut']['height_mm']);shape=cut(cyl(AF/math.sqrt(3),nb,nt,(x,y),sections=6),cyl(.81,nb-.1,nt+.1,(x,y)))
   for angle in (0,3,5,10,15,30):
    R=trimesh.transformations.rotation_matrix(math.radians(angle),[0,0,1],[x,y,0]);nut=evaluate(transform(shape,R));records.append(dict(bolt=bolt,nut_AF_mm=AF,rotation_deg=angle,intersections=intersections(nut,[(support['name'],body)])))
 bearing=dict(nominal_nut_top_Z_mm=d['nut_bottom_Z_mm']+max(cfg['nut']['height_mm']),roof_Z_mm=d['nut_pocket_Z_mm'][1],under_head_Z_mm=d['cap_wing_top_Z_mm'],screw_nominal_length_mm=cfg['screw']['nominal_length_mm'])
 bearing['unloaded_roof_gap_mm']=bearing['roof_Z_mm']-bearing['nominal_nut_top_Z_mm'];bearing['nominal_closed_grip_to_nut_top_mm']=bearing['under_head_Z_mm']-bearing['roof_Z_mm'];bearing['nominal_full_engagement_length_mm']=max(cfg['nut']['height_mm']);bearing['nominal_tip_exposure_after_gap_closure_mm']=bearing['screw_nominal_length_mm']-bearing['nominal_closed_grip_to_nut_top_mm']-bearing['nominal_full_engagement_length_mm']
 for f in (Path(__file__),cfgpath,folder/'keeper_frame.json',BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='HEX_ROTATION_AND_NOMINAL_GRIP_REFERENCE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,rotation_samples=records,bearing_reference=bearing,actual_preload_N=None,actual_thread_strength_N=None,actual_retention_N=None,actual_locking_or_torque_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Both catalog AF extremes,nominal smooth nut bore/maxheight,actual retained Support CAD. Positive intersections show geometric rotation obstruction at selected angles,not exact backlash limit,material deformation/self-locking/torque capacity or tolerance qualification. Bottom-loaded nut can fall when bolt removed. Nominal loaded grip is arithmetic only;no accepted loaded position/force imposed. Screw length tolerance/thread runout/chamfer/actual thread fit unverified;do not prescribe torque or preload.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_NUT_CAPTURE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
