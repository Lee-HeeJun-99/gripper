"""Physical prototype test matrix and provenance-safe EMPTY measurement schema.

No hardware is operated or results fabricated. Simulated measurements cannot be
promoted to physical data;unmeasured values remain null,never zero.
"""
import argparse,csv,json,math,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def validate_measurement(record):
 if record['status']=='NOT MEASURED':
  if record['value'] is not None:raise ValueError('unmeasured physical data must remain null')
  return True
 if record['status']!='MEASURED':raise ValueError('per-field records cannot independently declare a physical GatePASS')
 if record.get('origin')!='PHYSICAL':raise ValueError('simulation is not physical measurement')
 if record['value'] is None or not math.isfinite(float(record['value'])):raise ValueError('missing finite actual measurement')
 for key in ('specimen_id','instrument_id','calibration_reference','actual_time','units'):
  if not record.get(key):raise ValueError('missing physical provenance '+key)
 if record.get('expanded_uncertainty') is None or record['expanded_uncertainty']<0:raise ValueError('measurement uncertainty is required')
 return True

def measurement_unit(metric):
 if metric.endswith('_mm_s'):return 'mm/s'
 if metric.endswith('_per_mm'):return '1/mm'
 if metric.endswith('_fraction'):return '1'
 return metric.rsplit('_',1)[-1]

def plans():
 rows=[
 ('P01','Single-finger small-load bending',['tip_displacement_mm','force_N','unloaded_shape_mm'],['calibrated force gauge','camera with scale','thickness gauge'],'clamp5mm;measure force/displacement in both bend directions;do not fit E to an unqualified FEM response'),
 ('P02','Tendon stroke-curvature',['geometric_stroke_mm','cable_tension_N','distributed_curvature_per_mm'],['two independent wire load cells','linear stage/encoder','camera'],'record actual guide path and reel rotation separately;slack/stretch/sliding are not equalized tension'),
 ('P03','Rail-Skin bond and force-displacement',['peel_force_N','bondline_thickness_mm','creep_mm'],['bond coupons','force gauge','microscope'],'PET/TPU and polymer/metal alternatives each get separate specimen IDs;adhesive layer is not zero-thickness'),
 ('P04','Repeated Skin-Rail actuation',['cycle_count','residual_tip_mm','crack_length_mm','force_drift_N'],['repeatable actuator','load cell','camera'],'1000cycle screening target only;not demonstrated fatigue life or reliability rating'),
 ('P05','Skin/object load path',['skin_vertical_load_N','guide_vertical_load_N','object_motion_mm'],['calibrated contact/load sensing','camera','isolated-load-path control fixtures'],'Skin/Guide load fraction needs real sensor calibration or physically justified controls;video alone does not measure force partition'),
 ('P06','Geometry/size generalization',['object_width_mm','object_height_mm','object_depth_mm','object_mass_kg','slip_mm'],['R20/R30 specimens','cylinder','box','scale','camera'],'register material,orientation,initial pose and surface condition;no fragile-damage claim without material strength test'),
 ('P07','50g unsupported Holding',['mass_kg','downward_slip_mm','object_speed_mm_s','support_gap_mm','support_reaction_N','skin_load_fraction'],['calibrated scale','camera','support withdrawal fixture','load-path sensing'],'reuse0.05kg/R30/gravity9.81/assumedmu0.3 simulation protocol as comparator;physical friction must be measured'),
 ('P08','100g unsupported Holding',['mass_kg','downward_slip_mm','object_speed_mm_s','support_gap_mm','skin_load_fraction'],['P07 equipment','75g and100g masses'],'after qualified50g evidence;change mass alone first;no result generated here'),
 ('P09','Lift',['palm_rise_mm','object_rise_mm','relative_slip_mm','cable_tension_N'],['vertical stage','independent palm/object tracking','wire load cells'],'proposed20mm lift target;both palm and object must rise under gravity;not verified by palm command alone'),
 ('P10','Release and Recovery',['contact_end_time_s','residual_tip_mm','shape_error_mm','object_separation_mm'],['camera','wire sensors','shape reference template'],'measure unloading and separation;proposed1mm recovery screen is not an existing GatePASS or full elastic certification')]
 return [dict(test_id=i,test=name,metrics=metrics,equipment_required=equipment,equipment_available='NOT VERIFIED',protocol=protocol,status='NOT RUN',measurements={m:None for m in metrics},physical_qualified_pass=False) for i,name,metrics,equipment,protocol in rows]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tests=plans();fields=[]
 for t in tests:
  for m in t['metrics']:fields.append(dict(test_id=t['test_id'],metric=m,value=None,units=measurement_unit(m),status='NOT MEASURED',origin=None,specimen_id=None,instrument_id=None,calibration_reference=None,actual_time=None,expanded_uncertainty=None))
 for f in fields:validate_measurement(f)
 with (out/'measurement_template.csv').open('w') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(fields[0]));writer.writeheader()
  for row in fields:writer.writerow({k:('NULL' if v is None else v) for k,v in row.items()})
 result=dict(status='PHYSICAL_TEST_PLAN_ONLY_ALL_RESULTS_NOT_MEASURED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),tests=tests,measurement_fields=fields,
             simulation_comparator=dict(hold_window_s=[1.6,2.0],max_downward_slip_mm=2,max_speed_mm_s=5,min_support_gap_mm=5,max_support_reaction_N=1e-5,min_skin_load_fraction=.8,unchanged=True),
             physical_instrument_limit='A0.01N force gauge CANNOTverify1e-5N support reaction;that criterion remains unmeasured/blocked unless load-path removal is independently proven or adequate sensing exists. DoNOTround to0 or relax original simulation Gate.',
             proposed_hardware_extended_hold_s=10,extended_hold_scope='new stronger bench observation target,NOT an old criterion retroactively changed',physical_tests_executed=0)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(tests=len(tests),unmeasured_fields=len(fields),physical_tests_executed=0),indent=2))
if __name__=='__main__':main()
