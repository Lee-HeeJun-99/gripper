"""Independent bounded replacement proof, not re-running unchanged coupons."""
import argparse,json,math,shutil
import trimesh
from incremental_stage1 import ROOT,read,bounds,common,sha
from build_stage1 import cyl,cut,volume
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--base',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';base=ROOT/'cad/exports'/a.base/'summary.json';idx=json.loads(src.read_text());old=json.loads(base.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 changed=[n for n,v in idx['parts'].items() if v['sha256']!=old['parts'][n]['sha256']];assert set(changed)=={'F0_MOTOR','F1_MOTOR','F2_MOTOR'}
 motors={n:read(ROOT/idx['parts'][n]['path']) for n in changed};mb={n:bounds(s) for n,s in motors.items()};quality=[]
 for n in changed:
  f=ROOT/idx['parts'][n]['path'];m=trimesh.load(f.with_suffix('.stl'),force='mesh');quality.append(dict(part=n,closed_positive_mesh=bool(m.is_volume)))
 # All points of prescribed moving laminate/tip have |X|<=54.05, |Y|<=13.5.
 # Terminal expression decreases with closure0..60deg; swivel bound uses
 # P_X<=43, |dx|<=6, dz<=20, beta<=14.585deg. R57 is conservative.
 b=mb['F0_MOTOR'];radial_lower=math.hypot(b[0],abs(b[4]));moving_bound=57
 # Entire finite wire remains X>5, |Y|<=0.32 in localF0. Other sectors
 # rotate both motors and wire by120deg. Actual motor boxes prove separation.
 planar_wire_clear=b[4]<-.32 and mb['F1_MOTOR'][1]>.32 and mb['F2_MOTOR'][3]<5
 # Full-turn coupling annulus contains all actual six coupling members.
 ann=cut(cyl(12.6,(80,-32,20),19.8,(0,1,0)),cyl(2.525,(80,-32.1,20),20,(0,1,0)))
 containment=[]
 for n,v in idx['parts'].items():
  if n.startswith('F0_COUPLING'):containment.append(dict(part=n,excess_mm3=volume(cut(read(ROOT/v['path']),ann))))
 intersections=[dict(motor=n,full_turn_coupling_envelope_mm3=common(ann,s)) for n,s in motors.items()]
 spec=idx['design_geometry']['motor_spec'];actual_shaft=read(ROOT/idx['parts']['F0_SHAFT']['path']);gap=bounds(actual_shaft)[1]-b[4]
 fit=dict(motor=spec['model'],model_is_maximum_envelope=True,maximum_pilot_height_mm=2.5,minimum_plate_mm=2.9,pilot_axial_margin_mm=.4,minimum_pilot_hole_mm=22.45,maximum_pilot_D_mm=22,pilot_radial_margin_mm=.225,minimum_screw_hole_mm=3.55,screw_major_max_mm=3,corner_pitch_error_mm=math.sqrt(2)*.1,machining_position_error_bound_mm=math.sqrt(2)*.05,corner_pitch_radial_margin_mm=(3.55-3)/2-math.sqrt(2)*(.1+.05),mount_screw_engagement_mm=[2.8,3.2],mount_thread_depth_min_mm=4.5,screw_bottom_margin_mm=1.3,actual_CAD_maxshaft_gap_mm=gap,physical_spec_gap_mm=[1,3],minimum_input_grip_mm=11,output_grip_mm=5.8,actual_hardware='NOT MEASURED; shaft/pilot incoming inspection and alignment mandatory')
 passed=all(r['closed_positive_mesh'] for r in quality) and radial_lower>moving_bound and planar_wire_clear and all(abs(r['excess_mm3'])<1e-7 for r in containment) and all(abs(r['full_turn_coupling_envelope_mm3'])<1e-7 for r in intersections) and abs(gap-1)<1e-6 and fit['corner_pitch_radial_margin_mm']>0
 result=dict(status='MOTOR_REPLACEMENT_GEOMETRY_TRANSFER_PASS' if passed else 'FAIL',changed_parts=changed,unchanged_parts=len(idx['parts'])-len(changed),mesh_checks=quality,motor_bounds_mm=mb,motor_radial_lower_bound_mm=radial_lower,prescribed_moving_Finger_radial_bound_mm=moving_bound,planar_wire_separation=planar_wire_clear,coupling_containment=containment,new_motor_coupling_full_turn=intersections,interface_fit=fit,input_sha256={str(src.relative_to(ROOT)):sha(src),str(base.relative_to(ROOT)):sha(base)},scope='Only unchanged nominal geometry evidence transfers from base. Explicit bounds for prescribed0..60deg family, not arbitrary physical FEM motion. Manufacturer dimensions, not actual hardware/temperature/torque/driver qualification.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],changed=changed,radial_lower_mm=radial_lower,wire_separate=planar_wire_clear,shaft_gap_mm=gap,corner_margin_mm=fit['corner_pitch_radial_margin_mm'])))
if __name__=='__main__':main()
