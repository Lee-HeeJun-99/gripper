"""Replay a SEALED graph_probe case into a fresh directory,never overwrite raw.

Uses the original binaries/scene/control/grid/step count. Only output filenames
change. This is trajectory reproducibility,not renewed physical qualification.
"""
import argparse
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from run_trial import execute_process
from trial_validation import read_states
from birth_monitor import Monitor


def role_hashes(value,key):
    found=set()
    if isinstance(value,dict):
        for name,item in value.items():
            if name==key and isinstance(item,str):found.add(item)
            found.update(role_hashes(item,key))
    elif isinstance(value,list):
        for item in value:found.update(role_hashes(item,key))
    return found


def inside_results(case,out,root):
    results=(root/'results').resolve()
    return results in case.resolve().parents and results in out.resolve().parents


def replay(case,out,wall_override=None):
    case=case.resolve();out=out.resolve()
    if not inside_results(case,out,ROOT):raise ValueError('case/output must stay in project external-drive results tree')
    if out.exists():raise ValueError('refuse existing output')
    manifest=json.loads((ROOT/'reports/CURVED_RESEARCH_EVIDENCE_MANIFEST_V2.json').read_text())
    def sealed(path):
        name=str(path.relative_to(ROOT))
        if name not in manifest['files']or sha(path)!=manifest['files'][name]:raise ValueError('unsealed/changed artifact '+name)
    for name in('scene.scn','command.json','identity.json'):sealed(case/name)
    command=json.loads((case/'command.json').read_text())
    if len(command)!=8 or Path(command[0]).name!='graph_probe':raise ValueError('only sealed native graph_probe8argument cases supported')
    # SDK executable is bound indirectly by its sealed actual memory audit.
    driver_audit=ROOT/'results/autonomous_20261116_phase_grid_a01/memory_continuation_v1.json';sealed(driver_audit)
    if sha(Path(command[0]))!=json.loads(driver_audit.read_text())['driver_binary_sha256']:raise ValueError('SDK driver binary differs')
    identity=json.loads((case/'identity.json').read_text());frame_hashes=role_hashes(identity,'frame_sha256')
    # The older Frame DLL is outside the new autonomous build glob. Its
    # precise role/hash is nevertheless recorded in the SEALED inherited
    # identity. Never accept an arbitrary matching digest from another role.
    if len(frame_hashes)!=1 or sha(Path(command[5]))not in frame_hashes:raise ValueError('sealed inherited Frame role/hash differs')
    for token in command[6:]:sealed(Path(token))
    tree=ET.parse(case/'scene.scn')
    for element in tree.getroot().iter('RequiredPlugin'):
        for token in element.get('pluginName','').split():
            path=Path(token)
            if path.is_file():sealed(path.resolve())
    decision=case/'summary.json'
    if not decision.exists():decision=case/'metrics_same_grid_v2.json'
    if not decision.exists():decision=case/'metrics.json'
    sealed(decision);prior=json.loads(decision.read_text());process=prior.get('process')
    if not process or process['exit_code']!=0 or process['process_status']!='exited':raise ValueError('reference did not complete;do not silently extend failed/timeout trajectories')
    prediction=process['runtime_s']*1.1;wall=480 if prediction<=480 else 900 if prediction<=900 else 1320
    if wall_override is not None:
        if wall_override not in(480,900,1320)or wall_override<wall:raise ValueError('override must respect measured finite profile')
        wall=wall_override
    out.mkdir(parents=True,exist_ok=False)
    if prediction>1320:write_json(out/'summary.json',dict(status='BLOCKED',prediction=prediction,attempts=0,reason='actual identical-case forecast exceeds1320s policy'));return
    for element in tree.getroot().iter():
        if'filename'in element.attrib:element.set('filename',str(out/element.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command[2]=str(out/'scene.scn');write_json(out/'command.json',command);shutil.copy2(__file__,out/'RunnerSource.py')
    write_json(out/'identity.json',dict(sealed_manifest_sha256=sha(ROOT/'reports/CURVED_RESEARCH_EVIDENCE_MANIFEST_V2.json'),source_checkpoint=manifest['source_checkpoint'],reference=str(case),reference_decision_sha256=sha(decision),runner_sha256=sha(out/'RunnerSource.py')))
    write_json(out/'resource_decision.json',dict(wall=wall,prediction=prediction,reference_runtime_s=process['runtime_s'],memory=4294967296,attempts=1))
    monitor=Monitor(out);monitor.thread.start()
    try:result=execute_process(command,out,wall)
    finally:monitor.finish()
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();passed=result['exit_code']==0 and'[ERROR]'not in log and'Unused Attribute'not in log and f'{command[3]} iterations done'in log;errors={}
    if passed:
        sealed(case/'state.txt');before=read_states(case/'state.txt');after=read_states(out/'state.txt')
        passed=len(before)==len(after)and [r['time']for r in before]==[r['time']for r in after]
        if passed:errors={k:float(np.max(np.abs(np.array([r[k]for r in before])-np.array([r[k]for r in after]))))for k in('X','V','R')};passed=not any(errors.values())
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=result,state_difference=errors,scope='actual sealed-case full trajectory equality ONLY;reference physics FAILs/limited scope remain unchanged;no grasp/energy certificate inferred'))
    print('sealed replay',passed,result['runtime_s'],errors)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--case',required=True,type=Path);parser.add_argument('--out',required=True,type=Path);args=parser.parse_args();replay(args.case,args.out)
