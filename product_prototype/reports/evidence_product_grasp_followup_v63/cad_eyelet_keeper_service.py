"""Keeper-specific finite service sequence;not hand/tool/thread or continuous cover CCD."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,cut,transform
from complete_drive_service import axial_sweep
from bridge_assembly_audit import hits

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_eyelet_keeper894/full_assembly_recipe.json';parts=json.loads(src.read_text())['parts'];solids=[evaluate(p['shape']) for p in parts];lookup={p['name']:p for p in parts};records=[];fasteners=[f'f0_c1_s0_keeper_{kind}{k}' for kind in ('screw','nut') for k in (0,1)]
 for k in (0,1):
  nut=lookup[f'f0_c1_s0_keeper_nut{k}'];M=np.array(nut['shape']['matrix']);swept=evaluate(transform(cut(cyl(1.1,-11.35,-2.35,sections=6),cyl(.55,-11.5,-2.2)),M));records.append(dict(part=nut['name'],type='EXACT_HEX_ANNULUS_AXIAL_SWEEP',distance_mm=-8.,intersections=hits(swept,parts,solids,[nut['name']])))
 for k in (0,1):
  screw=lookup[f'f0_c1_s0_keeper_screw{k}'];swept=evaluate(axial_sweep(screw['shape'],8));records.append(dict(part=screw['name'],type='EXACT_STEPPED_CYLINDER_AXIAL_SWEEP',distance_mm=8.,intersections=hits(swept,parts,solids,[screw['name'],*fasteners[2:]])))
 H=np.array(json.loads((src.parent/'keeper_frame.json').read_text()));direction=H[:3,1]
 for name,removed in [('f0_c1_s0_keeper_cover',fasteners),('f0_c1_s0_eyelet',fasteners+['f0_c1_s0_keeper_cover'])]:
  original=evaluate(lookup[name]['shape'])
  for distance in (0,.25,.5,1,2,4,8):
   moved=original.copy();moved.apply_translation(direction*distance);records.append(dict(part=name,type='SAMPLED_NOT_CONTINUOUS_CLEARANCE',distance_mm=distance,intersections=hits(moved,parts,solids,[name,*removed])))
 result=dict(status='KEEPER_SERVICE_REVIEW_REQUIRED' if any(r['intersections'] for r in records) else 'NOMINAL_KEEPER_SERVICE_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,src.parent/'keeper_frame.json',BASE/'cad/complete_drive_service.py',BASE/'cad/bridge_assembly_audit.py')},records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE keeper sequence:nuts exactnegative8mm sweep with screws retained,then screws exactpositive8mm sweep after nutsremoved,then cover/eyelet7sampledpositions each. Actual finite286part obstacles retained except declared disassembly order. Actuator unloaded and wire unthreaded BEFORE eyelet removal;wire not part of this hardware-only service scene. No hand/tool/thread/preload/tolerance,continuous cover/eyelet CCD,skin strength or actual assembly qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],blocked=sum(bool(r['intersections']) for r in records),runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_KEEPER_SERVICE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
