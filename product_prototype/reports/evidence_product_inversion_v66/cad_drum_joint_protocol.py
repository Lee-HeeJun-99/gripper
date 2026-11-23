"""New finite drum-clamp physical test schema;all measurements remain NULL."""
import argparse,csv,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha
from assembly_recipe_io import resolve_recipe
from joint_bench_protocol import validate_joint_record
from prototype_protocol import measurement_unit

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_root_catalog_drive1045');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case/'assembly_delta_recipe.json';_,hashes=resolve_recipe(src);tests=[
  ('D01','Actual thread/material/dimension inspection',['wire_free_end_diameter_mm','thread_pitch_mm','thread_engagement_mm','pad_thickness_mm'],['thread gauges to supplier-confirmed class','microscope','micrometer'],'Identify purchased lots and confirm actual free-end burr/fray,not nominal0.45wire only. No live motor power.'),
  ('D02','Adjuster rotation/pad force',['screw_rotation_deg','pad_displacement_mm','pad_normal_force_N','residual_wire_flattening_mm'],['calibrated pad force fixture','displacement microscope','angle readout'],'Head has nominal0.4mmfreegap. Do not use bearing-torque/preload formula. Record first-contact origin and fixture compliance independently.'),
  ('D03','Independent c0/c1 pullout and pad stop',['wire_tension_N','wire_slip_mm','pad_drift_mm','permanent_wire_flattening_mm'],['wire load cell','independent optical slip tracking','guarded static fixture'],'c0incomingload positiveY,c1negativeY;do not assume equal sharing. Preregister safe force/slip/damage bounds from real requirements BEFORE test;simulation1.5NisNOTa qualified clamp rating.'),
  ('D04','Release/rethread/repeated exchange',['loosen_rotation_deg','wire_free_end_diameter_mm','pad_escape_mm','nut_escape_mm','cycle_count'],['unpowered service fixture','capture tray','microscope'],'Catch loose pad/nut and record free-end condition after release;do not certify repeatable replacement by geometric reversibility. Stop on strand damage or permanent set.')]
 records=[];plans=[]
 for channel in (0,1):
  for test_id,title,metrics,equipment,procedure in tests:
   ident=f'c{channel}_{test_id}';plans.append(dict(test_id=ident,title=title,channel=channel,equipment=equipment,procedure=procedure,status='NOT RUN',safe_force_limit_N=None,safe_slip_limit_mm=None,physical_qualified_pass=False))
   for metric in metrics:
    r=dict(test_id=ident,metric=metric,value=None,units=measurement_unit(metric),status='NOT MEASURED',origin=None,specimen_id=None,instrument_id=None,calibration_reference=None,actual_time=None,expanded_uncertainty=None,geometry_configuration_sha256=sha(src),material_lot_id=None);validate_joint_record(r);records.append(r)
 with (out/'drum_measurement_template.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows({k:('NULL' if v is None else v) for k,v in r.items()} for r in records)
 for f in (Path(__file__),BASE/'cad/joint_bench_protocol.py',BASE/'cad/prototype_protocol.py',BASE/'cad/assembly_recipe_io.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DRUM_JOINT_TEST_SCHEMA_ALL_NOT_MEASURED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,tests=plans,measurement_fields=records,physical_tests_executed=0,apparatus_available='NOT VERIFIED',physical_service_qualified=False,fabrication_ready=False,scope='New finite dual-drum candidate test matrix,reusing physical provenance/unit/positiveuncertainty/timezone/materiallot guards. Validating templates isNOTexecutingtests or proving authenticity/capacity. No invented measurements,force limits/material/friction/preload or physical PASS. Source geometry is exact parent-hashed current assembly;motor actuation forbidden until fixture/axis/power qualified.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],tests=len(plans),unmeasured_fields=len(records))))
if __name__=='__main__':main()
