"""Persist new runner/source/loader guard unit evidence separately from physics."""
import sys
import shutil
from curve_common import ROOT,OUT,sha,write_json
from closure_validation_suite import logged


def main():
    out=OUT/'patch_refinement_v2/checks_v2';out.mkdir(exist_ok=False)
    sources=list((ROOT/'tools').glob('curve_*.py'))+list((ROOT/'tests').glob('test_patch_*.py'))+[ROOT/'tests/test_local_history_guards.py']
    write_json(out/'sources.json',{str(p.relative_to(ROOT)):sha(p)for p in sources})
    for p in sources:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    commands=[('patch_guards',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_patch_*.py','-v']),('local_history_guard',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_local_history_guards.py','-v']),('python_compile',[sys.executable,'-m','py_compile']+sources)]
    results={name:logged(command,out/name,180)for name,command in commands}
    write_json(out/'summary.json',dict(status='PASS'if all(r['exit_code']==0 for r in results.values())else'FAIL',checks=results,scope='source/runner unit guards only,NOT SOFA convergence gates'))
    print({name:r['exit_code']for name,r in results.items()})


if __name__=='__main__':main()
