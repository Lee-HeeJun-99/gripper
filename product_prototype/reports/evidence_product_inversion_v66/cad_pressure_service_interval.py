"""Nominal CAD nut-service displacement window,not physical tolerances/CCD."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def travel_window(nut_x,clamp_max_x,mouth_x):
 lo=float(nut_x[1]-mouth_x);hi=float(nut_x[0]-clamp_max_x)
 if not np.all(np.isfinite([*nut_x,clamp_max_x,mouth_x])) or nut_x[0]>=nut_x[1]:raise ValueError('finite ordered geometry required')
 return dict(minimum_nut_rootward_travel_to_clear_mouth_mm=lo,maximum_travel_before_root_clamp_AABB_mm=hi,nominal_window_exists=hi>lo,midpoint_travel_mm=(lo+hi)/2 if hi>lo else None,midpoint_end_margin_mm=(hi-lo)/2 if hi>lo else None)
def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_captive_nut941/full_assembly_recipe.json';frame=src.parent/'root_frame.json';M=np.asarray(json.loads(frame.read_text()));parts=json.loads(src.read_text())['parts'];b={}
 for name in ('f0_c1_s0_pressure_captive_nut_M1p6','f0_root_clamp'):
  mesh=evaluate(next(p['shape'] for p in parts if p['name']==name));mesh.apply_transform(np.linalg.inv(M));b[name]=mesh.bounds
 nut_x=b['f0_c1_s0_pressure_captive_nut_M1p6'][:,0];root_x=float(b['f0_root_clamp'][1,0]);detail=travel_window(nut_x,root_x,9.4)
 result=dict(status='NOMINAL_DISASSEMBLY_WINDOW_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,frame,BASE/'cad/pressure_captive_nut.py',BASE/'cad/manufacturing_assembly.py')},actual_Root_frame_bounds_mm={k:v.tolist() for k,v in b.items()},declared_cage_mouth_x_mm=9.4,detail=detail,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Bounds of actual941nut/RootClamp and explicit designedcagemouth. Interval is necessary nominal geometry for fullnutexit vsRootClampAABB,not allobstacle or continuouspath proof. Verify chosen travel with finite sweep;real tolerance/hand access/retention not measured.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_SERVICE_INTERVAL_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
