"""Hash new intermediate CAD/raw artifacts without tracking bulk duplicates.
No artifact is removed or rewritten. Final AI/AH full referenced CAD is saved.
"""
import json
from baseline_registry import ROOT,ref,dump
def main():
    tags=[f'revAG_ground{i}' for i in range(1,6)]+['revAH_pilot1']
    for tag in tags:
        folder=ROOT/'cad/exports'/tag;path=folder/'LOCAL_RAW_MANIFEST.json'
        if path.exists():raise ValueError('Do not overwrite raw manifest')
        d=json.loads((folder/'summary.json').read_text())
        dump(path,dict(status='PRESERVED_LOCAL_RAW',actual_result_status=d['status'],files=[ref(f) for f in sorted(folder.iterdir()) if f.is_file()],scope='Intermediate actual CAD remains at original path; only producer/summary/manifest tracked to avoid duplicate bulk CAD',whole_system_release=False))
    folder=ROOT/'validation/transmission/AI_tab_h3'
    dump(folder/'FAILED_EXECUTION.json',dict(status='EXECUTION_FAIL',exit_code=1,actually_executed=True,command='PYTHONPATH=/tmp/regrip_stage2_fem robot_ws/bin/python palm_tab_fem.py --h-mm3 --tag AI_tab_h3',error='Result serialization TypeError: numpy int32 DOF not JSON serializable',producer=ref(folder/'producer.py'),saved_field=ref(folder/'field.npz'),reason_for_corrected_run='Original saved field lacks P2 edge DOFs, so full equilibrium cannot be recovered from vertex displacements alone. New tag h3b casts JSON int and preserves complete state; no equation/criterion change.',whole_system_release=False))
    dump(ROOT/'validation/alignment/AH_pilot_bounds1_FAILED.json',dict(status='ENVIRONMENT_IMPORT_FAIL',exit_code=1,command='python3 shared_pilot_tolerance.py --candidate revAH_pilot2 --tag AH_pilot_bounds1',error='Legacy MOTOR_SPEC import requires OCP; system python has no OCP',corrected_environment='PYTHONPATH=/tmp/regrip_stage1_ocp robot_ws Python, tag AH_pilot_bounds2',whole_system_release=False))
    print('New intermediate raw artifacts preserved and hashed; nothing removed')
if __name__=='__main__':main()
