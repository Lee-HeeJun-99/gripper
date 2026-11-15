"""Cold-start immutable reference-element refinement; no moving state transfer."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,identity,sha,write_json
from curve_patch_build import PATCH_BUILD,PATCH_PLUGIN
from curve_local_history import immutable
from curve_phase_grid import count
from curve_cycle_loss import sample
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor


def main():
    p=argparse.ArgumentParser();p.add_argument('--spacing',type=float,default=.00125,choices=(.00125,.000625,.0003125));p.add_argument('--prefix',action='store_true');a=p.parse_args()
    duration=8.2 if a.prefix else 4;label={.00125:'uniform',.000625:'local625',.0003125:'local312'}[a.spacing]
    out=OUT/'patch_refinement_v2'/(label+('_prefix82'if a.prefix else'_profile4'));out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((PATCH_BUILD/'manifest.json').read_text());api=json.loads((OUT/'patch_refinement_v2/api/summary.json').read_text());runtime=identity()
    if api['status']!='PASS'or manifest['binary']!=sha(PATCH_PLUGIN)or manifest['generated']!=sha(PATCH_BUILD/'PatchGenerated.inc')or any(sha(ROOT/name)!=h for name,h in manifest['sources'].items()):raise ValueError('refined compiled/API prerequisite')
    for key in ('curved','inherited'):
        if immutable(runtime[key])!=immutable(manifest['parent'][key]):raise ValueError('parent physical binary changed')
    if a.spacing!=.00125:
        uniform=json.loads((OUT/'patch_refinement_v2/uniform_profile4/summary.json').read_text())
        if uniform['status']!='PASS'or any(uniform['state_difference'].values()):raise ValueError('exact uniform dynamics prerequisite')
    wall=480;prediction=None;steps=count(duration,.0005)
    if a.prefix:
        own=json.loads((OUT/'patch_refinement_v2'/(label+'_profile4')/'summary.json').read_text())
        if own['status']!='PASS':raise ValueError('own measured cold-start profile prerequisite')
        prediction=own['process']['runtime_s']*steps/own['steps']*1.2;wall=480 if prediction<=480 else 900
        if prediction>900:write_json(out/'summary.json',dict(status='BLOCKED',prediction=prediction,attempts=0,reason='own actual profile exceeds finite900s policy;not an actual environment timeout'));return
    parent=OUT/'full_coarse_history1250nm';tree=ET.parse(parent/'scene.scn');contact=tree.getroot().find('.//CurvedMaterialContact');contact.tag='PatchRefinedContact'
    pairs=list(map(int,contact.get('segments').split()));spacings=[a.spacing if pairs[i]%21>=18 else .00125 for i in range(0,len(pairs),2)]
    # Sites are fixed for the ENTIRE run,including detached states. Bounds
    # chosen in material coordinates90--100mm before this contrast,not moved
    # with contact/force/unknown future state. All six structural layers kept.
    if a.spacing!=.00125:contact.set('edgeSpacing',' '.join(map(str,spacings)))
    total=sum(round(5/h)for h in spacings)
    if total>1000000:raise ValueError('unchanged total material-state budget')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=json.loads((parent/'command.json').read_text());command[2]=str(out/'scene.scn');command[3]=str(steps);command[-1]=str(PATCH_PLUGIN)
    shutil.copy2(__file__,out/'RunnerSource.py');write_json(out/'identity.json',dict(runtime=runtime,patch=manifest,parent_scene_sha256=sha(parent/'scene.scn'),runner_sha256=sha(out/'RunnerSource.py')));write_json(out/'command.json',command);write_json(out/'config.json',dict(duration=duration,steps=steps,local_spacing=a.spacing,background_spacing=.00125,material_region_mm=[90,100],total_material_states=total,immutable=True));write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,memory=4294967296,attempts=1))
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=process['exit_code']==0 and'[ERROR]'not in log and'Unused Attribute'not in log and f'{steps} iterations done'in log;differences={};phases={}
    actual_grids=[json.loads(line[len('PATCH_GRID '):])for line in log.splitlines()if line.startswith('PATCH_GRID ')]
    passed&=bool(actual_grids)and all(g['states']==total and g['elements']==len(spacings)for g in actual_grids)
    if passed:
        if a.spacing==.00125:
            first=[r for r in read_states(parent/'state.txt')if r['time']<=duration+1e-8];second=read_states(out/'state.txt')
            if len(first)!=len(second):raise ValueError('actual uniform frame count')
            differences={k:float(np.max(np.abs(np.array([r[k]for r in first])-np.array([r[k]for r in second]))))for k in('X','V','R')};passed=not any(differences.values())
        times=(0,.5,2,3,4,6,7,8.2)if a.prefix else(0,.5,2,3,4)
        phases={f'{lo}_{hi}':sample(out,hi)['total']-sample(out,lo)['total']for lo,hi in zip(times[:-1],times[1:])}
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,steps=steps,actual_grids=actual_grids,state_difference=differences,phase_losses_Fmm=phases,scope='actual API/prefix execution gate only;local refinement is NOT full space/time/grasp qualification'))
    print(label,duration,passed,process,phases,flush=True)


if __name__=='__main__':main()
