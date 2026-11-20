"""Append-only product campaign evidence;prior immutable hashes must still match."""
import argparse,json,shutil,subprocess
from pathlib import Path
from analyse import BASE,sha
from observer_identity import compiled_alarm_window,compiled_feature_rows,compiled_mapping_acceleration,compiled_inertia_input,compiled_inertia_force
ROOT=BASE.parent

def immutable(name):
    return name.startswith(('product_prototype/results/','product_prototype/reports/evidence_','product_prototype/cad/build_','product_prototype/meshes/','product_prototype/drawings/','/home/ubuntu/SOFA/','/home/ubuntu/miniconda3/envs/robot_ws/lib/python3.10/site-packages/trimesh/'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--prior',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();prior=BASE/'reports'/a.prior/'manifest.json';old=json.loads(prior.read_text());files={k:v for k,v in old['files'].items() if immutable(k)};bad=[k for k,v in files.items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
    if bad:raise ValueError('prior immutable evidence mismatch:'+str(bad))
    out=BASE/'reports'/a.name;out.mkdir(exist_ok=False);cases={}
    for case in a.cases:
        folder=BASE/'results'/case;summary=folder/'summary.json'
        if not summary.exists():raise ValueError('Missing final summary;do not archive partial run as complete:'+case)
        shutil.copy2(summary,out/(case+'.json'));cases[case]=dict(raw=str(folder.relative_to(ROOT)),summary_sha256=sha(summary))
        for f in folder.rglob('*'):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
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
    for name in ('inertia_force_build.py','inertia_force_run.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
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
    for relative in ('bin/runSofa-26.06.00','include/Sofa.DefaultType/sofa/defaulttype/RigidMass.h','include/Sofa.Component.Mass/sofa/component/mass/UniformMass.inl','include/Sofa.Component.Mass/sofa/component/mass/UniformMass.h','include/Sofa.Core/sofa/core/Mapping.h','include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.h','include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.inl'):
        f=sdk/relative;files[str(f)]=sha(f)
    for category in ('meshes','drawings'):
        for candidate in ('precurve_distal40_route_audit_v10','finite_eyelet_support_v11'):
            for f in (BASE/category/candidate).rglob('*'):
                if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    for f in out.iterdir():
        if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    result=dict(scope='Product functionality/clearance diagnostics,NOT final physics/fabrication qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),prior_manifest_sha256=sha(prior),prior_immutable_audit=dict(checked=sum(immutable(k) for k in old['files']),mismatches=bad),cases=cases,files=files)
    (out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(files=len(files),cases=len(cases),prior_checked=result['prior_immutable_audit']['checked'],mismatches=bad)))

if __name__=='__main__':main()
