"""Isolated real Git/Supervisor with FAKE workers/gates, no account/Codex calls."""
import argparse,contextlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from types import SimpleNamespace
from baseline_registry import ROOT,ref,dump
import goal_session_manager as gm
from goal_manager_policy import engineering_record,stream_health

FAKE_WORKER=r'''import hashlib,json,re,sys,time
from pathlib import Path
prompt=sys.argv[1]
if prompt.startswith('SAVE-ONLY RECOVERY'):sys.exit(0)
cfg=json.loads(Path('scenario.json').read_text());request=Path(re.search(r'Write (.*?) with JSON keys',prompt,re.S).group(1))
head=re.search(r'expected_HEAD="([a-f0-9]+)"',prompt).group(1);i=int(re.search(r'save_request(\d+)\.json',str(request)).group(1));mode=cfg['mode']
if mode=='quota':print(json.dumps(dict(type='turn.failed',error=dict(message='usage_limit_reached'))));sys.exit(1)
if mode=='mutate':Path('product_prototype/stage12_integrated/scripts/goal_manager_policy.py').write_text('UNTRUSTED_CHANGE');sys.exit(0)
if mode=='live_stop':Path('product_prototype/stage12_integrated/runtime/STOP').touch();time.sleep(10);sys.exit(0)
if mode=='clean_failure':sys.exit(1)
if mode=='resume' and i==1:print(json.dumps(dict(type='error',message='rate_limit_exceeded')));sys.exit(1)
f=Path('product_prototype/stage12_integrated/validation/test'+str(i)+'/summary.json');f.parent.mkdir(parents=True)
f.write_text(json.dumps(dict(status='FAIL',scope='ISOLATED FAKE PHYSICS, SOFTWARE TEST ONLY',force_N=1 if mode=='stagnate' else i+1)))
r=dict(path=str(f),SHA256=hashlib.sha256(f.read_bytes()).hexdigest());candidate=Path('product_prototype/stage12_integrated/test_candidate.json')
record=dict(category='ACTUAL_PRODUCT_VALIDATION',task_id='software_test_task',mechanism='ISOLATED_ONLY',system_gate_ids=['continuous_load_path'],actual_change_files=[],candidate_reference=dict(path=str(candidate),SHA256=hashlib.sha256(candidate.read_bytes()).hexdigest()))
data=dict(expected_HEAD=head,message='Isolated fake worker '+str(i),files=[r],results=[r],engineering_progress=record)
if mode=='bad_hash':data['files'][0]['SHA256']='0'*64
request.write_text(json.dumps(data))
print(json.dumps(dict(type='turn.completed',usage=dict(input_tokens=1,output_tokens=1))))
if mode=='timeout' and i==0:time.sleep(10)
'''
FAKE_GATE='''from pathlib import Path
import json
def audit(b,c):
    cfg=json.loads(Path('scenario.json').read_text())
    if cfg['mode']=='bad_gate':return dict(status='UNTRUSTED_FAKE_PASS',errors=[])
    n=len(list(Path('product_prototype/stage12_integrated/validation').glob('test*/summary.json')))
    return dict(status='STAGE1_STAGE2_INTEGRATED_DIGITAL_RELEASE_PASS' if n>=cfg['target'] else 'INTEGRATED_NOT_QUALIFIED',errors=[] if n>=cfg['target'] else ['ISOLATED_FAKE_MISSING_GATE'])
'''
def build(repo,mode,target):
    root=repo/'product_prototype/stage12_integrated';scripts=root/'scripts';scripts.mkdir(parents=True)
    for name in ('validation','cad/exports','hardware_test/fixtures','models'):(root/name).mkdir(parents=True,exist_ok=True)
    for name in gm.TRUSTED:shutil.copyfile(ROOT/'scripts'/name,scripts/name)
    (scripts/'integrated_release_gate.py').write_text(FAKE_GATE)
    for name in ('CURRENT_BASELINE.json','models/integrated_contract.json','RELEASE_STATUS.json'):(root/name).write_text('{}')
    (root/'INTEGRATED_TASKS.json').write_text('{"tasks":[]}');(root/'test_candidate.json').write_text('{"parts":[{"id":"ISOLATED_FAKE"}]}')
    s2=repo/'product_prototype/stage2_load_transfer'
    for rel in ('scripts/commit_guard.py','scripts/stage2_release_gate.py','models/analytical/criteria.json'):
        dst=s2/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT.parent/'stage2_load_transfer'/rel,dst)
    (repo/'fake_worker.py').write_text(FAKE_WORKER);(repo/'scenario.json').write_text(json.dumps(dict(mode=mode,target=target)))
    (repo/'.gitignore').write_text('product_prototype/stage12_integrated/runtime/\n')
    subprocess.run(['git','init','-q',str(repo)],check=True)
    for k,v in [('user.name','Isolated goal test'),('user.email','test@example.invalid'),('commit.gpgsign','false')]:subprocess.run(['git','config',k,v],cwd=repo,check=True)
    subprocess.run(['git','checkout','-qb',gm.BRANCH],cwd=repo,check=True);subprocess.run(['git','add','.'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','Isolated baseline'],cwd=repo,check=True)
    (repo/'user_untracked.txt').write_text('PRESERVE')
    return root
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py');controls=[];original=(gm.ROOT,gm.REPO,gm.command,gm.account_check)
    for source in ('goal_session_manager.py','goal_manager_policy.py','session_manager.py','supervised_save.py'):shutil.copyfile(ROOT/'scripts'/source,out/('tested_'+source))
    try:
        for mode,target,expected,minimum in [('normal',11,'INTEGRATED_RELEASE_GATE_PASS',11),('timeout',2,'INTEGRATED_RELEASE_GATE_PASS',2),('quota',100,'EXTERNAL_ACCOUNT_OR_SERVICE_LIMIT',0),('bad_hash',100,'SUPERVISED_SAVE_OR_PROGRESS_REJECTED',0),('mutate',100,'TRUSTED_SOURCE_CHANGED',0),('stagnate',100,'STAGNATION_AFTER_STRATEGY_REVIEW',4),('stop',100,'USER_STOP',0),('resume',3,'EXTERNAL_ACCOUNT_OR_SERVICE_LIMIT',1),('live_stop',100,'USER_STOP',0),('clean_failure',100,'REPEATED_WORKER_EXECUTION_FAILURE',0),('bad_gate',100,'EXECUTION_OR_AUDIT_FAILURE',0)]:
            with tempfile.TemporaryDirectory(prefix='regrip-goal-controls-') as temp:
                repo=Path(temp);root=build(repo,mode,target)
                if mode=='stop':(root/'runtime').mkdir();(root/'runtime/STOP').touch()
                gm.ROOT=root;gm.REPO=repo;gm.command=lambda prompt:[sys.executable,str(repo/'fake_worker.py'),prompt];gm.account_check=lambda:None
                args=SimpleNamespace(execute=True,per_run_seconds=1 if mode=='timeout' else 8,tag='goal_test',resume=False)
                with (out/(mode+'.log')).open('w') as log,contextlib.redirect_stdout(log):gm.run_goal(args)
                status=json.loads((root/'runtime/goal_test/status.json').read_text());ledger=json.loads((root/'runtime/goal_test/ledger.json').read_text())
                assert status.get('reason')==expected,(mode,status)
                assert status['completed_cycles']>=minimum
                assert (repo/'user_untracked.txt').read_text()=='PRESERVE'
                if mode=='normal':assert status['completed_cycles']==11 and status['state']=='COMPLETE' and status['max_runs'] is None
                if mode=='timeout':assert ledger['recovery_workers']==1 and status['completed_cycles']==2
                if mode in ('quota','stop'):assert not list((root/'runtime/goal_test').glob('save_result*.json'))
                if mode=='clean_failure':assert status['sessions_started']==2
                if mode=='bad_gate':assert status['sessions_started']==0
                if mode=='bad_hash':assert list((root/'validation').glob('test*/summary.json')),'Never delete unsaved output'
                if mode=='resume':
                    cfg=repo/'scenario.json';cfg.write_text(json.dumps(dict(mode='normal',target=3)));subprocess.run(['git','add','scenario.json'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','Isolated operator removes fake quota'],cwd=repo,check=True)
                    args.resume=True
                    with (out/'resume_after.log').open('w') as log,contextlib.redirect_stdout(log):gm.run_goal(args)
                    resumed=json.loads((root/'runtime/goal_test/status.json').read_text());assert resumed['state']=='COMPLETE' and resumed['sessions_started']>status['sessions_started']
                controls.append(dict(case=mode,expected_reason=expected,passed=True,real_Codex_calls=0))
        with tempfile.TemporaryDirectory(prefix='regrip-goal-policy-') as temp:
            r=Path(temp);log=r/'events';err=r/'stderr';err.write_text('')
            log.write_text(json.dumps(dict(type='item.completed',item=dict(type='agent_message',text='example usage_limit_reached')))+'\n')
            assert not stream_health(log,err)['external_limit']
            log.write_text(json.dumps(dict(type='error',message='insufficient_quota'))+'\n');assert stream_health(log,err)['external_limit']
            f=r/'summary.json';f.write_text('{"status":"FAIL","force_N":NaN}')
            request=dict(files=[dict(path='summary.json',SHA256='unused')],results=['summary.json'],engineering_progress=dict(category='ACTUAL_PRODUCT_VALIDATION',task_id='x',mechanism='m',system_gate_ids=['x']))
            try:engineering_record(request,r)
            except ValueError:pass
            else:raise AssertionError('NaN accepted')
            f.write_text('{"status":"PASS","scope":"PROSE_ONLY"}')
            try:engineering_record(request,r)
            except ValueError:pass
            else:raise AssertionError('Prose-only accepted')
            controls.append(dict(case='real_error_events_nonfinite_and_prose_controls',passed=True))
    finally:gm.ROOT,gm.REPO,gm.command,gm.account_check=original
    dump(out/'summary.json',dict(status='PASS',test_only=True,scope='ISOLATED MANAGER SOFTWARE ONLY: fake workers/fake release gates; no ReGrip physics PASS',controls=controls,actual_external_Codex_sessions=0,producer=ref(out/'producer.py'),goal_manager=ref(out/'tested_goal_session_manager.py'),policy=ref(out/'tested_goal_manager_policy.py'),unchanged_supervisor=ref(out/'tested_supervised_save.py'),entry_point=ref(out/'tested_session_manager.py')))
    print(json.dumps(dict(status='PASS',controls=len(controls),real_Codex_calls=0,physics_release=False)))
if __name__=='__main__':main()
