"""Record one actual mesh-and-assembly diagnostic cycle without promotion."""
import json,shutil,subprocess,datetime
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,dump,S1
from integrated_release_gate import audit

def main():
    out=ROOT/'validation/transmission/AK_palm_diagnostic_cycle1';shutil.copyfile(__file__,out/'producer.py')
    names=['AK_palm_bending1','AK_palm_bending_verify1','AK_palm_mount1','AK_palm_mount2','AK_palm_mount_verify1']
    results={n:json.loads((out.parent/n/'summary.json').read_text()) for n in names}
    release=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))
    dump(out/'release_summary.json',release)
    logs=['bending.log','mount.log','mount2.log','verify_bending.log','verify_mount.log']
    executions=[dict(log=ref(out/log),exit_code=code,virtual_memory_limit_KiB=4194304,timeout_s=420,BLAS_OMP_threads=1) for log,code in zip(logs,[0,1,0,0,0])]
    d=results['AK_palm_bending1'];m=results['AK_palm_mount2']
    verified=results['AK_palm_bending_verify1']['status']=='INDEPENDENT_REPRESENTATION_VERIFICATION_PASS' and results['AK_palm_mount_verify1']['status']=='INDEPENDENT_MOUNT_GEOMETRY_VERIFICATION_PASS'
    result=dict(status='DIAGNOSTIC_VERIFIED_SUPPORT_AND_FEM_QUALIFICATION_BLOCKED' if verified else 'DIAGNOSTIC_VERIFICATION_FAIL',
        starting_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),task='AI_whole_palm_support',track='C',
        time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),producer=ref(out/'producer.py'),plan=ref(out/'plan.json'),
        evidence=[ref(out.parent/n/'summary.json') for n in names],executions=executions,
        transitive_sources=[ref(ROOT/'scripts/baseline_registry.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')],
        geometry=dict(other_parts=m['other_parts_checked'],minimum_modeled_part_distance_mm=m['minimum_other_part_distance_mm'],
            support_material_area_mm2=m['support_annular_area_mm2'],no_modeled_support_contact=not m['touching_parts']),
        mesh_diagnosis=[dict(h_mm=r['h_mm'],quality_failure_count=r['poor_element_count'],poor_volume_fraction=r['poor_volume_fraction'],
            poor_saved_solution_energy_fraction=r['poor_actual_energy_fraction'],P1_bending_energy_errors=[p['relative_energy_error'] for p in r['probes']],
            parasitic_shear_energy_fractions=[p['shear_energy_fraction'] for p in r['probes']]) for r in d['rows']],
        verification_pass=verified,whole_system_release=False,release_audit=ref(out/'release_summary.json'),release_status=release['status'],release_error_count=len(release['errors']),
        preserved_failure='Initial uninterrupted-annulus assumption exit1; original producer/inputs/log/FAIL summary retained. Corrected audit uses actual perforated footprint, not relaxed physical tolerance.',
        next_action='Define a separate finite external base-attachment design and its full force/moment load path before an assembly support solve. For FEM, investigate small boundary features and higher-order or thickness-aware discretization with an independently supported benchmark; do not blindly refine these P1 meshes.',
        limitations=['No new equilibrium or strength solve','Manufactured pure-bending probe is a representation diagnostic on actual meshes, not measured response',
            'No unique-cause or compliance-bound claim','P2 exact polynomial reproduction does not qualify a P2 equilibrium solution',
            'No fixed annulus support, material, friction/preload, overload cap or same-revision release qualified'],
        save_status='PENDING_SUPERVISOR_LOCAL_SAVE',owned_live_analysis_children=0)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],release_status=result['release_status'],release_errors=result['release_error_count']),indent=2))
if __name__=='__main__':main()
