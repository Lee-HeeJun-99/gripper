"""Actual SQLite persistence, process interruption and integrity checks, NOT Optuna."""
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
from integrated_common import OUT,ROOT,write_json

def command(root,*args):return [sys.executable,str(ROOT/'tools/integrated_search.py'),'--out',str(root),'--metric','hermite',*args]
def execute(root,*args):
    p=subprocess.run(command(root,*args),capture_output=True,text=True,timeout=90)
    log=OUT/'search_checks'/(root.name+'_'+str(time.time_ns())+'.log');log.write_text(p.stdout+p.stderr)
    return p
def clone_db(source,target):
    target.mkdir();a=sqlite3.connect(source/'research_grid.sqlite3');b=sqlite3.connect(target/'research_grid.sqlite3');a.backup(b);a.close();b.close()

def main():
    directory=OUT/'search_checks';directory.mkdir(parents=True,exist_ok=False);study=OUT/'search_hermite';main=json.loads((study/'summary.json').read_text());checks={}
    failed=[r for r in main['trials'] if r['status']=='failed'];checks['failed_has_no_objective']=len(failed)==1 and failed[0]['metrics']['objective_values'] is None
    checks['no_duplicate_physical_designs']=len({r['design_sha256'] for r in main['trials']})==len(main['trials']) and main['grid_count']==30
    p=execute(study,'--limit','1');after=json.loads((study/'summary.json').read_text());checks['completed_resume_no_duplicate']=p.returncode==0 and after['complete']==main['complete']
    seed=directory/'seed';p=execute(seed,'--limit','3');repro=json.loads((seed/'summary.json').read_text());original={r['design_sha256']:r for r in main['trials']}
    checks['seed_reproducibility']=p.returncode==0 and repro['complete']==3 and all(r['metrics']==original[r['design_sha256']]['metrics'] for r in repro['trials'] if r['status']=='complete')
    interrupted=directory/'interrupted';log=(directory/'interrupted_process.log').open('x')
    process=subprocess.Popen(command(interrupted,'--limit','1','--delay-after-running','2'),stdout=log,stderr=subprocess.STDOUT);running=False;started=time.monotonic()
    try:
        while time.monotonic()-started<15 and process.poll() is None:
            try:
                with sqlite3.connect(interrupted/'research_grid.sqlite3') as db:running=db.execute('SELECT count(*) FROM trials WHERE status="running"').fetchone()[0]>0
            except sqlite3.Error:pass
            if running:break
            time.sleep(.05)
    finally:
        if process.poll() is None:process.terminate()
        process.wait(timeout=10);log.close()
    p=execute(interrupted,'--limit','3');continued=json.loads((interrupted/'summary.json').read_text())
    checks['real_process_interruption_resume']=running and process.returncode!=0 and p.returncode==0 and continued['complete']==3 and all(r['metrics']==original[r['design_sha256']]['metrics'] for r in continued['trials'] if r['status']=='complete')
    bad=directory/'bad_identity';clone_db(study,bad)
    with sqlite3.connect(bad/'research_grid.sqlite3') as db:db.execute('UPDATE metadata SET value=? WHERE key="identity"',('{}',))
    checks['identity_mismatch_rejected']=execute(bad,'--limit','1').returncode!=0
    bad=directory/'bad_result';clone_db(study,bad)
    with sqlite3.connect(bad/'research_grid.sqlite3') as db:db.execute('UPDATE trials SET result=? WHERE design=(SELECT design FROM trials WHERE status="complete" LIMIT 1)',('{"stiffness_ratio":999999}',))
    checks['damaged_objective_rejected']=execute(bad,'--limit','1').returncode!=0
    write_json(directory/'summary.json',dict(checks=checks,passed=all(checks.values()),scope='deterministic static-FEM SQLite workflow; Optuna trial count remains zero'))
    print(checks)

if __name__=='__main__':main()
