"""Actual synchronized energy journal on the NEW nonuniform phase grid."""
import argparse
import csv
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,identity,sha,write_json
from curve_compensation_energy import compiled_only
from curve_phase_grid import count
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor


def main():
    p=argparse.ArgumentParser();p.add_argument('--fine',action='store_true');p.add_argument('--duration',type=int,default=4,choices=(4,8,24));a=p.parse_args();label='fine'if a.fine else'coarse';out=OUT/f'energy_v14_{label}_{a.duration}s';out.mkdir(exist_ok=False)
    source=OUT/('full_'+label);baseline=json.loads((source/'metrics.json').read_text())
    if not baseline['bounded_hold_pass']or not baseline['recovery_pass']:raise ValueError('actual new-grid physical hold/recovery prerequisite')
    proof=ROOT/'results/autonomous_20261116_beam_compensation_a01/energy_fast_v14_dt500_s8/summary.json'
    if json.loads(proof.read_text())['status']!='PASS':raise ValueError('actual independent uniform8s observer equivalence prerequisite')
    build=ROOT/'build/autonomous_20261116_curve_a01/transaction_fast_v14';manifest=json.loads((build/'journal_manifest.json').read_text());binary=build/'transaction_journal';binaries=[binary]+[build/'normal_bridge'/n for n in('libContactReturnBridge.so','libFrameReturnBridge.so')]
    if manifest['binaries']!={p.name:sha(p)for p in binaries}or any(sha(ROOT/n)!=v for n,v in compiled_only(manifest['sources']).items()):raise ValueError('immutable observer source/binary changed;do not mix versions')
    if manifest['configuration']!=dict(value_only=True,grouped_contact=True,reuse_energy=True,reuse_frame=True):raise ValueError('observer configuration differs')
    h=baseline['config']['dt'];steps=count(a.duration,h);wall=480;prediction=None
    if a.duration!=4:
        prior=OUT/f'energy_v14_{label}_{4 if a.duration==8 else 8}s/summary.json';own=json.loads(prior.read_text())
        if own['status']!='PASS':raise ValueError('own actual shorter phase-grid energy profile prerequisite')
        prediction=own['process']['runtime_s']*steps/own['actual_steps']*1.1;wall=480 if prediction<=480 else 900 if prediction<=900 else 1320
        if prediction>1320:write_json(out/'summary.json',dict(status='BLOCKED',reason='actual own profile exceeds1320s finite policy;not observed environment exhaustion',prediction=prediction,attempts=0));return
    write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,margin=1.1,memory=4294967296,attempts=1))
    tree=ET.parse(source/'scene.scn')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=list(map(str,[binary,SDK,out/'scene.scn',steps,out/'energy.csv',FRAME,BEAM,PLUGIN,'after_structural_compensation']))
    shutil.copy2(__file__,out/'RunnerSource.py');write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),observer=manifest,baseline_identity=baseline['identity'],baseline_scene_sha256=sha(source/'scene.scn'),runner_sha256=sha(out/'RunnerSource.py')))
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();markers=[json.loads(s[len('TRANSACTIONS '):])for s in log.splitlines()if s.startswith('TRANSACTIONS ')];passed=not process['exit_code']and'[ERROR]'not in log and bool(markers);errors={};energy=None
    if passed:
        m=markers[-1];passed=m['begins']==steps and m['pre_commits']==steps and m['post_commits']==steps and m['same_state_energy_reuse_checks']==2*(steps//1000)and m['max_same_state_energy_reuse_error']==0 and m['frame_snapshot_equivalence_checks']==3*(steps//1000)and m['max_frame_snapshot_error']==0
        before=[r for r in read_states(source/'state.txt')if r['time']<=a.duration+1e-8];after=read_states(out/'state.txt');passed&=len(before)==len(after)
        if len(before)==len(after):errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed&=not any(errors.values())
        with(out/'energy.csv').open()as f:rows=list(csv.DictReader(f))
        if len(rows)!=3*steps:raise ValueError('actual transaction row count mismatch')
        first,last=rows[0],rows[-1];stored=lambda r:sum(float(r[k])for k in('beam_U','layer_U','contact_U','K'))
        losses=('Rayleigh_mass_work','Rayleigh_stiffness_work','derived_velocity_projection_loss','derived_beam_quadratic_projection','layer_quadratic_projection','contact_plastic','contact_endpoint_projection','contact_detachment','layer_plastic','frame_return_projection')
        work=float(last['derived_actuator_Euler_work'])+float(last['derived_external_Euler_work']);balance=stored(last)-stored(first)-work+sum(float(last[k])for k in losses)
        remainder=sum(float(last[k])for k in('beam_nonlinear_remainder','layer_nonlinear_or_return_remainder','frame_return_plastic','frame_return_projection','grouped_contact_mapped_remainder'))
        energy=dict(derived_balance=balance,separately_computed_signed_remainders=remainder,unexplained_discrete_residual=balance-remainder,actuator_and_external_Euler_work=work,max_material_return_residual=float(last['max_material_return_residual']),max_frame_return_residual=float(last['max_frame_return_residual']),unknown_pressure_work=last['unknown_pressure_work'],unknown_total_closure=last['unknown_total_closure'])
        passed&=energy['max_material_return_residual']<1e-18 and energy['max_frame_return_residual']<1e-18 and m['max_kinetic_algorithmic_residual']<1e-18
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,actual_steps=steps,duration=a.duration,time_grid=baseline['config']['time_grid'],instrumentation_state_difference=errors,transactions=markers,energy_diagnostic=energy,scope='actual NEW-grid query/API/transaction validation,not physical energy/time certification. Signed remainders are NOT heat;unknown fields remain NULL. Grasp optimization stays blocked by remaining phase/history gates.'))
    print(label,a.duration,passed,process['runtime_s'],errors,energy)


if __name__=='__main__':main()
