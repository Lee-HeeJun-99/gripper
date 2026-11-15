"""Predeclared transient/quiet grid;validate a factor-two refinement of ALL steps."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,identity,sha,write_json
from curve_event_grid import BUILD,PLUGIN,SOURCES,analyze
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor
EVENTS=[0,.5,2,3,4,6,7,14,16,16.5]
DIVISORS=[1,2,1,2,1,2,1,2,16,1]


def count(duration,base):
    total=0
    for i,t in enumerate(EVENTS):
        end=min(duration,EVENTS[i+1]if i+1<len(EVENTS)else duration)
        if end<=t:continue
        n=(end-t)/(base/DIVISORS[i])
        if abs(n-round(n))>1e-7:raise ValueError('grid endpoint not integer steps')
        total+=round(n)
    return total


def run(fine,profile,nodes=21,history=.0025,tag=''):
    if nodes not in(21,41)or history not in(.0025,.00125)or(nodes==41 and history!=.0025)or(tag and not tag.isalnum())or(profile and tag):raise ValueError('bounded one-factor mesh/history/repeat contrast')
    h=.00025 if fine else .0005;duration=4 if profile else 24
    suffix=('_n41'if nodes==41 else'')+('_history1250nm'if history==.00125 else'')
    name=('profile_'if profile else'full_')+('fine'if fine else'coarse')+suffix+('_'+tag if tag else'');out=OUT/name;out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((BUILD/'build_manifest.json').read_text())
    if manifest['binary']!=sha(PLUGIN)or any(sha(ROOT/p)!=v for p,v in manifest['sources'].items()):raise ValueError('compiled event loop mismatch')
    parent=ROOT/'results/autonomous_20261116_fixed_clock_a01';source=parent/'grasp'/('half24'if fine else'base24')
    if nodes==41 or history==.00125:source=ROOT/'results/autonomous_20261116_beam_compensation_a01/grasp'/('mesh41_half'if nodes==41 else'history_fine_half')
    baseline=json.loads((source/'metrics.json').read_text())
    if not baseline['bounded_hold_pass']or baseline['config']['nodes']!=nodes or baseline['config']['history_spacing']!=history:raise ValueError('actual same-physics uniform initial reference prerequisite')
    steps=count(duration,h);wall=480;prediction=None
    if not profile:
        own=json.loads((OUT/(('profile_fine'if fine else'profile_coarse')+suffix)/'metrics.json').read_text())
        pure=own['status']=='PASS'and not any(own['prefix_state_errors'].values())
        control=OUT/(('profile_fine'if fine else'profile_coarse')+suffix)/'prefix_same_grid_v2.json'
        if not pure and control.exists():
            actual=json.loads(control.read_text());pure=actual['status']=='PASS'and not any(actual['prefix_state_errors'].values())and actual['same_dt']==h and actual['original_metrics_sha256']==sha(OUT/(('profile_fine'if fine else'profile_coarse')+suffix)/'metrics.json')
        if not pure:raise ValueError('own actual new-grid API/profile prerequisite against SAME time grid')
        # Actual prior full/profile predictions differed by at most~6%;10%
        # planning margin is used here,NOT a physical gate/tolerance change.
        prior=json.loads((parent/'grasp/quarter18/metrics.json').read_text())
        prior_steps=round(prior['config']['duration']/prior['config']['dt'])
        rate=max(own['process']['runtime_s']/own['config']['actual_steps'],prior['process']['runtime_s']/prior_steps)
        prediction=rate*steps*1.1;wall=480 if prediction<=480 else 900 if prediction<=900 else 1320
        if prediction>1320:write_json(out/'metrics.json',dict(status='BLOCKED',reason='own recorded profile exceeds1320s finite policy,not an actual environment timeout',prediction=prediction));return
    write_json(out/'resource_decision.json',dict(wall=wall,predicted_with_margin=prediction,margin=1.1,memory=4294967296,attempts=1,scope='predeclared new numerical grid;physical limits unchanged'))
    tree=ET.parse(source/'scene.scn');root=tree.getroot();loop=root.find('FixedStepClockAnimationLoop')
    if loop is None:loop=root.find('DefaultAnimationLoop')
    if loop is None:raise ValueError('exact-clock reference')
    root.set('dt',str(h))
    loop.tag='EventStepClockAnimationLoop';loop.attrib.clear();loop.set('eventTimes',' '.join(map(str,EVENTS)));loop.set('stepDivisors',' '.join(map(str,DIVISORS)));loop.set('filename',str(out/'grid.csv'))
    root.insert(0,ET.Element('RequiredPlugin',name='TransientTimeGrid',pluginName=str(PLUGIN)))
    for e in root.iter():
        if'filename'in e.attrib and e is not loop:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    c=baseline['config'].copy();c.update(dt=h,duration=duration,actual_steps=steps,profile_only=profile,clock_model='predeclared_transient_quiet_dyadic_grid',time_grid=dict(base_dt=h,event_times=EVENTS,step_divisors=DIVISORS),scope='distinct numerical integration grid,NOT a uniform-dt result')
    write_json(out/'config.json',c);ident=identity();ident['structural_compensation']=baseline['identity']['structural_compensation'];ident['event_grid']=manifest
    shutil.copy2(__file__,out/'RunnerSource.py');ident['runner_source_sha256']=sha(out/'RunnerSource.py');write_json(out/'identity.json',ident)
    command=json.loads((source/'command.json').read_text());command[2]=str(out/'scene.scn');command[3]=str(steps);write_json(out/'command.json',command)
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=not process['exit_code']and'[ERROR]'not in log and f'{steps} iterations done'in log;errors={}
    if passed:
        reference=source
        control=OUT/(('profile_fine'if fine else'profile_coarse')+suffix+'_same_grid_control')
        if not profile and control.exists()and json.loads((control/'summary.json').read_text())['status']=='PASS':reference=control
        before={round(r['time']*1e9):r for r in read_states(reference/'state.txt')if r['time']<=.5+1e-8};after=[r for r in read_states(out/'state.txt')if r['time']<=.5+1e-8]
        # Match actual common epochs;never interpolate/generated state values.
        after=[r for r in after if round(r['time']*1e9)in before];before=[before[round(r['time']*1e9)]for r in after]
        if not after or abs(after[-1]['time']-.5)>1e-8:raise ValueError('missing actual shared .5s epoch')
        passed=len(before)==len(after)
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
    result=dict(status='PASS'if passed and profile else'EXPERIMENTAL'if passed else'FAIL',config=c,identity=ident,process=process,prefix_state_errors=errors)
    if passed and not profile:result=analyze(out,c,process);result['prefix_state_errors']=errors
    result['global_energy']='BLOCKED pending this grid actual synchronized journal';result['grasp_optimization']='BLOCKED';write_json(out/'metrics.json',result);print(name,result['status'],process['runtime_s'],errors,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('profile_coarse','profile_fine','full_coarse','full_fine'));p.add_argument('--nodes',type=int,default=21);p.add_argument('--history',type=float,default=.0025);p.add_argument('--tag',default='');a=p.parse_args();run(a.stage.endswith('fine'),a.stage.startswith('profile'),nodes=a.nodes,history=a.history,tag=a.tag)
