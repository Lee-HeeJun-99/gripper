"""Fail-closed dimensional interface contract;catalog compatibility isn't CAD fit."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

REQUIRED=('horn_centre_datum_mm','horn_mount_hole_pattern_mm','mount_thread_engagement_mm','horn_outer_envelope_mm','horn_stack_height_mm','manufacturer_assembly_torque_Nm','validated_motor_body_to_output_axis_transform')
def missing_dimensions(data):return [key for key in REQUIRED if data.get(key) is None]
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'config/motor_horn_interface_v49.json';d=json.loads(src.read_text());missing=missing_dimensions(d)
 result=dict(status='BLOCKED_MOTOR_DIMENSIONAL_INTERFACE' if missing else 'REVIEW_REQUIRED_NOT_AUTOMATIC_FIT_APPROVAL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,BASE/'results/product_drum_contract962/summary.json')},missing_dimensions=missing,catalog_family_compatibility=d['manufacturer_compatibility_only'],existing_drum_bore_D_mm=6.,bore_to_horn_fit_qualified=False,available_CAD_python_modules={x:importlib.util.find_spec(x) is not None for x in ('FreeCAD','OCP','OCC','cadquery')},fabrication_ready=False,STEP_generated=False,actual_motor_test=None,scope='CurrentD6drum bore isgenericresearchhole,not validatedshaft/spline/horn interface. SupplierpackageM2x4doesnotdefineholepitch,direction,engagement or torque. No newguessedpattern/drilledCAD,price/stock/continuousrating or physicalfit supplied. Allrequiredfieldsremainmissing;truefamilycompatibility neverpromoted tofitPASS. Data-presence gate alonewouldnotvalidate dimensions/material/torque;independentCAD/physicalchecks required.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],missing_dimensions=missing),indent=2))
if __name__=='__main__':main()
