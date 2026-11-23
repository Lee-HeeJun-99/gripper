"""Finite free-end,actual pad samples and nominal tool access;not pullout proof."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,union
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections
from drum_wire_clamp import radial
from deformed_wire_screen import probes

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';meta=json.loads((src.parent/'summary.json').read_text());spec=BASE/next(k for k in meta['input_hashes'] if k.startswith('config/termination_drum_clamp_'));cfg=json.loads(spec.read_text());fastpath=BASE/'config'/cfg['source_fasteners'];fast=json.loads(fastpath.read_text());parts,hashes=resolve_recipe(src);solids={p['name']:evaluate(p['shape']) for p in parts};pad='f0_c0_drum_pressure_pad';screw='f0_c0_drum_adjuster_M1p6';y=cfg['wire_axis_Y_mm'];z=cfg['wire_axis_Z_mm'];sx=cfg['screw_under_head_X_mm'];s=fast['screw'];head=max(s['head_height_mm']);obstacles=[(n,b) for n,b in solids.items() if n!=screw];records=[]
 key=evaluate(radial((s['hex_AF_mm']/math.sqrt(3))/math.cos(math.pi/64),sx+head-s['nominal_drive_depth_mm'],sx+head+15,y,z));records.append(dict(operation='NOMINAL_KEY_SHANK_ENVELOPE',intersections=intersections(key,obstacles)))
 sweep=evaluate(union(radial(s['diameter_mm']/2,sx-s['nominal_length_mm'],sx+8,y,z),radial(max(s['head_diameter_mm'])/2,sx,sx+head+8,y,z)));records.append(dict(operation='SCREW_CONSERVATIVE_TRANSLATION_ENVELOPE',intersections=intersections(sweep,obstacles)))
 for dy in (0,.1,.5,1,2,4,6):
  body=solids[pad].copy();body.apply_translation([0,dy,0]);records.append(dict(operation='ACTUAL_PAD_TRANSLATION_SAMPLED_ONLY',translation_Y_mm=dy,intersections=intersections(body,[(n,b) for n,b in solids.items() if n not in {pad,screw}])) )
 wire=[];route=np.array([[cfg['wire_axis_X_mm'],0,z],[cfg['wire_axis_X_mm'],-6,z]])
 for index,probe in probes(route,.22522275007459786):
  wire.append(dict(sample=index,intersections=intersections(probe,list(solids.items()))))
 for f in (Path(__file__),spec,fastpath,src.parent/'summary.json',BASE/'cad/drum_wire_clamp.py',BASE/'cad/deformed_wire_screen.py',BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DRUM_CLAMP_SERVICE_REVIEW' if any(r['intersections'] for r in records+wire) else 'ONE_UNLOADED_DRUM_PAD_TOOL_AND_WIRE_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,service_records=records,free_end_wire_records=wire,free_end_reference_route_mm=route.tolist(),wire_envelope_radius_mm=.22522275007459786,actual_pullout_N=None,actual_preload_N=None,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='One radial c0 clamp inREST. Wire centreline straight6mm from savedlead endpoint[50,0,56.75] along negativeY,not a measured bent/frayed/loaded wire. Finite capsule reference0.45mm plus existing sagitta budget;no physical thread/contact/friction. Nominal key shank and conservative screw translation contain finite geometry,not whole tool/hand/helical thread fit. Pad translates after screw removal,seven ACTUAL samples,not continuous CCD. All remaining hardware retained;no loaded clamping or pullout,wire damage/force or Native/holding qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],pad_hits=[len(r['intersections']) for r in records if r['operation']=='ACTUAL_PAD_TRANSLATION_SAMPLED_ONLY'])))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_drum_wire_clamp1035');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_DRUM_SERVICE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
