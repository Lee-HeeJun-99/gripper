"""Isolated Git save controls; never stages the real repository or runs Codex."""
import argparse,copy,json,subprocess,tempfile
from pathlib import Path
from baseline_registry import ROOT,ref,dump
from supervised_save import validate,save,digest,untracked,git

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);controls=[]
    with tempfile.TemporaryDirectory(prefix='regrip-supervised-save-') as tmp:
        repo=Path(tmp);subprocess.run(['git','init','-q',str(repo)],check=True)
        for key,value in [('user.name','ReGrip isolated test'),('user.email','isolated@example.invalid'),('commit.gpgsign','false')]:subprocess.run(['git','config',key,value],cwd=repo,check=True)
        guard=repo/'guard.py';guard.write_text("import subprocess\nassert all(int(subprocess.check_output(['git','cat-file','-s',':'+p]))<50000000 for p in subprocess.check_output(['git','diff','--cached','--name-only']).decode().splitlines())\n")
        subprocess.run(['git','add','guard.py'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','Isolated baseline'],cwd=repo,check=True)
        old=repo/'old_user_work.txt';old.write_text('PRESERVE');old_untracked=untracked(repo);head=git(repo,'rev-parse','HEAD')
        f=repo/'product_prototype/stage12_integrated/validation/new/summary.json';f.parent.mkdir(parents=True);f.write_text('{"status":"FAIL","scope":"TEST FIXTURE"}\n')
        r=dict(path=str(f.relative_to(repo)),SHA256=digest(f));request=dict(expected_HEAD=head,message='Isolated actual save test',files=[r],results=[r])
        assert validate(repo,request,head,old_untracked)==[r['path']]
        variants=[]
        x=copy.deepcopy(request);x['expected_HEAD']='0'*40;variants.append(('wrong HEAD',x))
        x=copy.deepcopy(request);x['files'][0]['SHA256']='0'*64;variants.append(('stale hash',x))
        x=copy.deepcopy(request);x['files']*=2;variants.append(('duplicate paths',x))
        x=copy.deepcopy(request);x['files']=[];variants.append(('empty save',x))
        x=copy.deepcopy(request);x['results']=[];variants.append(('no results',x))
        x=copy.deepcopy(request);x['files'][0]['path']='../escape';variants.append(('path traversal',x))
        x=copy.deepcopy(request);x['files'].append(dict(path='old_user_work.txt',SHA256=digest(old)));variants.append(('old user data',x))
        for name,x in variants:
            try:validate(repo,x,head,old_untracked)
            except (ValueError,KeyError,TypeError):controls.append(dict(name=name,rejected=True))
            else:raise AssertionError(name+' accepted')
        result=save(repo,request,head,old_untracked,guard,digest(guard));assert result['after_HEAD']!=head and old.read_text()=='PRESERVE';assert not git(repo,'status','--porcelain','--untracked-files=no')
        controls.append(dict(name='exact indexed-hash guarded local commit',passed=True))
        controls.append(dict(name='preexisting untracked data preserved',passed=True))
        # A second real cycle verifies clean commit handoff, not just dry run.
        second=repo/'product_prototype/stage12_integrated/validation/new2/summary.json';second.parent.mkdir(parents=True);second.write_text('{"status":"PASS","scope":"TEST FIXTURE"}\n')
        head=result['after_HEAD'];r=dict(path=str(second.relative_to(repo)),SHA256=digest(second));request=dict(expected_HEAD=head,message='Second isolated cycle',files=[r],results=[r])
        result=save(repo,request,head,old_untracked,guard,digest(guard));assert result['after_HEAD']!=head
        controls.append(dict(name='second sequential local save',passed=True))
    dump(out/'summary.json',dict(status='PASS',test_only=True,scope='ISOLATED GIT SUPERVISOR TESTS ONLY; NO RESEARCH PASS',controls=controls,producer=ref(Path(__file__)),helper=ref(ROOT/'scripts/supervised_save.py'),external_Codex_sessions_launched=0))
    print(json.dumps(dict(status='PASS',controls=len(controls),real_research_repository_staged=False)))
if __name__=='__main__':main()
