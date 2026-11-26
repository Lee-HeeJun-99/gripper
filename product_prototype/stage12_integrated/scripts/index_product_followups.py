"""Index actual current-session work and register still-unexecuted followups.
Late indexing is explicit; it is not a claim of preregistered task timestamps.
"""
import json
from baseline_registry import ROOT,dump
def main():
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());ids={t['id'] for t in q['tasks']}
    actual=[
        ('shared_pilot_alignment','A',0,'Actual common pilot register removes motor/bridge bolt-float centering dependency','Finite CAD, interference, independent geometric audit and declared tolerance intervals; no total motor reaction/strength approval'),
        ('local_palm_tabs','C',1,'Local drive tabs preserve mount locations without a full heavy Palm annulus','Actual Palm subset, same non-Palm hashes and bolt support footprints, geometry audit; no strength promotion'),
        ('actual_palm_tab_unit_load','C',2,'Actual lightened-tab material needs a local load/compliance screen','Actual STEP submodel, finite1N washer load, force<1e-8N, moment<1e-10Nm, energy/residual<1e-8, mesh response1%; no full-Palm or material strength release'),
        ('catalog_fixed_clutch_interval','A',1,'A complete published nominal+tolerance clutch offers a different rated-load window from minimum-only HPMC','Primary manufacturer torque tolerance, actual conversion/dynamic demand and preserved geometry mismatch; no temperature/fault or installed-CAD claim')]
    for name,track,priority,hypothesis,criteria in actual:
        if name in ids:raise ValueError('Do not duplicate indexed tasks')
        q['tasks'].append(dict(id=name,track=track,priority=priority,status='READY',hypothesis=hypothesis,criteria=criteria,prerequisites=[],system_gate_contribution=3,cost='4GiB/420s per child',last_run_utc=None,consecutive_runs=0,registration_note='Retrospective task index of actual current-session implementation. Source snapshots establish methods; no preregistration timestamp claimed.'))
    for t in [
        dict(id='AH_collet_and_axial_capacity',track='A',priority=0,hypothesis='Actual minimum4.2mm shaft grip and spring axial load require a validated clamp/motor bearing path',criteria='Actual collet load model, finite engagement, torque/axial capacity and material bounds; no force cap from guessed friction',fallback='rated_stock_clutch_and_actuator'),
        dict(id='AI_whole_palm_support',track='C',priority=1,hypothesis='Local tab compliance alone does not bound the full Palm and Root reactions',criteria='Same253-part geometry, actual full-Palm support/load ports, static equilibrium and1% response convergence; actual material proof remains separate',fallback='reinforced_local_tabs'),
        dict(id='actual_finger_load_ports',track='B',priority=2,hypothesis='Actual free PET end/root clamp/terminal contact must connect tendon load to assembled Finger behavior',criteria='Use actual-boundary map and independent reference only within proven scope; full deformation, friction, gap and load equilibrium',fallback='simpler_replaceable_finger_cartridge')]:
        if t['id'] in ids:raise ValueError('Duplicate followup')
        t.update(status='READY',prerequisites=[],system_gate_contribution=4,cost='bounded actual product validation, no random parameter sweep',last_run_utc=None,consecutive_runs=0);q['tasks'].append(t)
    dump(ROOT/'INTEGRATED_TASKS.json',q)
if __name__=='__main__':main()
