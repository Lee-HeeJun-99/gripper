"""Two REAL supervisor cycles in an isolated Git fixture, using a fake worker.

No Codex call, real research change, account use or permission bypass.
"""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from baseline_registry import ROOT,ref,dump
import session_manager as manager

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='regrip-manager-flow-') as tmp:
        repo=Path(tmp);root=repo/'product_prototype/stage12_integrated';scripts=root/'scripts';scripts.mkdir(parents=True)
        for name in ('validation','cad/exports','hardware_test/fixtures'):(root/name).mkdir(parents=True)
        for name in ('CURRENT_BASELINE.json','RELEASE_STATUS.json'):(root/name).write_text('{}')
        (root/'INTEGRATED_TASKS.json').write_text('{"tasks":[]}')
        (repo/'.gitignore').write_text('product_prototype/stage12_integrated/runtime/\n')
        (repo/'reports').mkdir();(repo/'reports/INTEGRATED_CURRENT_STATUS.md').write_text('baseline')
        shutil.copyfile(ROOT/'scripts/supervised_save.py',scripts/'supervised_save.py')
        guard=repo/'product_prototype/stage2_load_transfer/scripts/commit_guard.py';guard.parent.mkdir(parents=True);shutil.copyfile(ROOT.parent/'stage2_load_transfer/scripts/commit_guard.py',guard)
        (scripts/'baseline_registry.py').write_text("from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\n")
        (scripts/'integrated_release_gate.py').write_text("def audit(b,c): return dict(status='INTEGRATED_NOT_QUALIFIED')\n")
        (root/'models').mkdir();(root/'models/integrated_contract.json').write_text('{}')
        worker=repo/'fake_worker.py';worker.write_text('''import sys,re,json,hashlib,subprocess
from pathlib import Path
prompt=sys.argv[1];request=Path(re.search(r" Write (.*?) with JSON keys",prompt).group(1));head=re.search(r'expected_HEAD="([a-f0-9]+)"',prompt).group(1)
i=len(list(request.parent.glob('save_result*.json')));f=Path('product_prototype/stage12_integrated/validation/cycle'+str(i)+'/summary.json');f.parent.mkdir(parents=True);f.write_text(json.dumps(dict(status='FAIL',scope='ISOLATED SYNTHETIC TEST FIXTURE')))
r=dict(path=str(f),SHA256=hashlib.sha256(f.read_bytes()).hexdigest());report=Path('reports/INTEGRATED_CURRENT_STATUS.md');report.write_text('Isolated cycle '+str(i));rr=dict(path=str(report),SHA256=hashlib.sha256(report.read_bytes()).hexdigest());request.write_text(json.dumps(dict(expected_HEAD=head,message='Isolated manager cycle '+str(i),files=[r,rr],results=[str(f)])))
''')
        subprocess.run(['git','init','-q',str(repo)],check=True)
        for key,value in [('user.name','Isolated manager test'),('user.email','test@example.invalid'),('commit.gpgsign','false')]:subprocess.run(['git','config',key,value],cwd=repo,check=True)
        subprocess.run(['git','checkout','-qb','development/regrip-autonomous-research'],cwd=repo,check=True)
        subprocess.run(['git','add','.'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','Isolated baseline'],cwd=repo,check=True)
        (repo/'user_untracked.txt').write_text('PRESERVE')
        manager.ROOT=root;manager.REPO=repo;manager.command=lambda prompt:[sys.executable,str(worker),prompt]
        original=sys.argv;sys.argv=['session_manager.py','--execute','--tag','flow','--max-runs','2','--per-run-seconds','5']
        try:manager.main()
        finally:sys.argv=original
        summary=json.loads((root/'runtime/flow/summary.json').read_text());status=json.loads((root/'runtime/flow/status.json').read_text())
        assert len(summary['runs'])==2 and all(r['progress'] and not r['dirty'] and r['exit_code']==0 for r in summary['runs'])
        assert status['state']=='STOPPED' and status['stop_reason']=='RUN_BUDGET_EXHAUSTED'
        assert (repo/'user_untracked.txt').read_text()=='PRESERVE'
        assert all((root/f'runtime/flow/save_result{i}.json').is_file() for i in range(2))
    dump(out/'summary.json',dict(status='PASS',test_only=True,scope='ISOLATED TWO-CYCLE REAL SUPERVISOR / FAKE WORKER; NOT RESEARCH RELEASE',controls=['two manifest saves commit and continue','read-only gate creates no tracked dirt','launch budget stops after2','old user untracked preserved'],external_Codex_sessions_launched=0,producer=ref(Path(__file__)),manager=ref(ROOT/'scripts/session_manager.py'),save_helper=ref(ROOT/'scripts/supervised_save.py')))
    print('PASS: two actual isolated supervisor cycles; no Codex launched')
if __name__=='__main__':main()
