"""Catalog dimensional contract and explicit tolerance arithmetic,not joint physics."""
import argparse,json,subprocess,time,sys,math
from pathlib import Path
from manufacturing_assembly import BASE,sha

def interval_gap(cavity,part):
 if len(cavity)!=2 or len(part)!=2 or not all(math.isfinite(v) for v in [*cavity,*part]) or cavity[0]>cavity[1] or part[0]>part[1]:raise ValueError('finite ordered intervals required')
 return [cavity[0]-part[1],cavity[1]-part[0]]

def contract(cfg):
 s=cfg['screw_candidate'];n=cfg['nut_candidate'];d=cfg['design_targets_NOT_PROCESS_CAPABILITY']
 if (s['nominal_diameter_mm'],s['pitch_mm'],s['right_hand'])!=(n['nominal_diameter_mm'],n['pitch_mm'],n['right_hand']):raise ValueError('incompatible thread designation')
 af=d['pocket_AF_mm'];at=d['pocket_AF_plus_minus_mm'];height=d['pocket_height_mm'];ht=d['pocket_height_plus_minus_mm']
 afgap=interval_gap([af-at,af+at],n['AF_interval_mm']);hgap=interval_gap([height-ht,height+ht],n['height_interval_mm'])
 tip_margin=(d['pad_width_mm']-d['pad_XY_plus_minus_mm'])/2-s['end_diameter_interval_mm'][1]/2-d['axis_position_plus_minus_mm']-d['nominal_axis_to_pad_width_centre_mm']
 return dict(nut_AF_total_clearance_interval_mm=afgap,nut_height_total_clearance_interval_mm=hgap,conditional_tip_to_pad_width_edge_margin_mm=tip_margin,nominal_free_stack_turns=d['nominal_unloaded_stack_travel_mm']/s['pitch_mm'],nominal_free_stack_angle_deg=360*d['nominal_unloaded_stack_travel_mm']/s['pitch_mm'],screw_max_top_mm=d['screw_tip_mm']+s['length_interval_mm'][1],nominal_thread_designation_compatible=True,actual_thread_fit_qualified=False,actual_preload_N=None,actual_torque_Nm=None,geometric_full_nut_rotation_barrier_mm=n['minimum_across_corners_mm']-(af+at),scope='Conditional on declared design manufacturing targets and supplier dimension crosschecks,NOT as-built tolerance or actual thread/proof-load acceptance. Projection/clearance calculations do not measure preload. Nut corner barrier requires retained walls;actual angular backlash/chamfer unspecified.')

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'config/pressure_shoe_fastener_v47.json';cfg=json.loads(src.read_text());detail=contract(cfg)
 result=dict(status='CATALOG_DIMENSIONAL_COMPATIBILITY_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,BASE/'cad/manufacturing_assembly.py')},detail=detail,runtime_s=time.monotonic()-start,physical_measurements_executed=0,fabrication_ready=False,next='Finite cage/screw/tool CAD and real thread/retention/preload/slip/indentation tests. No thread mesh or strength inferred from plain cylinders.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_FASTENER_CONTRACT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
