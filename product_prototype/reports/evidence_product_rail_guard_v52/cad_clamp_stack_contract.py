"""Actual CAD stack closure kinematics, NOT preload or compliant joint physics."""
import argparse,json,subprocess,time,sys
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def closure(seat_top,rail_bottom,skin_top,pad_bottom,pad_top,screw_bottom):
 values=np.array([seat_top,rail_bottom,skin_top,pad_bottom,pad_top,screw_bottom],float)
 if not np.all(np.isfinite(values)):raise ValueError('finite stack coordinates required')
 gaps=[rail_bottom-seat_top,pad_bottom-skin_top,screw_bottom-pad_top]
 if min(gaps)<0:raise ValueError('overlapping stack: closure law inapplicable')
 return dict(lower_seat_rail_gap_mm=gaps[0],skin_pad_gap_mm=gaps[1],pad_screw_gap_mm=gaps[2],pad_thickness_mm=pad_top-pad_bottom,ideal_free_stack_closure_travel_mm=sum(gaps),actual_preload_N=None,actual_joint_stiffness_N_per_mm=None)

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic()
 src=BASE/'results/product_rail_clamp908/full_assembly_recipe.json';frame=src.parent/'root_frame.json';M=np.array(json.loads(frame.read_text()));parts=json.loads(src.read_text())['parts']
 names=['f0_c1_s0_support','f0_rail_right','f0_skin','f0_c1_s0_rail_pressure_pad_RESEARCH','f0_c1_s0_rail_clamp_screw_PROXY'];solids={}
 for part in parts:
  if part['name'] in names:
   mesh=evaluate(part['shape']);mesh.apply_transform(np.linalg.inv(M));solids[part['name']]=mesh
 # Seat is the lower horizontal face in the explicitly declared Root clamp
 # window, NOT the overall Support maximum (which includes web and boss).
 support=solids[names[0]];v=support.vertices;selected=v[(v[:,0]>10.1)&(v[:,0]<13.9)&(v[:,1]>9.5)&(v[:,1]<12.01)&(v[:,2]<-.5)]
 if len(selected)==0:raise ValueError('seat extraction failed; review changed geometry')
 seat=float(selected[:,2].max())
 # Rail and Skin bounds over the entire precurved finger are NOT stack
 # coordinates. Use actual near-Root vertices within the clamp station.
 local={}
 for name in names[1:3]:
  section=solids[name].section(plane_origin=[12,0,0],plane_normal=[1,0,0])
  if section is None:raise ValueError('missing actual Root section')
  v=section.vertices;q=v[v[:,1]>9.5]
  if len(q)==0:raise ValueError('no actual Root stack vertices')
  local[name]=[float(q[:,2].min()),float(q[:,2].max())]
 pad=solids[names[3]].bounds;screw=solids[names[4]].bounds
 r=closure(seat,local[names[1]][0],local[names[2]][1],float(pad[0,2]),float(pad[1,2]),float(screw[0,2]))
 result=dict(status='CAD_FREE_STACK_KINEMATICS_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,frame,BASE/'cad/manufacturing_assembly.py')},measured_CAD_coordinates_mm=dict(seat_top=seat,rail_skin=local,pad_bounds=pad.tolist(),screw_bounds=screw.tolist()),closure=r,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Nominal CAD coordinates;ideal rigid free-stack closure along Rootnormal. Rail/Skin bending, bonded stack constraint, screw thread/pitch/preload, real pad manufacturing, contact pressure and strength are NOT measured or simulated. Required screw travel is NOT a preload command or qualified Native joint. Existing .03mm pad remains research-only.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420)
 (out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_STACK_CONTRACT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
