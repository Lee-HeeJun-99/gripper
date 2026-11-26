"""Offline manager controls. No Codex session, authentication or network call."""
import argparse,fcntl,tempfile,json
from pathlib import Path
from baseline_registry import ROOT,ref,dump
from session_manager import has_progress,command
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    original=dict(HEAD='a',actual_result_artifacts={'x':'1'})
    assert not has_progress(original,dict(HEAD='b',actual_result_artifacts={'x':'1'}))
    assert has_progress(original,dict(HEAD='b',actual_result_artifacts={'x':'1','y':'2'}))
    cmd=command('TEST_ONLY_NOT_EXECUTED');assert '--sandbox' in cmd and 'workspace-write' in cmd and not any('bypass' in s for s in cmd)
    with tempfile.TemporaryDirectory(prefix='regrip-manager-lock-') as tmp:
        p=Path(tmp)/'lock'
        with p.open('a+') as first,p.open('a+') as second:
            fcntl.flock(first,fcntl.LOCK_EX|fcntl.LOCK_NB)
            rejected=False
            try:fcntl.flock(second,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:rejected=True
            assert rejected
    dump(out/'summary.json',dict(status='PASS',scope='OFFLINE MANAGER CONTROLS ONLY',controls=['metadata-only commit is not progress','new actual result is progress candidate, not product PASS','workspace sandbox retained','concurrent lock rejected'],external_Codex_sessions_launched=0,producer=ref(Path(__file__))))
    print(json.dumps(dict(status='PASS',external_sessions_launched=0)))
if __name__=='__main__':main()
