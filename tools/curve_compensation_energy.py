"""Validate observer timing AFTER structural arithmetic and BEFORE Commit."""
import json
import argparse
import csv
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT, OUT, BUILD, SDK, FRAME, BEAM, PLUGIN, PREFIX, identity, sha, write_json
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states


def compiled_only(hashes):
    # Keep original documentation snapshots,but documentation is not a C++
    # compilation input. Every header,generated include and CMake/source stays
    # strict. This does not permit any physical-source/binary mismatch.
    return {p:h for p,h in hashes.items()if not p.endswith('.md')}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--steps',type=int,default=2000);args=parser.parse_args();steps=args.steps
    if steps not in(2000,16000,48000):raise ValueError('bounded one/eight/twenty-four-second validation stages')
    out=OUT/('energy_after_arithmetic_'+str(steps)+'_v9');out.mkdir(exist_ok=False)
    build=ROOT/'build/autonomous_20261116_curve_a01/transaction_v9'
    source=OUT/('grasp/repeat24'if steps==48000 else'grasp/base');baseline=json.loads((source/'metrics.json').read_text())
    if not baseline.get('bounded_hold_pass'):raise ValueError('actual coupled arithmetic baseline prerequisite')
    paths=list((ROOT/'diagnostics/transaction_energy').iterdir())+list((ROOT/'diagnostics/contact_return_energy').iterdir())+[ROOT/'models/contact_energy/ReturnAudit.h',ROOT/'models/closure_frame/FrameLayer.cpp',FRAME.parent/'FrameLayerBase.inc']
    for p in paths:
        if p.is_file():
            target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    write_json(out/'sources.json',{str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()})
    hashes={str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()};binary=build/'transaction_journal';manifest=build/'journal_manifest.json'
    if manifest.exists():
        old=json.loads(manifest.read_text())
        if compiled_only(old['sources'])!=compiled_only(hashes) or old['binary']!=sha(binary)or old['bridge']!=sha(build/'normal_bridge/libContactReturnBridge.so')or old['frame_bridge']!=sha(build/'normal_bridge/libFrameReturnBridge.so'):raise ValueError('refuse mixed/rebuilt journal identity')
    else:
        for name,command in[('configure',['cmake','-S','diagnostics/transaction_energy','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DREGRIP_NORMAL_AUDIT=ON','-DFROZEN_CURVE_BUILD='+str(BUILD),'-DFROZEN_FRAME_BUILD='+str(FRAME.parent)]),('build',['cmake','--build',build,'-j2'])]:
            r=logged(command,out/name,180)
            if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=r));return
        write_json(manifest,dict(sources=hashes,binary=sha(binary),bridge=sha(build/'normal_bridge/libContactReturnBridge.so'),frame_bridge=sha(build/'normal_bridge/libFrameReturnBridge.so')))
    tree=ET.parse(source/'scene.scn')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    command=list(map(str,[binary,SDK,out/'scene.scn',steps,out/'energy.csv',FRAME,BEAM,PLUGIN,'after_structural_compensation']))
    write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),baseline_identity=baseline['identity'],source_scene_sha256=sha(source/'scene.scn')))
    wall=180 if steps==2000 else 480
    if steps==48000:
        proof=json.loads((OUT/'energy_after_arithmetic_2000_v9/summary.json').read_text());profile=json.loads((OUT/'energy_after_arithmetic_16000_v8/summary.json').read_text())
        if proof['status']!='PASS'or not baseline.get('recovery_pass'):raise ValueError('actual scope/recovery prerequisites')
        prediction=profile['process']['runtime_s']*3;wall=900
        if prediction*1.1>wall:raise ValueError('actual8s energy profile exceeds full-phase allowance')
        write_json(out/'resource_decision.json',dict(profile_runtime=profile['process']['runtime_s'],prediction=prediction,margin=1.1,wall=wall,attempts=1,memory=4294967296,scope='actual24s observer including full release/recovery;no hard physical threshold change'))
    process=execute_process(command,out,wall);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();markers=[json.loads(s[len('TRANSACTIONS '):])for s in log.splitlines()if s.startswith('TRANSACTIONS ')]
    passed=not process['exit_code']and'[ERROR]'not in log and bool(markers);errors={}
    if passed:
        a=[r for r in read_states(source/'state.txt')if r['time']<=steps*.0005+1e-8];b=read_states(out/'state.txt');passed=len(a)==len(b)
        if passed:
            errors={k:float(np.max(np.abs(np.array([r[k]for r in a])-np.array([r[k]for r in b]))))for k in('X','V','R')};passed=not any(errors.values())
    energy=None
    if passed:
        with(out/'energy.csv').open()as stream:rows=list(csv.DictReader(stream))
        if len(rows)!=3*steps:raise ValueError('actual synchronized row count')
        first=rows[0];last=rows[-1];stored=lambda r:sum(float(r[k])for k in('beam_U','layer_U','contact_U','K'))
        loss_keys=('Rayleigh_mass_work','Rayleigh_stiffness_work','derived_velocity_projection_loss','derived_beam_quadratic_projection','layer_quadratic_projection','normal_quadratic_projection','contact_plastic','contact_endpoint_projection','contact_detachment','layer_plastic','frame_return_projection')
        work=float(last['derived_actuator_Euler_work'])+float(last['derived_external_Euler_work'])
        balance=stored(last)-stored(first)-work+sum(float(last[k])for k in loss_keys)
        remainders=sum(float(last[k])for k in('beam_nonlinear_remainder','layer_nonlinear_or_return_remainder','normal_nonlinear_remainder'))+float(last['frame_return_plastic'])+float(last['frame_return_projection'])
        energy=dict(steps=steps,derived_balance=balance,explicit_potential_and_frame_return_remainders=remainders,remaining=balance-remainders,algorithmic_active_work=work,max_material_return_residual=float(last['max_material_return_residual']),max_frame_return_residual=float(last['max_frame_return_residual']),frame_return_projection=float(last['frame_return_projection']),unknown_pressure_work=last['unknown_pressure_work'],global_closure='BLOCKED;dt and parameter derivation incomplete')
        passed&=energy['max_material_return_residual']<1e-18 and energy['max_frame_return_residual']<1e-18
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,transactions=markers,instrumentation_state_difference=errors,binary_sha256=sha(binary),energy_diagnostic=energy,global_energy='BLOCKED',scope='actual synchronized observer AFTER same live structural arithmetic instance and BEFORE every forcefield Commit;all original forcefield order retained;not full phase energy closure'))
    print(passed,errors,markers)


if __name__=='__main__':main()
