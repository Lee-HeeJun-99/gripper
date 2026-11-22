"""Read-only measured-evidence gate, not catalog stall-based motor approval."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def qualify(measured):
 required=('continuous_output_torque_Nm','loaded_speed_rpm','required_stroke_mm','thermal_duty_pass','horn_interface_verified','wire_minimum_bend_radius_mm','termination_pullout_N','skin_rail_bond_fatigue_pass')
 missing=[k for k in required if measured.get(k) is None]
 return dict(status='BLOCKED_MISSING_PHYSICAL_COMPONENT_DATA' if missing else 'REQUIRES_ENGINEERING_REVIEW_NOT_AUTOMATIC_APPROVAL',missing=missing,motor_selected=None,material_selected=None)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args();out=BASE/'results'/args.tag;out.mkdir(exist_ok=False)
 source=BASE/'results/product_drive707/summary.json';old=json.loads(source.read_text());catalog=BASE/'config/procurement_candidates_v12.json';data=json.loads(catalog.read_text())
 measured={k:None for k in ('continuous_output_torque_Nm','loaded_speed_rpm','required_stroke_mm','thermal_duty_pass','horn_interface_verified','wire_minimum_bend_radius_mm','termination_pullout_N','skin_rail_bond_fatigue_pass')}
 scenarios=[r for r in old['scenarios'] if r['tension_N_per_wire']==1.5]
 result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (source,catalog)},qualification=qualify(measured),measurements=measured,conditional_torque_range_Nm=[min(r['conditional_design_torque_Nm'] for r in scenarios),max(r['conditional_design_torque_Nm'] for r in scenarios)],candidate_catalog_date=data['checked_date'],scope='Uses existing manufacturer-candidate snapshot and conditional budgets;NO new procurement recommendation, stock verification, purchase or physical experiment. Stall/no-load ratings do not satisfy continuous loaded duty. CAD V21 retains baseline0.5mm wire;0.45mm supplier alternatives require separate geometry.',tests=[dict(case='all_unmeasured_must_block',pass_result=qualify({})['status'].startswith('BLOCKED')),dict(case='zero_not_invented',pass_result=all(v is None for v in measured.values()))])
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['qualification'],indent=2))
if __name__=='__main__':main()
