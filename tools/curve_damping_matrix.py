"""Read the actual solved public MBK matrix;test measurement purity first."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,identity,sha,write_json
from run_trial import execute_process
from trial_validation import read_states


def main():
    p=argparse.ArgumentParser();p.add_argument('--duration',type=float,default=4);a=p.parse_args()
    if a.duration not in(4,17.1):raise ValueError('bounded profile/full matrix stages')
    name='profile4'if a.duration==4 else'release17';out=OUT/('damping_'+name);out.mkdir(exist_ok=False)
    source=OUT/'grasp'/('profile_halfdt'if a.duration==4 else'half24')
    baseline=json.loads((source/'metrics.json').read_text());dt=baseline['config']['dt']
    if dt!=.00025:raise ValueError('actual fixed-clock half-dt reference required')
    binary=ROOT/'build/autonomous_20261116_damping_a01/v1/damping_matrix_audit'
    paths=[ROOT/'diagnostics/damping_matrix'/n for n in('Driver.cpp','CMakeLists.txt')]
    for path in paths:
        target=out/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    manifest=dict(sources={str(x.relative_to(ROOT)):sha(x)for x in paths},binary=sha(binary))
    wall=480;prediction=None
    if a.duration!=4:
        profile=json.loads((OUT/'damping_profile4/summary.json').read_text())
        if profile['status']!='PASS'or profile['compiled']!=manifest:raise ValueError('own actual pure profile with same compiled probe required')
        prediction=profile['process']['runtime_s']*a.duration/4*1.2
        if prediction>900:write_json(out/'summary.json',dict(status='BLOCKED',reason='actual profile exceeds bounded900s',prediction=prediction));return
        wall=900 if prediction>480 else 480
    write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,memory=4294967296,attempts=1))
    tree=ET.parse(source/'scene.scn')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    command=list(map(str,[binary,SDK,out/'scene.scn',round(a.duration/dt),out/'matrix',FRAME,BEAM,PLUGIN]))
    write_json(out/'command.json',command);write_json(out/'identity.json',dict(runtime=identity(),compiled=manifest,reference=baseline['identity'],scene_sha256=sha(source/'scene.scn')))
    process=execute_process(command,out,wall);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    passed=not process['exit_code']and'[ERROR]'not in log and'DAMPING_AUDIT'in log;errors={}
    if passed:
        before=[r for r in read_states(source/'state.txt')if r['time']<=a.duration+1e-8];after=read_states(out/'state.txt')
        passed=len(before)==len(after)
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,compiled=manifest,instrumentation_state_difference=errors,scope='read-only actual public solved MBK plus mass;not damping PSD certification'))
    print(passed,process,errors)


if __name__=='__main__':main()
