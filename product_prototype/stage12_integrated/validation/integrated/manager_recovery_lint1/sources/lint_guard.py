"""Installed pyflakes undefined-name/local check only, never physics approval."""
import argparse,ast,json,shutil
from pathlib import Path
from pyflakes.checker import Checker
from pyflakes.messages import UndefinedName,UndefinedLocal
from baseline_registry import ROOT,ref,dump
def errors(text,name):return [str(m) for m in Checker(ast.parse(text),filename=name).messages if isinstance(m,(UndefinedName,UndefinedLocal))]
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);snap=out/'sources';snap.mkdir();failures=[];sources=[]
    for file in sorted((ROOT/'scripts').glob('*.py')):
        copied=snap/file.name;shutil.copyfile(file,copied);sources.append(ref(copied));failures+=errors(file.read_text(),file.name)
    rejected=bool(errors('answer = definitely_missing_symbol\n','NEGATIVE_CONTROL_NOT_EXECUTED'))
    result=dict(status='PASS' if not failures and rejected else 'FAIL',scope='STATIC UNDEFINED NAME/LOCAL CHECK ONLY; NOT ALL STYLE, RUNTIME OR PHYSICAL VALIDATION',errors=failures,negative_control_rejected=rejected,sources=sources,producer=ref(snap/Path(__file__).name))
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],undefined_errors=failures,negative_control_rejected=rejected)));raise SystemExit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
