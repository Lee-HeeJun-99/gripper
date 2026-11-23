"""Finite unloaded Rail-clamp disassembly screens;not preload or continuous CCD."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,transform,cyl
from complete_drive_service import axial_sweep
from bridge_assembly_audit import hits

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/'full_assembly_recipe.json';frame=src.parent/'root_frame.json';parts=json.loads(src.read_text())['parts'];solids=[evaluate(p['shape']) for p in parts];lookup={p['name']:p for p in parts};M=np.array(json.loads(frame.read_text()));screw='f0_c1_s0_rail_clamp_screw_PROXY';pad='f0_c1_s0_rail_pressure_pad_RESEARCH';records=[]
 sweep=evaluate(axial_sweep(lookup[screw]['shape'],8));records.append(dict(part=screw,type='EXACT_STEPPED_AXIAL_SWEEP',distance_mm=8.,intersections=hits(sweep,parts,solids,[screw])))
 driver=evaluate(transform(cyl(.8,2.8,12.8,(12,11.5)),M));records.append(dict(part='ASSUMED_driver_shank_R0.8',type='FINITE_STATIC_TOOL_PROXY',intersections=hits(driver,parts,solids,[screw])))
 original=evaluate(lookup[pad]['shape'])
 for distance in (0,.25,.5,1,2,4):
  moved=original.copy();moved.apply_translation(-M[:3,1]*distance);records.append(dict(part=pad,type='SAMPLED_INBOARD_REMOVAL',distance_mm=distance,intersections=hits(moved,parts,solids,[pad,screw])))
 moving=[p for p in parts if p['name'].startswith('f0_c1_s0_') and p['name'] not in (screw,pad)];excluded=[screw,pad,*[p['name'] for p in moving]]
 for distance in (0,.25,.5,1,2,4,8):
  for p in moving:
   moved=evaluate(p['shape']);moved.apply_translation((M[:3,1]+a.longitudinal_ratio*M[:3,0])*distance);records.append(dict(part=p['name'],type='SAMPLED_ASSEMBLY_OUTBOARD_REMOVAL',distance_mm=distance,path_length_mm=distance*np.sqrt(1+a.longitudinal_ratio**2),intersections=hits(moved,parts,solids,excluded)))
 result=dict(status='RAIL_CLAMP_SERVICE_REVIEW_REQUIRED' if any(r['intersections'] for r in records) else 'UNLOADED_RAIL_CLAMP_SERVICE_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,frame,BASE/'cad/complete_drive_service.py',BASE/'cad/bridge_assembly_audit.py')},records=records,moving_subassembly_count=len(moving),runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Explicit UNLOADED service sequence:unthreadwire/unloadactuator,removeclampscrew exact+8mm axial sweep,slidepadinboard6sampledpositions,then7partkeeper/Support/Eyelet assemblyoutboard7sampledpositions. RemainingCADobstacles retained;ownmovingparts excluded because same rigidtranslation. DriverR0.8 isASSUMED,notselectedtool. No hand/thread/preload/reversibility/continuousCCD/deformedfinger/objectclearance or force-transfer qualification.')
 result['longitudinal_ratio']=a.longitudinal_ratio
 if a.longitudinal_ratio:result['scope']+=' Assembly samples use outboard+longitudinal vector with declared ratio;distance_mm is outboardprojection,path_length_mm is actualtranslation length. Not a full trajectory or deformedfinger test.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],blocked=sum(bool(r['intersections']) for r in records),runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_rail_clamp906');p.add_argument('--longitudinal-ratio',type=float,default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.case).name!=a.case or not np.isfinite(a.longitudinal_ratio):p.error('local case and finite ratio required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--longitudinal-ratio',str(a.longitudinal_ratio),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_RAIL_SERVICE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
