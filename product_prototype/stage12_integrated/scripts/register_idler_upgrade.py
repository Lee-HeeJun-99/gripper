"""Register the actual structural mechanism before its CAD trial."""
import json
from baseline_registry import ROOT,dump
def main():
    p=ROOT/'INTEGRATED_TASKS.json';q=json.loads(p.read_text());name='idler_integral_M3_shoulder'
    if any(t['id']==name for t in q['tasks']):raise ValueError('Already registered')
    q['tasks'].append(dict(id=name,track='A',priority=0,status='READY',hypothesis='Larger finite runout and integral metal shoulder improve Idler section modulus while preserving positive preload bypass and3mm pulley journal',difference='Actual load-carrying mechanism/shaft and nut change, not a tension or dt retry',criteria='Finite actual CAD, metal preload path, nominal interference and independent geometry/motion checks; no material/thread strength certification from a nominal diameter',prerequisites=[],system_gate_contribution=4,cost='4GiB/420s per child',fallback='double_supported_idler',last_run_utc=None,consecutive_runs=0))
    dump(p,q)
if __name__=='__main__':main()
