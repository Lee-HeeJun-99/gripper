"""Resolve a failed purity comparison against a DIFFERENT initial time grid."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,identity,sha,write_json
from curve_fixed_clock import BUILD,PLUGIN,SOURCES
from run_trial import execute_process
from trial_validation import read_states


def main():
    p=argparse.ArgumentParser();p.add_argument('profile',choices=('profile_coarse_n41','profile_coarse_history1250nm'));a=p.parse_args();source=OUT/a.profile;prior=json.loads((source/'metrics.json').read_text());out=OUT/(a.profile+'_same_grid_control');out.mkdir(exist_ok=False)
    if prior['status']!='FAIL'or prior['process']['exit_code']or not prior['prefix_state_errors']:raise ValueError('only observed differing-grid comparator failure may use this branch')
    h=prior['config']['dt'];steps=round(.5/h);m=json.loads((BUILD/'build_manifest.json').read_text())
    if m['binary']!=sha(PLUGIN)or any(sha(ROOT/n)!=v for n,v in m['sources'].items()):raise ValueError('immutable fixed clock differs')
    tree=ET.parse(source/'scene.scn');root=tree.getroot();loop=root.find('EventStepClockAnimationLoop')
    if float(root.get('dt'))!=h or loop is None:raise ValueError('new-grid profile source differs')
    loop.tag='FixedStepClockAnimationLoop';loop.attrib.clear();loop.set('filename',str(out/'clock.csv'));root.insert(0,ET.Element('RequiredPlugin',name='PurePrefixControl',pluginName=str(PLUGIN)))
    for e in root.iter():
        if'filename'in e.attrib and e is not loop:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=json.loads((source/'command.json').read_text());command[2]=str(out/'scene.scn');command[3]=str(steps)
    shutil.copy2(__file__,out/'RunnerSource.py');write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),fixed_clock=m,profile_scene_sha256=sha(source/'scene.scn'),runner_source=sha(out/'RunnerSource.py')))
    process=execute_process(command,out,180);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=not process['exit_code']and'[ERROR]'not in log and f'{steps} iterations done'in log;errors={}
    if passed:
        before=[r for r in read_states(source/'state.txt')if r['time']<=.5+1e-8];after=read_states(out/'state.txt');passed=len(before)==len(after)
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
    result=dict(status='PASS'if passed else'FAIL',process=process,same_dt=h,actual_steps=steps,prefix_state_errors=errors,original_failed_comparison=prior['prefix_state_errors'],scope='actual same-grid .5s fixed-clock control. Original FAIL remains immutable;no tolerance relaxation/no physics success inferred from tiny old differences.')
    write_json(out/'summary.json',result);target=source/'prefix_same_grid_v2.json'
    if target.exists():raise ValueError('refuse overwritten reassessment')
    write_json(target,dict(result,control_summary_sha256=sha(out/'summary.json'),original_metrics_sha256=sha(source/'metrics.json')));print(a.profile,result)


if __name__=='__main__':main()
