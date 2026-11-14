"""Final delta checks and evidence-integrity test, no reuse of test PASS flags."""
import ast
import argparse
import json
from pathlib import Path
import subprocess
import sys
from verification_common import ROOT,sha,write_json,assert_build_current
from optimize import validate_gate

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/next_phase/final_quality');a=p.parse_args()
    out=a.out;out.mkdir(parents=True,exist_ok=False)
    results=[]
    for pattern in ('test_research_models.py','test_experiment_contract.py','test_research_runner.py'):
        cmd=[sys.executable,'-m','unittest','discover','-s','tests','-p',pattern,'-v']
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
        (out/(pattern+'.log')).write_text(r.stdout+r.stderr);results.append(dict(pattern=pattern,exit_code=r.returncode,command=cmd))
    syntax=[]
    for folder in ('tools','tests','models','experiments'):
        for path in (ROOT/folder).rglob('*.py'):
            ast.parse(path.read_text(),filename=str(path));syntax.append(str(path.relative_to(ROOT)))
    old=json.loads((ROOT/'reports/REVALIDATION_EVIDENCE_MANIFEST.json').read_text())
    errors=[p for p,h in old['files'].items() if sha(ROOT/p)!=h]
    errors += [p for p,h in old['report_sha256'].items() if sha(ROOT/'reports'/p)!=h]
    assert_build_current();validate_gate(ROOT/'results/revalidation_20261114T132734Z/physics_release/gate.json')
    write_json(out/'summary.json',dict(tests=results,syntax_files=syntax,syntax_passed=True,old_evidence_errors=errors,
        old_gate_integrity=True,passed=all(r['exit_code']==0 for r in results) and not errors,
        static_analysis_scope='syntax only; full lint/type analysis NOT RUN'))
    print([(r['pattern'],r['exit_code']) for r in results],len(syntax),'syntax files')
    if any(r['exit_code'] for r in results):raise SystemExit(1)

if __name__=='__main__':main()
