"""New captive clamp bench protocol,using existing physical-provenance guard.

No hardware operated;NULL measurements are never substituted by simulation.
"""
import argparse,csv,json,math,subprocess,sys,time
from datetime import datetime
from pathlib import Path
from manufacturing_assembly import BASE,sha
from prototype_protocol import validate_measurement,measurement_unit

def validate_joint_record(record):
 validate_measurement(record)
 if record['units']!=measurement_unit(record['metric']):raise ValueError('metric/unit mismatch')
 if record['status']=='MEASURED':
  u=float(record['expanded_uncertainty'])
  if not math.isfinite(u) or u<=0:raise ValueError('positive finite physical uncertainty required')
  stamp=datetime.fromisoformat(record['actual_time'])
  if stamp.tzinfo is None:raise ValueError('physical timestamp timezone required')
  if not record.get('geometry_configuration_sha256') or not record.get('material_lot_id'):raise ValueError('actual geometry/material lot required')
 return True

def plans():
 rows=[
 ('J01','Dimensional and thread inspection',['thread_pitch_mm','shoe_thickness_mm','pocket_AF_mm','burr_height_mm'],['thread ring/plug gauges to supplier-confirmed class','micrometer','microscope'],'Confirm actual thread class first;catalog designation and smooth envelope are NOT gauging acceptance.'),
 ('J02','Adjuster rotation versus actual preload',['screw_rotation_deg','preload_N','stack_displacement_mm','residual_indent_mm'],['calibrated load cell','angular encoder','displacement gauge','fixture compliance calibration'],'Record loading/unloading;do not derive preload from .07mmgap or72deg free-stack reference. Keep first-contact origin separate from tightened position.'),
 ('J03','Joint lateral load and slip',['force_x_N','force_y_N','preload_N','slip_x_mm','slip_y_mm'],['bidirectional calibrated force fixture','independent optical slip tracking'],'Apply measured loads to Eyelet/Support without moving fixedRoot. Load limits/slip limits require preregistration from real design requirements,not guessed GatePASS.'),
 ('J04','Eccentric force and root moment',['force_N','lever_arm_mm','moment_Nm','slip_mm','rail_bending_mm'],['measured lever fixture','load cell','root reaction measurement'],'Measure actual line of action;guide-centre point-force reference omits distributed bore/friction couple. Do not call fixture displacement joint slip without subtracting fixture compliance.'),
 ('J05','Unload and repeated cartridge exchange',['cycle_count','preload_N','residual_indent_mm','shoe_drift_mm','crack_length_mm'],['cycle counter','microscope','load cell'],'Record every assembly preload/material lot;no claimed fatigue life or zero damage. Stop on permanentcrease/crack/slip beyond preregistered safe bounds.'),
 ('J06','Nut and screw retention',['orientation_deg','screw_rotation_deg','nut_escape_mm','screw_escape_mm'],['unloaded inversion fixture','camera','manual tool'],'Test unpowered/unloaded orientation changes and repeat service. Geometric cage stop is NOT thread selflocking or retention under vibration.')]
 return [dict(test_id=i,title=t,metrics=m,equipment=e,procedure=p,status='NOT RUN',physical_measurements={k:None for k in m},preregistered_load_limit=None,preregistered_slip_limit=None,physical_qualified_pass=False) for i,t,m,e,p in rows]

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();spec=BASE/'config/pressure_shoe_fastener_v47.json';assembly=BASE/'results/product_captive_nut941/full_assembly_recipe.json';rows=[];tests=plans()
 for t in tests:
  for metric in t['metrics']:
   r=dict(test_id=t['test_id'],metric=metric,value=None,units=measurement_unit(metric),status='NOT MEASURED',origin=None,specimen_id=None,instrument_id=None,calibration_reference=None,actual_time=None,expanded_uncertainty=None,geometry_configuration_sha256=sha(assembly),material_lot_id=None)
   validate_joint_record(r);rows.append(r)
 with (out/'joint_measurement_template.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows({k:'NULL' if v is None else v for k,v in r.items()} for r in rows)
 result=dict(status='JOINT_BENCH_PROTOCOL_NOT_MEASURED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),spec,assembly,BASE/'cad/prototype_protocol.py')},tests=tests,measurement_fields=rows,physical_tests_executed=0,apparatus_available='NOT VERIFIED',runtime_s=time.monotonic()-start,fabrication_ready=False,scope='New finite941clamp testplan reuses existing validate_measurement;adds unit/positivefiniteuncertainty/timezone/actualgeometry/materiallot guards. Validating declared provenance cannot independently prove data authenticity or product PASS. No fabricated measurement,preload/friction/material or fatiguevalue.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],tests=len(tests),fields=len(rows)),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_JOINT_PROTOCOL_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
