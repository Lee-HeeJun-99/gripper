"""Sequential go/no-go checks. Writes a machine-readable, artifact-bound gate."""
import csv
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from baseline_regression import run as baseline_run
from run_trial import ROOT, run_trial, sha

sys.path.insert(0,str(ROOT/'reference_fem'))
from planar import solve


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume',action='store_true',help='Reuse completed runs only after checking binary hashes and configurations')
    args=parser.parse_args()
    out=ROOT/'results/physics_validation'
    out.mkdir(exist_ok=args.resume)
    def trial(name,**config):
        saved=out/name/'metrics.json'
        if args.resume and saved.exists():
            report=json.loads(saved.read_text())
            expected=dict(k=None,connectors=None,dt=.0005,duration=3.,load=.0001,n=11,timeout=60)
            expected.update(config)
            if any(report['config'][key]!=value for key,value in expected.items()):
                raise RuntimeError('cached configuration mismatch: '+name)
            if report['diagnostics_sha256']!=sha(ROOT/'build/diagnostics/libReGripDiagnostics.so'):
                raise RuntimeError('cached diagnostics mismatch: '+name)
            if config.get('k') is not None and report['plugin_sha256']!=sha(ROOT/'build/plugin/bin/libSofaTangentialV110.so'):
                raise RuntimeError('cached plugin mismatch: '+name)
            return report
        return run_trial(out/name,**config)
    checks={}
    cached=out/'baseline/comparison.json'
    if args.resume and cached.exists():
        b=json.loads(cached.read_text())
        checks['baseline']=b['passed'] and b['diagnostics_sha256']==sha(ROOT/'build/diagnostics/libReGripDiagnostics.so')
    else:
        checks['baseline']=baseline_run(out/'baseline')
    test=subprocess.run([str(ROOT/'build/plugin/test_forcefield')],capture_output=True,text=True)
    (out/'native_test.log').write_text(test.stdout+test.stderr)
    checks['native_force_matrix']=test.returncode==0
    if not all(checks.values()):
        raise RuntimeError('baseline or native API test failed')
    spec=importlib.util.spec_from_file_location('v106_original',ROOT/'handover/20261114/SOFA_V106_Tangential_Coupling/tangential_fem_v106.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    refs=[]
    with (ROOT/'handover/20261114/SOFA_V106_Tangential_Coupling/comparison_V106_static.csv').open(encoding='utf-8-sig') as stream:
        gold=list(csv.DictReader(stream))
    checks['v106_original_reproduced']=True
    for g in gold:
        k=float(g['k_connector']);value=original.solve(k)
        checks['v106_original_reproduced'] &= abs(value['deflection_mm']-float(g['deflection_mm']))<1e-8
        equivalent=solve(k)
        refs.append(dict(k=k,rectangular_tip=value['deflection_mm'],circular_tip=equivalent['deflection_mm']))
    with (out/'reference_comparison.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(refs[0]));writer.writeheader();writer.writerows(refs)
    results={}
    specs=[('free',{}),('k0',dict(k=0)),('k001',dict(k=.01)),('k01',dict(k=.1)),
           ('k1',dict(k=1)),('k10',dict(k=10)),('k100',dict(k=100)),
           ('k1_repeat',dict(k=1)),('free_dt_half',dict(dt=.00025)),
           ('k1_dt_half',dict(k=1,dt=.00025)),('k1_dt_double',dict(k=1,dt=.001)),
           ('k1_extend',dict(k=1,duration=6)),('k1_half_load',dict(k=1,load=.00005)),
           ('k1_refine',dict(k=1,n=21,connectors=list(range(2,21,2))))]
    specs += [('k100_dt_half',dict(k=100,dt=.00025)),('k100_dt_double',dict(k=100,dt=.001)),
              ('k100_refine',dict(k=100,n=21,connectors=list(range(2,21,2)))),
              ('sparse_tip',dict(k=1,connectors=[10])),('sparse_mid',dict(k=1,connectors=[5]))]
    for name,config in specs:
        result=trial(name,**config)
        results[name]=result
        checks[name+'_equilibrium']=result['status']=='complete'
        if result['status']!='complete':
            # Do not silently use an invalid case in comparisons.
            continue
        if name in ('free','k0','k001','k01','k1','k10','k100'):
            ref=solve(config.get('k',0))
            checks[name+'_static_reference']=abs(result['tip_deflection_mm']/ref['deflection_mm']-1)<.005
    def rel(a,b):return abs(a/b-1)
    if all(r['status']=='complete' for r in results.values()):
        free=results['free']['tip_deflection_mm'];on=results['k1']['tip_deflection_mm']
        checks['k0_equals_free']=rel(results['k0']['tip_deflection_mm'],free)<1e-10
        checks['repeat']=rel(results['k1_repeat']['tip_deflection_mm'],on)<1e-10
        checks['dt_free']=rel(results['free_dt_half']['tip_deflection_mm'],free)<.001
        checks['dt_on_half']=rel(results['k1_dt_half']['tip_deflection_mm'],on)<.001
        checks['dt_on_double']=rel(results['k1_dt_double']['tip_deflection_mm'],on)<.001
        checks['duration_extension']=rel(results['k1_extend']['tip_deflection_mm'],on)<.001
        checks['load_linearity']=rel(results['k1_half_load']['tip_deflection_mm']*2,on)<.005
        checks['mesh_refinement_same_connector_locations']=rel(results['k1_refine']['tip_deflection_mm'],on)<.01
        tips=[results[name]['tip_deflection_mm'] for name in ['free','k001','k01','k1','k10','k100']]
        slips=[results[name]['max_x_slip_mm'] for name in ['free','k001','k01','k1','k10','k100']]
        checks['monotone_tip']=all(a>b for a,b in zip(tips,tips[1:]))
        checks['monotone_slip']=all(a>b for a,b in zip(slips,slips[1:]))
    else:
        checks['comparisons_have_valid_inputs']=False
    failure=trial('timeout_probe',k=1,timeout=.001)
    checks['timeout_classification']=failure['status']=='timeout' and failure['effective_stiffness'] is None
    for name in ('k100_dt_half','k100_dt_double'):
        checks[name+'_convergence']=rel(results[name]['tip_deflection_mm'],results['k100']['tip_deflection_mm'])<.001
    checks['k100_mesh_convergence']=rel(results['k100_refine']['tip_deflection_mm'],results['k100']['tip_deflection_mm'])<.01
    for name,connectors in [('sparse_tip',[10]),('sparse_mid',[5])]:
        expected=solve(1,connectors=connectors)['deflection_mm']
        checks[name+'_reference']=rel(results[name]['tip_deflection_mm'],expected)<.005
    summary=[]
    for name,r in results.items():
        summary.append(dict(case=name,k=r['config']['k'],dt=r['config']['dt'],n=r['config']['n'],load=r['config']['load'],
                            status=r['status'],tip=r.get('tip_deflection_mm'),slip=r.get('max_x_slip_mm'),
                            residual=r.get('relative_residual'),
                            stiffness_ratio=results['free']['tip_deflection_mm']/r['tip_deflection_mm'] if r['status']=='complete' and r['config']['load']==1e-4 else None))
    with (out/'summary.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    checks={key:bool(value) for key,value in checks.items()}
    gate=dict(passed=all(checks.values()),checks=checks,
              plugin_sha256=sha(ROOT/'build/plugin/bin/libSofaTangentialV110.so'),
              diagnostics_sha256=sha(ROOT/'build/diagnostics/libReGripDiagnostics.so'),
              scope='30 mm bilayer, small planar rotations <0.005 rad, model force units, connector k up to 100',
              excludes=['finite rotation consistency','real vacuum friction','physical pressure calibration','100 mm gripper'])
    gate['source_sha256']={path:sha(ROOT/path) for path in [
        'tools/native_scene.py','tools/run_trial.py','tools/baseline_regression.py',
        'reference_fem/planar.py','plugin/src/TangentialRigidForceField.cpp',
        'diagnostics/PrecisionStateWriter.cpp','tests/test_forcefield.cpp']}
    (out/'gate.json').write_text(json.dumps(gate,indent=2))
    print(json.dumps(gate,indent=2))
    return 0 if gate['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
