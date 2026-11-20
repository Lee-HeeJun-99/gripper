"""Append-only product campaign evidence;prior immutable hashes must still match."""
import argparse,json,shutil,subprocess
from pathlib import Path
from analyse import BASE,sha
from observer_identity import compiled_alarm_window,compiled_feature_rows,compiled_mapping_acceleration,compiled_inertia_input,compiled_inertia_force
ROOT=BASE.parent

def immutable(name):
    return name.startswith(('product_prototype/results/','product_prototype/reports/evidence_','product_prototype/cad/build_','product_prototype/meshes/','product_prototype/drawings/','/home/ubuntu/SOFA/','/home/ubuntu/miniconda3/envs/robot_ws/lib/python3.10/site-packages/trimesh/'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--prior',required=True);p.add_argument('--cases',nargs='+',required=True);p.add_argument('--designs',nargs='*',default=[]);p.add_argument('--modules',nargs='*',default=[]);a=p.parse_args();prior=BASE/'reports'/a.prior/'manifest.json';old=json.loads(prior.read_text());files={k:v for k,v in old['files'].items() if immutable(k)};bad=[k for k,v in files.items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
    if bad:raise ValueError('prior immutable evidence mismatch:'+str(bad))
    out=BASE/'reports'/a.name;out.mkdir(exist_ok=False);cases={}
    for case in a.cases:
        folder=BASE/'results'/case;summary=folder/'summary.json'
        if not summary.exists():raise ValueError('Missing final summary;do not archive partial run as complete:'+case)
        shutil.copy2(summary,out/(case+'.json'));cases[case]=dict(raw=str(folder.relative_to(ROOT)),summary_sha256=sha(summary))
        rejection=folder/'SOURCE_IDENTITY_REJECTION.json'
        if rejection.exists():cases[case]['evidence_rejection']=json.loads(rejection.read_text())
        visual_rejection=folder/'VISUALIZATION_REJECTION.json'
        if visual_rejection.exists():cases[case]['visualization_rejection']=json.loads(visual_rejection.read_text())
        for f in folder.rglob('*'):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
        detail=json.loads(summary.read_text())
        if case.startswith(('b3_inertia','b3_native')):
            builds=[ROOT/detail['build']] if detail.get('build') else []
            builds.append(BASE/'cad'/('build_'+case))
            for build in builds:
                for f in [build/'CMakeCache.txt',*build.glob('libReGrip*.so')]:
                    if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
        for name,digest in detail.get('SDK_dependency_hashes',{}).items():
            f=Path(name)
            if sha(f)!=digest:raise ValueError('actual SDK evidence changed:'+name)
            files[name]=digest
    for name in ('guide_angular_audit.py','guide_entry_phase.py','guide_entry_assess.py','guide_row_dynamics.py','guide_entry_plot.py','guide_motion_clearance.py','guide_sector_candidate.py','guide_clearance_event.py','product_candidate_evidence.py','mechanism_candidates.py','guide_pair_coupon.py','run_alarm_window.py','b3_clearance_comparison.py','guide_chord_audit.py','guide_pair_time_assess.py','b3_clearance_plot.py','guide_route_identity.py','observer_identity.py','run_native.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    row_binary=BASE/'cad/build_pair_rows512/libReGripPairRows.so'
    if sha(row_binary)!='6a00b4e75ef314f5d92ebc67431ee36cedba02c91e6546ff28a4ffe9d5514527':raise ValueError('direct row observer binary changed')
    for f in [row_binary,BASE/'cad/build_pair_rows512/CMakeCache.txt',*list((BASE/'sofa/native_pair_rows').glob('*'))]:
        if f.is_file():
            files[str(f.relative_to(ROOT))]=sha(f)
            if f.suffix in ('.cpp','.txt'):shutil.copy2(f,out/('pair_rows_'+f.name))
    for f in compiled_alarm_window():files[str(f.relative_to(ROOT))]=sha(f)
    for name in ('finite_free_spin_reference.py','test_finite_mass.py','finite_reference_test_run.py','finite_mass_reference.py','finite_com_native.py','finite_com_audit.py','finite_mapped_mass_audit.py','finite_com_event_rows.py','finite_hardware_mass.py','finite_guide_coupon.py','finite_guide_assess.py','finite_guide_surface_audit.py','finite_mesh_compare.py','finite_support_replay.py','finite_hardware_sector.py','finite_support_sat.py','finite_mapped_consistency.py','finite_feature_run.py','closest_geometry.py','finite_native_plot.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    shutil.copy2(BASE/'cad/finite_guide_product.py',out/'finite_guide_product.py')
    for name in ('finite_union_moments.py','finite_union_run.py','test_finite_union.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for name in ('inertia_contact_phase.py','native_plane_policy.py','native_plane_assess.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for name in ('native_penalty_run.py','native_penalty_assess.py','native_compliance_ode.py','native_compliance_assess.py','native_newmark_cable.py','newmark_factor_build.py','native_loop_binary_audit.py','test_native_contact_policy.py','contact_policy_test_run.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for directory in ('native_penalty_probe','native_newmark_factors'):
        for f in (BASE/'sofa'/directory).iterdir():
            if f.is_file():shutil.copy2(f,out/(directory+'_'+f.name))
    for name in ('mapping_acceleration_build.py','mapping_acceleration_run.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for f in compiled_mapping_acceleration():
        files[str(f.relative_to(ROOT))]=sha(f)
        if f.suffix=='.cpp':shutil.copy2(f,out/'mapping_acceleration_Observer.cpp')
    mapping_build=BASE/'cad/build_b3_mapping_build589'
    files[str((mapping_build/'CMakeCache.txt').relative_to(ROOT))]=sha(mapping_build/'CMakeCache.txt')
    shutil.copy2(BASE/'sofa/native_mapping_acceleration/CMakeLists.txt',out/'mapping_acceleration_CMakeLists.txt')
    for name in ('inertia_input_build.py','inertia_input_run.py','inertia_input_validate.py','inertia_contact_audit.py','inertia_surface_audit.py','inertia_energy_audit.py','inertia_energy_time.py','native_response_blocks.py','test_native_inertia.py','inertia_test_run.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for f in compiled_inertia_input():
        files[str(f.relative_to(ROOT))]=sha(f)
        if f.suffix=='.cpp':shutil.copy2(f,out/'inertia_input_Observer.cpp')
    inertia_build=BASE/'cad/build_b3_inertia_input_build592'
    files[str((inertia_build/'CMakeCache.txt').relative_to(ROOT))]=sha(inertia_build/'CMakeCache.txt')
    shutil.copy2(BASE/'sofa/native_inertia_input/CMakeLists.txt',out/'inertia_input_CMakeLists.txt')
    for name in ('inertia_force_build.py','inertia_force_run.py','inertia_matrix_run.py','inertia_matrix_audit.py','inertia_world_run.py','inertia_force_contact_audit.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for name in ('native_loop_intervention.py','native_elastic_tendon.py','elastic_tendon_assess.py','native_spring_energy_run.py','native_spring_potential_fd.py','native_spring_potential_adapter.py','native_spring_newton_purity.py','elastic_tendon_plot.py','test_native_contact_policy.py','contact_policy_test_run.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for directory in ('native_spring_energy','native_unilateral_spring'):
        for f in (BASE/'sofa'/directory).iterdir():
            if f.is_file():shutil.copy2(f,out/(directory+'_'+f.name))
    for directory in ('native_inertia_force','native_system_matrix'):
        for f in (BASE/'sofa'/directory).iterdir():
            if f.is_file():shutil.copy2(f,out/(directory+'_'+f.name))
    for f in compiled_inertia_force():
        files[str(f.relative_to(ROOT))]=sha(f)
        if f.suffix=='.cpp':shutil.copy2(f,out/'inertia_force_Force.cpp')
    force_cache=BASE/'cad/build_b3_inertia_force_build623/CMakeCache.txt'
    files[str(force_cache.relative_to(ROOT))]=sha(force_cache)
    shutil.copy2(BASE/'sofa/native_inertia_force/CMakeLists.txt',out/'inertia_force_CMakeLists.txt')
    for f in compiled_feature_rows():
        files[str(f.relative_to(ROOT))]=sha(f)
        if f.suffix=='.cpp':shutil.copy2(f,out/'feature_Observer.cpp')
    feature_cache=BASE/'cad/build_feature_rows554/CMakeCache.txt';files[str(feature_cache.relative_to(ROOT))]=sha(feature_cache)
    shutil.copy2(BASE/'sofa/native_feature_rows/CMakeLists.txt',out/'feature_CMakeLists.txt')
    import inspect,trimesh
    library=Path(inspect.getfile(trimesh.triangles));files[str(library)]=sha(library)
    physical=BASE/'cad/build_default_control332/libReGripProductSequence.so'
    if sha(physical)!='3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0':raise ValueError('physical controller binary changed')
    files[str(physical.relative_to(ROOT))]=sha(physical)
    sdk=Path('/home/ubuntu/SOFA/v26.06.00')
    for relative in ('lib/libSofa.Component.SolidMechanics.Spring.so','include/Sofa.Component.SolidMechanics.Spring/sofa/component/solidmechanics/spring/SpringForceField.h','include/Sofa.Component.SolidMechanics.Spring/sofa/component/solidmechanics/spring/SpringForceField.inl','include/Sofa.Component.SolidMechanics.Spring/sofa/component/solidmechanics/spring/LinearSpring.h'):
        f=sdk/relative;files[str(f)]=sha(f)
    for relative in ('lib/libSofa.Component.ODESolver.Backward.so.26.06.00','lib/libSofa.Component.AnimationLoop.so.26.06.00','lib/libSofa.Component.Collision.Response.Contact.so.26.06.00','lib/libSofa.Component.MechanicalLoad.so.26.06.00','include/Sofa.Component.Constraint.Lagrangian.Model/sofa/component/constraint/lagrangian/model/BaseContactLagrangianConstraint.inl','include/Sofa.Component.Collision.Response.Contact/sofa/component/collision/response/contact/PenalityContactForceField.inl','include/Sofa.Component.Collision.Response.Contact/sofa/component/collision/response/contact/BarycentricPenalityContact.inl','include/Sofa.Component.MechanicalLoad/sofa/component/mechanicalload/PlaneForceField.inl','include/Sofa.Component.ODESolver.Backward/sofa/component/odesolver/backward/NewmarkImplicitSolver.h'):
        f=sdk/relative;files[str(f)]=sha(f)
    for relative in ('bin/runSofa-26.06.00','include/Sofa.DefaultType/sofa/defaulttype/RigidMass.h','include/Sofa.Component.Mass/sofa/component/mass/UniformMass.inl','include/Sofa.Component.Mass/sofa/component/mass/UniformMass.h','include/Sofa.Core/sofa/core/Mapping.h','include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.h','include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.inl'):
        f=sdk/relative;files[str(f)]=sha(f)
    for category in ('meshes','drawings'):
        for candidate in ('precurve_distal40_route_audit_v10','finite_eyelet_support_v11'):
            for f in (BASE/category/candidate).rglob('*'):
                if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    for case in a.cases:
        detail=json.loads((BASE/'results'/case/'summary.json').read_text())
        partial=detail.get('partial_CAD_output')
        if partial:
            folder=ROOT/partial
            if not folder.resolve().is_relative_to((BASE/'meshes').resolve()):raise ValueError('partial CAD path outside product meshes')
            for f in folder.rglob('*'):
                if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    if a.modules:
        for name in a.modules:
            if Path(name).name!=name:raise ValueError('local module name required')
            mesh=BASE/'meshes'/name;draw=BASE/'drawings'/name
            if not (mesh/'assembly_recipe.json').is_file() or not (draw/'summary.json').is_file():raise ValueError('incomplete unmounted module evidence')
            detail=json.loads((draw/'summary.json').read_text());recipe=json.loads((mesh/'assembly_recipe.json').read_text())
            if len(recipe['parts'])!=len(detail['records']) or detail['fabrication_ready']:raise ValueError('module count/scope mismatch')
            for record in detail['records']:
                f=mesh/(record['part']+'.stl');expected=record.get('STL_sha256',record.get('saved_STL_sha256'))
                if not expected or sha(f)!=expected:raise ValueError('module STL identity mismatch')
            for folder in (mesh,draw):
                for f in folder.rglob('*'):
                    if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    if a.designs:
        for name in a.designs:
            if Path(name).name!=name:raise ValueError('local product design name required')
            for category in ('meshes','drawings'):
                folder=BASE/category/name
                if not (folder/'checks.json').is_file():raise ValueError('incomplete product CAD evidence:'+str(folder))
                for f in folder.rglob('*'):
                    if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    if a.designs or a.modules:
        for f in (BASE/'cad').glob('*.py'):shutil.copy2(f,out/('cad_'+f.name))
        shutil.copy2(BASE/'sofa/native_multistep_contract.py',out/'native_multistep_contract.py')
        for f in (BASE/'config').glob('*v1*.json'):shutil.copy2(f,out/('config_'+f.name))
    for f in out.iterdir():
        if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    result=dict(scope='Product functionality/clearance diagnostics,NOT final physics/fabrication qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),prior_manifest_sha256=sha(prior),prior_immutable_audit=dict(checked=sum(immutable(k) for k in old['files']),mismatches=bad),cases=cases,files=files)
    (out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(files=len(files),cases=len(cases),prior_checked=result['prior_immutable_audit']['checked'],mismatches=bad)))

if __name__=='__main__':main()
