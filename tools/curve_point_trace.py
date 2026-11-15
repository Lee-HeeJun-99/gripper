"""Read actual per-material-point return BEFORE Commit;never change physics."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,PREFIX,identity,sha,write_json
from curve_phase_grid import count
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor
BUILD=ROOT/'build/autonomous_20261116_slip_front_a01/v1'
FROZEN=ROOT/'build/autonomous_20261116_curve_a01/transaction_fast_v14/normal_bridge'
SOURCES=[ROOT/'diagnostics/slip_front'/n for n in('Driver.cpp','CMakeLists.txt')]+[FROZEN/n for n in('CurveClassOnly.inc','IntegratedClassOnly.inc')]


def build():
    out=OUT/'slip_front/build_v1';out.mkdir(parents=True,exist_ok=False);hashes={str(p.relative_to(ROOT)):sha(p)for p in SOURCES};write_json(out/'source_hashes.json',hashes)
    for p in SOURCES:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    binary=BUILD/'slip_front_probe'
    if(BUILD/'manifest.json').exists():
        m=json.loads((BUILD/'manifest.json').read_text())
        if m['sources']!=hashes or m['binary']!=sha(binary):raise ValueError('frozen point probe differs')
        write_json(out/'summary.json',dict(status='PASS',reused=True,manifest=m));return
    for name,cmd in[('configure',['cmake','-S','diagnostics/slip_front','-B',BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DFROZEN_AUDIT_BUILD='+str(FROZEN)]),('build',['cmake','--build',BUILD,'-j2']),('ldd',['ldd',binary])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=r));return
    m=dict(sources=hashes,binary=sha(binary),runtime=identity());write_json(BUILD/'manifest.json',m);write_json(out/'summary.json',dict(status='PASS',manifest=m));print('frozen point probe build PASS')


def run(history=False,duration=4):
    name=('history'if history else'coarse')+str(duration);out=OUT/'slip_front'/name;out.mkdir(parents=True,exist_ok=False)
    m=json.loads((BUILD/'manifest.json').read_text());binary=BUILD/'slip_front_probe'
    if m['binary']!=sha(binary)or any(sha(ROOT/n)!=v for n,v in m['sources'].items()):raise ValueError('immutable point probe differs')
    source=OUT/('full_coarse_history1250nm'if history else'full_coarse');metric=source/'metrics_same_grid_v2.json'
    if not metric.exists():metric=source/'metrics.json'
    baseline=json.loads(metric.read_text())
    if not baseline['bounded_hold_pass']or not baseline['recovery_pass']:raise ValueError('actual physical reference prerequisite')
    h=baseline['config']['dt'];steps=count(duration,h);wall=480;prediction=None
    if duration==24:
        own=json.loads((OUT/'slip_front'/(('history'if history else'coarse')+'4')/'summary.json').read_text())
        if own['status']!='PASS':raise ValueError('own actual pure profile prerequisite')
        prediction=own['process']['runtime_s']*steps/own['actual_steps']*1.2;wall=480 if prediction<=480 else 900 if prediction<=900 else 1320
        if prediction>1320:write_json(out/'summary.json',dict(status='BLOCKED',reason='actual profile exceeds finite1320s policy,not observed environment exhaustion',prediction=prediction));return
    write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,memory=4294967296,attempts=1))
    tree=ET.parse(source/'scene.scn')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=list(map(str,[binary,SDK,out/'scene.scn',steps,out/'points.csv',FRAME,BEAM,PLUGIN,baseline['config']['nodes']]))
    shutil.copy2(__file__,out/'RunnerSource.py');write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),probe=m,baseline_metrics_sha256=sha(metric),baseline_scene_sha256=sha(source/'scene.scn'),runner_sha256=sha(out/'RunnerSource.py')))
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();markers=[json.loads(s[len('POINT_TRACE '):])for s in log.splitlines()if s.startswith('POINT_TRACE ')];passed=not process['exit_code']and'[ERROR]'not in log and bool(markers);errors={}
    if passed:
        passed=markers[-1]['steps']==steps and markers[-1]['snapshots']==(4 if duration==4 else 20)and markers[-1]['query_history_changes']==0
        a=[r for r in read_states(source/'state.txt')if r['time']<=duration+1e-8];b=read_states(out/'state.txt');passed&=len(a)==len(b)
        if len(a)==len(b):errors={k:float(np.max(np.abs(np.array([r[k]for r in a])-np.array([r[k]for r in b]))))for k in('X','V','R')};passed&=not any(errors.values())
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,actual_steps=steps,transactions=markers,instrumentation_state_difference=errors,scope='actual read-only material-return samples after structural accumulation/before contact Commit;not a new contact law or convergence approval',units=dict(reference='mm',weight='mm',normal_density='F/mm',capacity_density='F/mm',plastic_density='F',weighted_plastic='F mm')))
    print(name,passed,process['runtime_s'],errors)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('build','profile','full'));p.add_argument('--history',action='store_true');a=p.parse_args()
    if a.stage=='build':build()
    else:run(history=a.history,duration=4 if a.stage=='profile'else 24)
