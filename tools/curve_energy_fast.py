"""Validate an energy-only query optimization before finer-dt ledger runs."""
import argparse
import csv
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,BUILD,SDK,FRAME,BEAM,PLUGIN,PREFIX,identity,sha,write_json
from curve_compensation_energy import compiled_only
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--dt',type=float,default=.0005);parser.add_argument('--duration',type=int,default=1);parser.add_argument('--version',default='v10');a=parser.parse_args()
    if a.dt not in(.0005,.00025)or a.duration not in(1,8,24)or not a.version.isalnum():raise ValueError('bounded stages/dt/version')
    label='base'if a.dt==.0005 else'halfdt'
    if a.duration==24:label='repeat24'if a.dt==.0005 else'half_repeat24'
    source=OUT/'grasp'/label;baseline=json.loads((source/'metrics.json').read_text())
    if not baseline.get('bounded_hold_pass')or(a.duration==24 and not baseline.get('recovery_pass')):raise ValueError('actual baseline/recovery prerequisite')
    if baseline['config']['dt']!=a.dt:raise ValueError('reference timestep differs')
    name=f'energy_fast_{a.version}_dt{round(a.dt*1e6)}_s{a.duration}'
    out=OUT/name;out.mkdir(exist_ok=False);build=ROOT/'build/autonomous_20261116_curve_a01'/('transaction_fast_'+a.version)
    paths=list((ROOT/'diagnostics/transaction_energy').iterdir())+list((ROOT/'diagnostics/contact_return_energy').iterdir())+[ROOT/'models/contact_energy/ReturnAudit.h',ROOT/'models/closure_frame/FrameLayer.cpp',FRAME.parent/'FrameLayerBase.inc']
    hashes={str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()}
    for p in paths:
        if p.is_file():
            target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    write_json(out/'sources.json',hashes);binary=build/'transaction_journal';manifest=build/'journal_manifest.json'
    bridges=[build/'normal_bridge'/n for n in('libContactReturnBridge.so','libFrameReturnBridge.so')]
    if manifest.exists():
        old=json.loads(manifest.read_text())
        if compiled_only(old['sources'])!=compiled_only(hashes)or old['binaries']!={p.name:sha(p)for p in[binary,*bridges]}:raise ValueError('compiled energy observer changed;new version required')
    else:
        commands=[('configure',['cmake','-S','diagnostics/transaction_energy','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DREGRIP_NORMAL_AUDIT=ON','-DREGRIP_VALUE_ENERGY=ON','-DREGRIP_BUILD_VALUE_TEST=ON','-DFROZEN_CURVE_BUILD='+str(BUILD),'-DFROZEN_FRAME_BUILD='+str(FRAME.parent)]),('build',['cmake','--build',build,'-j2']),('value_api',[build/'normal_bridge/energy_value_api'])]
        for stage,command in commands:
            r=logged(command,out/stage,180)
            if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=stage,process=r));return
        write_json(manifest,dict(sources=hashes,binaries={p.name:sha(p)for p in[binary,*bridges]},unit_scope='600 Sphere/Cylinder/Box frozen-class energy API states,AD versus value;no production ForceField change'))
    wall=180 if a.duration==1 else 480 if a.duration==8 else 900
    prediction=None
    if a.duration==8:
        prior=json.loads((OUT/f'energy_fast_{a.version}_dt{round(a.dt*1e6)}_s1/summary.json').read_text())
        if prior['status']!='PASS':raise ValueError('own actual query-purity stage required')
        prediction=prior['process']['runtime_s']*8*1.5
        wall=480 if prediction<=480 else 900
        if prediction>900:write_json(out/'summary.json',dict(status='BLOCKED',reason='actual own1sprofile exceeds bounded8s allowance',prediction=prediction));return
    elif a.duration==24:
        prior=json.loads((OUT/f'energy_fast_{a.version}_dt{round(a.dt*1e6)}_s8/summary.json').read_text())
        if prior['status']!='PASS':raise ValueError('own actual8senergy profile required')
        prediction=prior['process']['runtime_s']*3*1.1
        wall=900 if prediction<=900 else 1320
        if prediction>1320:write_json(out/'summary.json',dict(status='BLOCKED',reason='own actual profile exceeds1320s policy;optimize before retry,not an observed environment timeout',prediction=prediction));return
    write_json(out/'resource_decision.json',dict(wall=wall,prediction_with_margin=prediction,attempts=1,memory=4294967296,scope='bounded read-only energy instrumentation;physical gates unchanged'))
    tree=ET.parse(source/'scene.scn')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);steps=round(a.duration/a.dt)
    command=list(map(str,[binary,SDK,out/'scene.scn',steps,out/'energy.csv',FRAME,BEAM,PLUGIN,'after_structural_compensation']))
    write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),reference_identity=baseline['identity'],reference_scene_sha256=sha(source/'scene.scn'),compiled_observer=json.loads(manifest.read_text())))
    process=execute_process(command,out,wall);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();markers=[json.loads(s[len('TRANSACTIONS '):])for s in log.splitlines()if s.startswith('TRANSACTIONS ')]
    passed=not process['exit_code']and'[ERROR]'not in log and bool(markers);errors={};energy_difference=None;energy=None
    if passed:
        before=[r for r in read_states(source/'state.txt')if r['time']<=a.duration+1e-8];after=read_states(out/'state.txt')
        passed=len(before)==len(after)
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
        with(out/'energy.csv').open()as f:rows=list(csv.DictReader(f))
        if len(rows)!=3*steps:raise ValueError('actual energy stage count differs')
        if a.dt==.0005:
            reference=OUT/'energy_after_arithmetic_48000_v9/energy.csv'
            with reference.open()as f:old=[r for r in csv.DictReader(f)if int(r['step'])<=steps]
            if len(old)!=len(rows):raise ValueError('energy comparison stage count')
            energy_difference=max(abs(float(u[k])-float(v[k]))for u,v in zip(old,rows)for k in u if k in v and k!='stage'and u[k]!='null'and v[k]!='null')
            passed&=energy_difference<1e-17
        first,last=rows[0],rows[-1];stored=lambda r:sum(float(r[k])for k in('beam_U','layer_U','contact_U','K'))
        loss_keys=('Rayleigh_mass_work','Rayleigh_stiffness_work','derived_velocity_projection_loss','derived_beam_quadratic_projection','layer_quadratic_projection','normal_quadratic_projection','contact_plastic','contact_endpoint_projection','contact_detachment','layer_plastic','frame_return_projection')
        work=float(last['derived_actuator_Euler_work'])+float(last['derived_external_Euler_work']);balance=stored(last)-stored(first)-work+sum(float(last[k])for k in loss_keys)
        remainder=sum(float(last[k])for k in('beam_nonlinear_remainder','layer_nonlinear_or_return_remainder','normal_nonlinear_remainder','frame_return_plastic','frame_return_projection'))
        energy=dict(derived_balance=balance,explicit_remainders=remainder,remaining=balance-remainder,algorithmic_active_work=work,max_material_return_residual=float(last['max_material_return_residual']),max_frame_return_residual=float(last['max_frame_return_residual']),unknown_pressure_work=last['unknown_pressure_work'])
        passed&=energy['max_material_return_residual']<1e-18 and energy['max_frame_return_residual']<1e-18
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,transactions=markers,dt=a.dt,duration=a.duration,instrumentation_state_difference=errors,maximum_energy_column_difference_vs_full_AD_observer=energy_difference,energy_diagnostic=energy,global_energy='BLOCKED until full time/parameter scope qualification',scope='value-only query optimization;force/Jacobian/Commit unchanged;actual baseline and full-AD observer comparisons are separate gates'))
    print(passed,process['runtime_s'],errors,energy_difference,energy)


if __name__=='__main__':main()
