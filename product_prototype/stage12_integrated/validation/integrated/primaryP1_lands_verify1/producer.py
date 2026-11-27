"""Independent reimported volumetric contact derivative for actual P1 clamp lands."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def main():
 out=ROOT/'validation/integrated/primaryP1_lands_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();rows=[]
 for rev in ('primaryP1_open9','primaryP1_clamp10'):
  src=ROOT/'cad/exports'/rev/'summary.json';d=json.loads(src.read_text());s={n:read(REPO/d['part_references'][n]['path']) for n in ('OPEN_FRAME','MOTOR_CAP','F0_MICRO_MOTOR')};assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
  derivatives=[]
  for eps in (.002,.001):
   derivatives.append(dict(inward_motor_shift_mm=eps,lower_volume_derivative_mm2=common(s['OPEN_FRAME'],translate(s['F0_MICRO_MOTOR'],0,0,-eps))/eps,upper_volume_derivative_mm2=common(s['MOTOR_CAP'],translate(s['F0_MICRO_MOTOR'],0,0,eps))/eps))
  # Restrict to finite planar split rails, excluding pad and vertical wall contacts.
  splitmask=box(5.1,-30,19.8,3.8,15,.6);cap=BRepAlgoAPI_Common(s['MOTOR_CAP'],splitmask).Shape();split_down01=common(s['OPEN_FRAME'],translate(cap,0,0,-.1));split_down025=common(s['OPEN_FRAME'],translate(cap,0,0,-.25))
  rows.append(dict(candidate=ref(src),revision=rev,nominal_motor_frame_overlap_mm3=common(s['F0_MICRO_MOTOR'],s['OPEN_FRAME']),nominal_motor_cap_overlap_mm3=common(s['F0_MICRO_MOTOR'],s['MOTOR_CAP']),derivatives=derivatives,split_rail_down01_intersection_mm3=split_down01,split_rail_down025_intersection_mm3=split_down025))
 old,new=rows;checks=dict(old_land_gap_reproduced=all(abs(x['lower_volume_derivative_mm2'])<1e-8 and abs(x['upper_volume_derivative_mm2'])<1e-8 for x in old['derivatives']),new_actual80mm2_contact_lands=all(abs(x['lower_volume_derivative_mm2']/80-1)<1e-6 and abs(x['upper_volume_derivative_mm2']/80-1)<1e-6 for x in new['derivatives']),nominal_no_motor_volume_overlap=all(r['nominal_motor_frame_overlap_mm3']<1e-8 and r['nominal_motor_cap_overlap_mm3']<1e-8 for r in rows),old_split_bottomeout=old['split_rail_down01_intersection_mm3']>1,new_split_open_01=new['split_rail_down01_intersection_mm3']<1e-8,new_split_closes_025=new['split_rail_down025_intersection_mm3']>1)
 result=dict(status='ACTUAL_P1_CLAMP_LAND_AND_SPLIT_GEOMETRY_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_CLAMP_LAND_VERIFY_FAIL',candidate=new['candidate'],producer=ref(out/'producer.py'),rows=rows,checks=checks,whole_system_release=False,limitations=['Small geometric test translations are not a preload/elastic deformation simulation','Source motor envelope is simplified; actual gearbox-case land location,allowable and tolerances unqualified','No same-revision strength/contact-pressure/global-energy release'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
