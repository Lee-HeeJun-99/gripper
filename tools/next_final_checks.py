"""Final hardened-component regression; legacy 45-gate evidence remains unchanged."""
import subprocess
import sys
from research_trial import run
from verification_common import ROOT,write_json,sha

def main():
    out=ROOT/'results/next_phase/final_finite';out.mkdir(parents=True,exist_ok=False);records={}
    for name,kw in [('base',{}),('halfdt',dict(dt=.00025)),('mesh',dict(n=21,connectors=list(range(2,21,2))))]:
        records[name]=run(out/name,length=30,k=1,load=1e-4,duration=3,finite=True,**kw)
    cmd=[sys.executable,str(ROOT/'tools/finite_objectivity.py'),'--out',str(out/'objectivity'),'--reference',str(out/'base')]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(out/'objectivity_command.log').write_text(p.stdout+p.stderr)
    import json
    objectivity=json.loads((out/'objectivity/summary.json').read_text())
    checks={name:r['status']=='PASS' for name,r in records.items()};checks['objectivity']=objectivity['status']=='PASS'
    for name,tol in [('halfdt',.001),('mesh',.01)]:checks[name+'_convergence']=abs(records[name]['tip_deflection_mm']/records['base']['tip_deflection_mm']-1)<tol
    write_json(out/'gate.json',dict(checks=checks,passed=all(checks.values()),
        binary_sha256=records['base']['binary_sha256'],metrics_sha256={name:sha(out/name/'metrics.json') for name in records},
        scope='EXPERIMENTAL objective connector with conservative mathematical kernel; three SOFA cases + whole-scene covariance, not full gripper certification'))
    print(checks)

if __name__=='__main__':main()
