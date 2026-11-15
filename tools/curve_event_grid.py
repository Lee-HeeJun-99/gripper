"""Independent nonuniform time-grid contrast near the observed release transient."""
import argparse
import inspect
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
import history_trial
from curve_common import ROOT,OUT,PREFIX,identity,sha,write_json
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor
BUILD=ROOT/'build/autonomous_20261116_event_clock_a01/v1';PLUGIN=BUILD/'libReGripEventStepClock.so'
SOURCES=[ROOT/'models/event_step_clock'/n for n in('Schedule.h','EventStepClock.cpp','CMakeLists.txt')]+[ROOT/'tests/test_event_clock.cpp']


def build():
    out=OUT/'build_event_v1';out.mkdir(parents=True,exist_ok=False)
    for p in SOURCES:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    hashes={str(p.relative_to(ROOT)):sha(p)for p in SOURCES};write_json(out/'sources.json',hashes)
    if(BUILD/'build_manifest.json').exists():
        old=json.loads((BUILD/'build_manifest.json').read_text())
        if old['sources']!=hashes or old['binary']!=sha(PLUGIN):raise ValueError('immutable event build changed;new build version required')
        write_json(out/'summary.json',dict(status='PASS',reused_immutable_build=True,**old));return
    if PLUGIN.exists():raise ValueError('unmanifested existing binary;do not overwrite it')
    for stage,command in[('unit_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',SOURCES[-1],'-o',out/'unit.bin']),('unit',[out/'unit.bin']),('configure',['cmake','-S','models/event_step_clock','-B',BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',BUILD,'-j2']),('ldd',['ldd',PLUGIN])]:
        r=logged(command,out/stage,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=stage,process=r));return
    manifest=dict(sources=hashes,binary=sha(PLUGIN),runtime=identity());write_json(BUILD/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('event grid math/build PASS')


def analyze(out,c,process):
    # Original physical tolerances/formulas are retained EXACTLY. Only its
    # uniform-grid iteration-count assumption becomes the actual logged count.
    original=inspect.getsource(history_trial.analyze);needle="steps=round(duration/config['dt'])"
    if original.count(needle)!=1:raise ValueError('preserved assessor changed;review required')
    adapted=original.replace(needle,"steps=config['actual_steps']")
    generated=out/'NonuniformAssessment.py'
    if generated.exists():raise ValueError('refuse assessment source overwrite')
    generated.write_text(adapted)
    namespace=history_trial.__dict__.copy();exec(compile(adapted,str(generated),'exec'),namespace)
    result=namespace['analyze'](out,c,process)
    result['nonuniform_assessment']=dict(original_source_sha256=sha(ROOT/'tools/history_trial.py'),generated_source_sha256=sha(generated),only_change="steps=config['actual_steps'];physical criteria/formulas unchanged")
    return result


def run(divisor,profile=False):
    if divisor not in(2,4):raise ValueError('bounded release step contrasts')
    manifest=json.loads((BUILD/'build_manifest.json').read_text())
    if manifest['binary']!=sha(PLUGIN)or any(sha(ROOT/p)!=h for p,h in manifest['sources'].items()):raise ValueError('compiled event grid differs')
    name='profile4'if profile else'release_div'+str(divisor);out=OUT/name;out.mkdir(parents=True,exist_ok=False)
    parent=ROOT/'results/autonomous_20261116_fixed_clock_a01';source=parent/'grasp'/('profile_halfdt'if profile else'half24');baseline=json.loads((source/'metrics.json').read_text());c=baseline['config'].copy()
    if c['dt']!=.00025:raise ValueError('fixed half-dt reference required')
    steps=16000 if profile else 64000+8000*divisor
    wall=480;prediction=None
    if not profile:
        prior=json.loads((OUT/'profile4/metrics.json').read_text())
        if prior['status']!='PASS'or any(prior['prefix_state_errors'].values()):raise ValueError('own uniform-prefix API/purity profile required')
        quarter=json.loads((parent/'grasp/quarter18/metrics.json').read_text())
        seconds_per_step=max(prior['process']['runtime_s']/16000,quarter['process']['runtime_s']/144000)
        prediction=seconds_per_step*steps*1.2
        if prediction>900:write_json(out/'metrics.json',dict(status='BLOCKED',reason='profile predicts beyond bounded900s,not observed environment exhaustion',prediction=prediction));return
        wall=900 if prediction>480 else 480
    write_json(out/'resource_decision.json',dict(wall=wall,predicted_with_margin=prediction,memory=4294967296,attempts=1))
    tree=ET.parse(source/'scene.scn');root=tree.getroot();loop=root.find('FixedStepClockAnimationLoop')
    if loop is None:raise ValueError('reference exact clock required')
    loop.tag='EventStepClockAnimationLoop';loop.attrib.clear();loop.set('eventTimes','0 16');loop.set('stepDivisors','1 '+str(divisor));loop.set('filename',str(out/'grid.csv'))
    root.insert(0,ET.Element('RequiredPlugin',name='EventTimeGrid',pluginName=str(PLUGIN)))
    for e in root.iter():
        if'filename'in e.attrib and e is not loop:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    c.update(duration=4 if profile else 18,profile_only=profile,actual_steps=steps,clock_model='explicit_dyadic_release_time_grid',time_grid=dict(base_dt=.00025,event_times=[0,16],step_divisors=[1,divisor]),scope='new integration grid,not a same-uniform-dt run')
    write_json(out/'config.json',c);ident=baseline['identity'].copy();ident['event_grid']=manifest;write_json(out/'identity.json',ident);identity()
    command=json.loads((source/'command.json').read_text());command[2]=str(out/'scene.scn');command[3]=str(steps);write_json(out/'command.json',command)
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=not process['exit_code']and'[ERROR]'not in log and f'{steps} iterations done'in log;errors={}
    if passed:
        end=4 if profile else 16;before=[r for r in read_states(source/'state.txt')if r['time']<=end+1e-8];after=[r for r in read_states(out/'state.txt')if r['time']<=end+1e-8]
        passed=len(before)==len(after)
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
    result=dict(status='PASS'if passed and profile else'EXPERIMENTAL'if passed else'FAIL',config=c,identity=ident,process=process,prefix_state_errors=errors)
    if passed and not profile:
        result=analyze(out,c,process);result['prefix_state_errors']=errors
    write_json(out/'metrics.json',result);print(name,result['status'],process['runtime_s'],errors)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('build','profile','div2','div4'));a=p.parse_args()
    if a.stage=='build':build()
    else:run(4 if a.stage in('profile','div4')else 2,profile=a.stage=='profile')
