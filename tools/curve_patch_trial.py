"""Cold-start immutable reference-element refinement; no moving state transfer."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
import csv
import numpy as np
from curve_common import ROOT,OUT,identity,sha,write_json
from curve_patch_build import PATCH_BUILD,PATCH_PLUGIN
from curve_local_history import immutable
from curve_phase_grid import count
from curve_cycle_loss import sample
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor


def grid_log_check(log,total,elements):
    records=[json.loads(line[len('PATCH_GRID '):])for line in log.splitlines()if line.startswith('PATCH_GRID ')]
    valid=bool(records)and'Unused Attribute'not in log and all(g['states']==total and g['elements']==elements for g in records)
    return valid,records


def main():
    p=argparse.ArgumentParser();p.add_argument('--spacing',type=float,default=.00125,choices=(.00125,.000625,.0003125));p.add_argument('--prefix',action='store_true');p.add_argument('--record-stride',type=int,choices=(20,200),default=20);a=p.parse_args()
    duration=8.2 if a.prefix else 4;label={.00125:'uniform',.000625:'local625',.0003125:'local312'}[a.spacing]
    suffix='_record200'if a.record_stride==200 else''
    out=OUT/'patch_refinement_v2'/(label+('_prefix82'if a.prefix else'_profile4')+suffix);out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((PATCH_BUILD/'manifest.json').read_text());api=json.loads((OUT/'patch_refinement_v2/api/summary.json').read_text());runtime=identity()
    if api['status']!='PASS'or manifest['binary']!=sha(PATCH_PLUGIN)or manifest['generated']!=sha(PATCH_BUILD/'PatchGenerated.inc')or any(sha(ROOT/name)!=h for name,h in manifest['sources'].items()):raise ValueError('refined compiled/API prerequisite')
    for key in ('curved','inherited'):
        if immutable(runtime[key])!=immutable(manifest['parent'][key]):raise ValueError('parent physical binary changed')
    if a.spacing!=.00125:
        uniform=json.loads((OUT/'patch_refinement_v2/uniform_profile4/summary.json').read_text())
        if uniform['status']!='PASS'or any(uniform['state_difference'].values()):raise ValueError('exact uniform dynamics prerequisite')
    wall=480;prediction=None;steps=count(duration,.0005);planning_margin=1.2;profile_basis=[]
    if a.prefix:
        own=json.loads((OUT/'patch_refinement_v2'/(label+'_profile4'+suffix)/'summary.json').read_text())
        if own['status']!='PASS':
            write_json(out/'summary.json',dict(status='BLOCKED',attempts=0,reason='own actual cold-start profile failed;do not launch longer identical run',profile_status=own['status'],profile_process=own.get('process')));return
        for profile,prefix in (('history1000nm_profile4_v1','history1000nm_prefix82_v1'),('patch_refinement_v2/local625_profile4','patch_refinement_v2/local625_prefix82')):
            first=OUT/profile/'summary.json';second=OUT/prefix/'summary.json'
            if first.exists()and second.exists():
                u=json.loads(first.read_text());v=json.loads(second.read_text())
                if u['status']=='PASS'and v['status']=='PASS':profile_basis.append(dict(profile_sha256=sha(first),prefix_sha256=sha(second),observed_rate_ratio=v['process']['runtime_s']/(u['process']['runtime_s']*v['steps']/u['steps'])))
        # Two actual same-grid cold-start contrasts justify a10% planning
        # allowance if both observed ratios are below it. This changes NO
        # physical tolerance or wall/memory limit;bad forecasts still timeout.
        if len(profile_basis)==2 and max(r['observed_rate_ratio']for r in profile_basis)<1.1:planning_margin=1.1
        prediction=own['process']['runtime_s']*steps/own['steps']*planning_margin;wall=480 if prediction<=480 else 900
        if prediction>900:write_json(out/'summary.json',dict(status='BLOCKED',prediction=prediction,attempts=0,planning_margin=planning_margin,profile_basis=profile_basis,reason='own actual profile exceeds finite900s policy;not an actual environment timeout'));return
    parent=OUT/'full_coarse_history1250nm';tree=ET.parse(parent/'scene.scn');contact=tree.getroot().find('.//CurvedMaterialContact');contact.tag='PatchRefinedContact'
    pairs=list(map(int,contact.get('segments').split()));spacings=[a.spacing if pairs[i]%21>=18 else .00125 for i in range(0,len(pairs),2)]
    # Sites are fixed for the ENTIRE run,including detached states. Bounds
    # chosen in material coordinates90--100mm before this contrast,not moved
    # with contact/force/unknown future state. All six structural layers kept.
    if a.spacing!=.00125:contact.set('edgeSpacing',' '.join(map(str,spacings)))
    contact.set('stride',str(a.record_stride))
    # Pure recording branch is AFTER actual force snapshot/Commit. Before
    # using sparse recording in finer runs,prove its actual625nm dynamics.
    if a.record_stride==200 and(a.prefix or a.spacing!=.000625):
        proof=json.loads((OUT/'patch_refinement_v2/local625_profile4_record200/summary.json').read_text())
        if proof['status']!='PASS'or any(proof['recording_equivalence']['state_difference'].values())or proof['recording_equivalence']['max_common_contact_value_difference']!=0:raise ValueError('actual pure-I/O equivalence prerequisite')
    total=sum(round(5/h)for h in spacings)
    if total>1000000:raise ValueError('unchanged total material-state budget')
    for e in tree.getroot().iter():
        if'filename'in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=json.loads((parent/'command.json').read_text());command[2]=str(out/'scene.scn');command[3]=str(steps);command[-1]=str(PATCH_PLUGIN)
    shutil.copy2(__file__,out/'RunnerSource.py');write_json(out/'identity.json',dict(runtime=runtime,patch=manifest,parent_scene_sha256=sha(parent/'scene.scn'),runner_sha256=sha(out/'RunnerSource.py')));write_json(out/'command.json',command);write_json(out/'config.json',dict(duration=duration,steps=steps,local_spacing=a.spacing,background_spacing=.00125,material_region_mm=[90,100],total_material_states=total,immutable=True,record_stride=a.record_stride));write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,memory=4294967296,attempts=1,planning_margin=planning_margin,profile_basis=profile_basis))
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=process['exit_code']==0 and'[ERROR]'not in log and'Unused Attribute'not in log and f'{steps} iterations done'in log;differences={};phases={}
    grid_valid,actual_grids=grid_log_check(log,total,len(spacings));passed&=grid_valid
    recording={}
    if passed and a.record_stride==200 and not a.prefix:
        reference=OUT/'patch_refinement_v2'/(label+'_profile4');old=read_states(reference/'state.txt');new=read_states(out/'state.txt');length=min(len(old),len(new))
        if length<2:raise ValueError('actual recording comparison missing')
        errors={k:float(np.max(np.abs(np.array([r[k]for r in old[:length]])-np.array([r[k]for r in new[:length]]))))for k in('X','V','R')}
        with(reference/'contact.csv').open()as f:oldcsv={round(float(r['time'])*1e9):r for r in csv.DictReader(f)}
        with(out/'contact.csv').open()as f:newcsv=list(csv.DictReader(f))
        common=[(oldcsv[round(float(r['time'])*1e9)],r)for r in newcsv if round(float(r['time'])*1e9)in oldcsv]
        if not common:raise ValueError('actual common recording epochs missing')
        csv_error=max(abs(float(x[k])-float(y[k]))for x,y in common for k in x)
        recording=dict(state_difference=errors,max_common_contact_value_difference=csv_error,compared_state_frames=length,compared_through_s=old[length-1]['time'],reference_complete=len(old)==len(new),scope='actual same-spacing path comparison;partial reference after timeout remains explicitly partial')
        passed&=not any(errors.values())and csv_error==0
        if a.spacing==.000625:passed&=len(old)==len(new)
    if passed:
        if a.spacing==.00125:
            first=[r for r in read_states(parent/'state.txt')if r['time']<=duration+1e-8];second=read_states(out/'state.txt')
            if len(first)!=len(second):raise ValueError('actual uniform frame count')
            differences={k:float(np.max(np.abs(np.array([r[k]for r in first])-np.array([r[k]for r in second]))))for k in('X','V','R')};passed=not any(differences.values())
        times=(0,.5,2,3,4,6,7,8.2)if a.prefix else(0,.5,2,3,4)
        phases={f'{lo}_{hi}':sample(out,hi)['total']-sample(out,lo)['total']for lo,hi in zip(times[:-1],times[1:])}
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=process,steps=steps,actual_grids=actual_grids,state_difference=differences,recording_equivalence=recording,phase_losses_Fmm=phases,scope='actual API/prefix execution gate only;local refinement is NOT full space/time/grasp qualification'))
    print(label,duration,passed,process,phases,flush=True)


if __name__=='__main__':main()
