"""Fail-closed Stage1 release gate. Geometry PASS is never product release."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'validation/release_revH';out.mkdir(parents=True,exist_ok=False)
 geom=json.loads((ROOT/'cad/exports/revH/audit.json').read_text())
 motion=json.loads((ROOT/'validation/motion_revH_rootdatum_v2/summary.json').read_text())
 service=json.loads((ROOT/'validation/service_revH_completed/summary.json').read_text())
 criteria=dict(real_STEP_STL_files=all((ROOT/f'cad/exports/revH/{p["id"]}.{suffix}').is_file() for p in geom['parts'] for suffix in ('step','stl')),single_valid_BRep_parts=all(p['brep_valid'] and p['solid_count']==1 for p in geom['parts']),nominal_bulk_interference_clear=not geom['collisions'],all_exported_meshes_closed=motion['all_meshes_watertight'],rest_finite_wire_straights_clear=not any(w['hits'] for w in service['straight_REST_wire_spans']),sampled_unloaded_cartridge_cutset_clear=not service['cartridge']['collision_samples'],staged_driver_approach_clear=not any(t['staged_hits'] for t in service['motor_tools']),bearing_axial_retention_complete=False,shaft_drum_torque_lock_complete=False,tendon_retention_complete=False,complete_motion_wire_clearance=False,full_tool_and_thread_interface=False,all_supplier_fits_and_tolerances=False,shop_dimensioned_drawings=False,jamming_extension_interface=False)
 result=dict(status='STAGE1_DESIGN_RELEASE_PASS' if all(criteria.values()) else 'STAGE1_DESIGN_RELEASE_FAIL',criteria=criteria,parts=len(geom['parts']),prescribed_interfinger_clear_sample_range_deg=motion['prescribed_clear_range_deg'],source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hardware_test='NOT MEASURED',Native_run=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2))
 # Part/assembly indices point to REAL generated files rather than duplicating
 # STEP payloads or treating an export recipe as an executed CAD kernel.
 for directory in ('parts','assembly'):(ROOT/'cad'/directory).mkdir(exist_ok=True)
 (ROOT/'cad/parts/index.json').write_text(json.dumps(dict(units='mm',revision='revH',parts=[dict(id=p['id'],STEP=f'../exports/revH/{p["id"]}.step',STL=f'../exports/revH/{p["id"]}.stl') for p in geom['parts']]),indent=2))
 (ROOT/'cad/assembly/index.json').write_text(json.dumps(dict(revision='revH',STEP='../exports/revH/ASSEMBLY.step',STL='../exports/revH/ASSEMBLY.stl',units='mm',axes='Z up; local X radial/Y tangential; angles0/120/240deg; all exported parts in WORLD coordinates',release=False),indent=2))
 for label,target in [('geometry','cad/exports/revH/audit.json'),('motion','validation/motion_revH_rootdatum_v2/summary.json'),('assembly','validation/service_revH_completed/summary.json'),('tolerance','validation/motion_revH_rootdatum_v2/summary.json')]:
  d=ROOT/'validation'/label;d.mkdir(exist_ok=True);(d/'index.json').write_text(json.dumps(dict(evidence=target,sha256=hashlib.sha256((ROOT/target).read_bytes()).hexdigest(),scope='See exact evidence scope; not full release'),indent=2))
 (out/'manifest.json').write_text(json.dumps({str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(ROOT.rglob('*')) if f.is_file() and f!=out/'manifest.json' and '__pycache__' not in str(f)},indent=2))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
