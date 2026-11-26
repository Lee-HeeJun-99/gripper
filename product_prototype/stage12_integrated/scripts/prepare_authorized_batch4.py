"""One-time operator queue authorization; NEVER starts a worker or resets usage."""
import json
from baseline_registry import ROOT,ref,dump
def main():
    authorization=ROOT/'AUTOMATION_AUTHORIZATION_20261126_4.json'
    c=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());assert c['revision']=='revAK_integral2'
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());h=json.loads((ROOT/'TRACK_HISTORY.json').read_text())
    name='AK_protected_maximum_load';assert not any(t['id']==name for t in q['tasks']),'Do not repeat allocation preparation'
    assert not any(t['status']=='RUNNING' for t in q['tasks'])
    q['tasks'].append(dict(id=name,track='A',priority=1,status='READY',hypothesis='Actual one-face grounded support removes the known bearing bypass but force cap needs rated/calibrated friction/spring and bounded transient energy. Simpler rated mechanisms may reduce missing bounds.',difference='Use actual AK inertia/topology and coupled axial clamp reaction, not old minimum-only HPMC or assumed static tension as peak protection',prerequisites=[],criteria='Real source-backed normal/trigger/maximum load separation; bound torque/radius/inertia/tendon stiffness/initial energy/delay and failure paths; actual CAD interfaces and unchanged convergence/material criteria. No guessed friction/preload certification',implementation='Reuse jam_energy2 and actual AK CAD; independently verify energy bound; investigate rated simpler actuator/limiter if current architecture cannot be qualified',fallback='rated_low_torque_actuator_or_independent_disconnect',system_gate_contribution=5,cost='4GiB/420seconds per analysis child, one3600second session maximum',target_revision=c['revision'],target_parts=c['parts'],target_candidate=c['definition'],last_run_utc=None,consecutive_runs=0))
    h['new_authorization']=dict(allocation_ID='authorized_20261126_4',authorization=ref(authorization),maximum_new_sessions=10,seconds_per_session=3600,usage_authority='runtime/authorized_20261126_4/status.json',legacy_budget_fields='Old automatic_launches_* fields retain original six-session consumed allocation only; not new usage')
    q['active_authorization']=ref(authorization)
    dump(ROOT/'INTEGRATED_TASKS.json',q);dump(ROOT/'TRACK_HISTORY.json',h)
    print(json.dumps(dict(status='NEW_ALLOCATION_INDEXED_NOT_LAUNCHED',old_usage_preserved=True,new_maximum=10,per_session_seconds=3600)))
if __name__=='__main__':main()
