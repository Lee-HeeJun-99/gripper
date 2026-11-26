"""Index only executed fixture geometry; leave full capacity/fixture tasks open."""
import json,datetime,subprocess
from baseline_registry import ROOT,REPO,ref,dump
def main():
    src=ROOT/'hardware_test/fixtures/AK_collet_stand1/summary.json';audit=ROOT/'hardware_test/inspection/AK_collet_stand1/summary.json'
    d=json.loads(src.read_text());v=json.loads(audit.read_text());assert d['status']=='FIXTURE_NOMINAL_GEOMETRY_PASS' and v['status']=='FIXTURE_GEOMETRY_AUDIT_PASS' and v['source']==ref(src)
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());name='AK_collet_reaction_fixture_geometry';assert not any(t['id']==name for t in q['tasks'])
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    q['tasks'].append(dict(id=name,track='C',status='PASS',scope='Six actual fixture CAD parts plus actual AK hub/bolt, nominal clearance and independent closed-mesh audit only; no proof load or complete rig',result='hardware_test/inspection/AK_collet_stand1/summary.json',target_revision='revAK_integral2',last_run_utc=now,consecutive_runs=1,registration_note='Post-execution result indexing, no fabricated prior registration'))
    h['cycles'].append(dict(task=name,track='C',time_utc=now,status='PASS',evidence=ref(audit),HEAD_at_result_indexing=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),execution='current interactive session; no external launch'))
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
if __name__=='__main__':main()
