"""Record the bounded external pad candidate; no adoption or system promotion."""
import json,shutil,datetime,subprocess
from baseline_registry import ROOT,REPO,S1,ref,dump
from integrated_release_gate import audit

def main():
    out=ROOT/'validation/transmission/AK_three_pad_cycle1'
    assert not (ROOT/'runtime/STOP').exists()
    shutil.copyfile(__file__,out/'producer.py')
    d=json.loads((out.parent/'AK_three_pad2/summary.json').read_text())
    v=json.loads((out.parent/'AK_three_pad_verify2/summary.json').read_text())
    assert d['geometry_pass'] and all(v['checks'].values())
    execution=json.loads((out/'execution.json').read_text())
    assert [execution[k]['exit_code'] for k in ('analysis','analysis2','verification','verification2')]==[1,0,1,0]
    release=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))
    dump(out/'release_summary.json',release)
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    report=ROOT/'reports/AK_THREE_PAD_SUPPORT_20261126.md'
    report.write_text('''# Separate AK finite three-pad support candidate

One fixed design evaluated: three radius3mm, height6mm cylindrical pads,
centers at radius25mm and60/180/300degrees; top z=-12mm, bottom z=-18mm.
New STEP/STL artifacts are external candidates only. AK235 parts and adopted
RevAA CAD/BOM are unchanged; no bottom foundation is specified or qualified.

All235 actual part source hashes verified before geometry analysis. Each pad
contacts the actual Palm underside over28.2743338823mm².702 exact other-part
intersection volumes and three Palm volumes are below1e-7mm³. No connection
of these pads to ground is implied. Independent .001/.002mm volume slices
reproduce contact areas within5.3e-12mm² and centroids within1.5e-13mm.

Normal unit reaction wrench is [0,0,1,y,-x,0], in N and Nmm about the Palm
origin. Uniform pressure yields a rank3 basis. Independent cross products
and virtual work agree; a1% area perturbation is rejected. Centered -1N
compression needs1/3N per pad. Uplift needs negative normal reactions and
is rejected. Fx and Mz cannot be balanced. A1N compressive case with My40Nmm
also requires a negative reaction in this basis. This is a conditional
pressure-basis test, not certification of arbitrary distributed contact.
The latter case is also outside the pad footprint x-extent; no allowable
or material strength is assigned. No actual assembly load envelope is known.

Thus the candidate identifies finite usable compression bearing surfaces,
but fails complete support: positive lift-off/lateral/torsion retention,
foundation attachment, preload/friction, compliance and strength remain open.
No full-Palm equilibrium, mesh convergence, global energy or release PASS.
Do not replace the old unsupported annular fixation with fixed pad nodes.

Failure records retained: first export used a double extension and exited1;
first verifier could not JSON-serialize NumPy bool_ and exited1. Original
producers, inputs, logs and partial artifacts remain under their own tags.
Corrected analysis and verifier exit0, with all stated checks inspected.
Four analysis children, each4GiB/420s and one thread; no SOFA run. The read-only
release audit remains INTEGRATED_NOT_QUALIFIED. Supervisor local save pending;
the worker did not attempt git add/commit, push or launch managers.

Next independent design must supply side/torsion and lift-off retention and
a finite connected ground path, with actual interference/load/preload bounds.
Do not repeat this fixed three-pad scan or refine the old unsupported P1 solve.
''')
    status='FINITE_SUPPORT_CANDIDATE_VERIFIED_SIX_DOF_ATTACHMENT_BLOCKED'
    summary=dict(status=status,starting_HEAD='593a8706f47d613f09d57d2a3628fb4bd5e9a3ab',task='AI_whole_palm_support',track='C',time_utc=now,
        analysis=ref(out.parent/'AK_three_pad2/summary.json'),verification=ref(out.parent/'AK_three_pad_verify2/summary.json'),
        preserved_failures=[ref(out.parent/n/'summary.json') for n in ('AK_three_pad1','AK_three_pad_verify1')],
        execution=ref(out/'execution.json'),logs=[ref(out/(n+'.log')) for n in ('analysis','analysis2','verification','verification2')],
        plan=ref(out/'plan.json'),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/baseline_registry.py'),ref(ROOT/'scripts/integrated_release_gate.py')],
        report=ref(report),release=ref(out/'release_summary.json'),release_status=release['status'],release_errors=len(release['errors']),
        contact_areas_mm2=[r['area_mm2'] for r in d['rows']],intersection_checks=705,normal_wrench_rank=d['rank'],
        verified=True,whole_system_release=False,adopted=False,physical_preload_N=None,foundation_attachment=None,
        save_status='PENDING_SUPERVISOR_LOCAL_SAVE',owned_live_analysis_children=0)
    dump(out/'summary.json',summary)
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text())
    assert not any(t['status']=='RUNNING' for t in q['tasks'])
    task=next(t for t in q['tasks'] if t['id']=='AI_whole_palm_support')
    task.update(last_run_utc=now,consecutive_runs=task.get('consecutive_runs',0)+1,last_cycle_status=status,
        last_diagnostic=ref(out/'summary.json'),reason='Separate finite three-pad CAD contacts actual AK underside and clears all234other parts; independent contact integration/wrench verification passes. Normal wrench rank3; uplift/lateral/torsion and ground attachment unqualified.',
        followup_hypothesis='Add separately tagged finite positive side/torsion/lift-off retention and connected ground attachment with explicit load/preload path. Do not treat three pads as fixed nodes or rerun the same scan.',
        selection_note='C finite support cycle complete, full support remains READY with new mechanism required; independent A/B tracks remain executable.')
    dump(ROOT/'INTEGRATED_TASKS.json',q)
    h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task=task['id'],track='C',time_utc=now,status=status,evidence=ref(out/'summary.json'),starting_HEAD=summary['starting_HEAD'],save_status='PENDING_SUPERVISOR_LOCAL_SAVE',execution='authorized_20261126_4 cycle7; four bounded children completed; no Git writes'))
    dump(ROOT/'TRACK_HISTORY.json',h)
    text='''# Bounded C cycle — separate finite three-pad support (2026-11-26)

Started at593a8706f47d613f09d57d2a3628fb4bd5e9a3ab. Supervisor local save PENDING;
no git add/commit attempted. Actual result: product_prototype/stage12_integrated/validation/transmission/AK_three_pad_cycle1/summary.json.

One separately tagged external candidate: three radius3mm/height6mm pads at
radius25mm,60/180/300deg, top z=-12mm. All235AK source hashes verified.
Actual underside contact28.2743338823mm² each;705intersection checks below
1e-7mm³. Independent two-width volume/centroid reconstruction and virtual work
pass;1% area corruption rejected. This is finite compression support geometry,
not AK/RevAA adoption or installed grounding. Wrench basis rank3; centered
-1N requires1/3N per pad, while uplift/Fx/Mz and eccentric case are rejected.
No full support, strength, preload/friction, FEM convergence or energy PASS.

Export extension error(exit1) and NumPy JSON serialization error(exit1) retained
with original producers/logs/partial artifacts. Corrected analysis and verifier
exit0 with checks inspected; four children4GiB/420s, one thread, no SOFA.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED. Historical failures
and unrelated untracked files unchanged; adopted CAD/BOM unchanged.

Next C requires new side/torsion/lift-off retention and connected ground path;
do not rerun pad scans or fix unsupported nodes. Independent A/B READY work
remains. No RUNNING task records or owned live analysis children at handoff.
Exact save request: product_prototype/stage12_integrated/runtime/authorized_20261126_4/save_request7.json.
No SDK/criteria/manager/Stage3/hardware changes, Git writes or external launch.

'''
    for p in [ROOT/'CHECKPOINT.md',ROOT/'AUTONOMOUS_RESUME.md',REPO/'reports/INTEGRATED_CURRENT_STATUS.md',REPO/'reports/INTEGRATED_NEXT_TASKS.md']:
        p.write_text(text+p.read_text())
    print(json.dumps(dict(status=status,release_status=release['status'],errors=len(release['errors'])),indent=2))
if __name__=='__main__':main()
