"""Record bounded actual-pad pressure analysis without release promotion or Git writes."""
import json,datetime,shutil,subprocess
from baseline_registry import ROOT,REPO,ref,dump
from integrated_release_gate import audit

def main():
    assert not (ROOT/'runtime/STOP').exists()
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert head=='02b9ca781bc3adb95848d97f0fd3f942472dc570'
    out=ROOT/'validation/transmission/AK_pad_pressure_cycle1'
    shutil.copyfile(__file__,out/'producer.py')
    d=json.loads((out.parent/'AK_pad_pressure1/summary.json').read_text())
    v=json.loads((out.parent/'AK_pad_pressure_verify2/summary.json').read_text())
    e=json.loads((out/'execution.json').read_text())
    assert all(d['checks'].values()) and all(v['checks'].values())
    assert [e[k]['exit_code'] for k in ('analysis','verification','verification2')]==[0,1,0]
    release=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))
    dump(out/'release_summary.json',release)
    report=ROOT/'reports/AK_PAD_PRESSURE_ENVELOPE_20261126.md'
    report.write_text('''# AK separate finite pad pressure envelope

This cycle resolves a specific uncertainty in the existing finite support
candidate: a uniform centroid pressure basis is sufficient but not necessary
for rigid normal equilibrium. This is a new distributed-pressure analysis of
actual CAD, not another placement/interference scan or a support adoption.

All235 AK candidate STEP hashes, existing three pad STEP hashes and upstream
geometry dependencies were checked. On the actual Palm/pad common faces,
two radius1mm uniform patches centered1.5mm in +x from pad0 and pad2 centers
carry0.5N each. Each actual area is pi mm²; pressure0.1591549431N/mm² is an
explicit conditional witness, not an allowable or predicted elastic pressure.
The positive patches balance [0,0,-1,0,14,0] N/Nmm with maximum residual
3.56e-15. The old centroid-only solution [0.52,-0.04,0.52]N rejects this case.
Thus that basis cannot certify all possible eccentric pressure equilibria.

For any nonnegative normal pressure on these actual footprints, the center
of pressure lies in their convex hull. The exact x projection is[-28,15.5]mm.
The old1N/My40Nmm case needs x40mm,24.5mm outside the necessary bound, and
remains impossible even with arbitrary nonuniform pressure. Boundary measures
cannot fix that exclusion. No full two-dimensional envelope is claimed.
All normal contact wrenches still have Fx=Fy=Mz=0 and Fz>=0. Uplift, lateral
and torsional retention and connected ground attachment remain unresolved.

Independent verification uses eight .001/.002mm solid volume/first-moment
slices on both actual Palm and pad sides, cross-product equilibrium, virtual
work, and cylinder volume-derived x extents. A deliberately shifted patch
crossing the pad edge has area0.5498301022mm² instead of pi and is rejected.
Every declared check passed. Initial verifier exit1 from NumPy bool_ JSON
serialization is retained under AK_pad_pressure_verify1 with original producer,
log and explicit failure summary; corrected verifier has a new output tag.
Three bounded children used4GiB/420s and one thread; no SOFA run.

This does not solve elasticity, pressure compatibility under deflection,
preload, material/strength, actual operating loads, full Palm energy or mesh
convergence. CAD/BOM and all historical PASS/FAIL scope remain unchanged.
Read-only release audit remains INTEGRATED_NOT_QUALIFIED. No inference of
system release from this rigid witness is permitted. Further C work requires
positive side/torsion/lift-off retention with a finite connected ground path;
repeat pressure patch scans are not progress. Independent A/B tasks remain.
Supervisor local save is PENDING. No Git add/commit or manager launch occurred.
''')
    status='FINITE_PRESSURE_ENVELOPE_VERIFIED_FULL_ATTACHMENT_BLOCKED'
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    summary=dict(status=status,starting_HEAD=head,task='AI_whole_palm_support',track='C',time_utc=now,
        analysis=ref(out.parent/'AK_pad_pressure1/summary.json'),verification=ref(out.parent/'AK_pad_pressure_verify2/summary.json'),
        preserved_failures=[ref(out.parent/'AK_pad_pressure_verify1/summary.json')],
        producer=ref(out/'producer.py'),plan=ref(out/'plan.json'),execution=ref(out/'execution.json'),
        logs=[ref(out/n) for n in ('analysis.log','verification.log','verification2.log')],report=ref(report),
        dependencies=[ref(ROOT/'scripts'/n) for n in ('baseline_registry.py','integrated_release_gate.py')],
        release=ref(out/'release_summary.json'),release_status=release['status'],release_errors=len(release['errors']),
        verified=True,whole_system_release=False,adopted=False,SOFA_runs=0,
        physical_elastic_pressure=None,ground_attachment=None,owned_live_analysis_children=0,
        save_status='PENDING_SUPERVISOR_LOCAL_SAVE')
    dump(out/'summary.json',summary)
    q=json.loads((ROOT/'INTEGRATED_TASKS.json').read_text());assert not any(t['status']=='RUNNING' for t in q['tasks'])
    t=next(t for t in q['tasks'] if t['id']==summary['task'])
    t.update(last_run_utc=now,consecutive_runs=t.get('consecutive_runs',0)+1,last_cycle_status=status,last_diagnostic=ref(out/'summary.json'),
        reason='Actual finite pressure patches support1N/My14Nmm beyond centroid basis; universal footprint excludes old40Nmm. Full six-DOF retention and ground attachment still absent.',
        followup_hypothesis='Require finite positive side/torsion/lift-off retention and connected ground path; no more pad/pressure scans. Actual elastic/preload/load evidence required before strength.',
        selection_note='C distributed-pressure uncertainty resolved in one bounded analysis. C remains READY only for a distinct retention mechanism; independent A/B work remains.')
    dump(ROOT/'INTEGRATED_TASKS.json',q)
    h=json.loads((ROOT/'TRACK_HISTORY.json').read_text());h['cycles'].append(dict(task=t['id'],track='C',time_utc=now,status=status,evidence=ref(out/'summary.json'),starting_HEAD=head,save_status='PENDING_SUPERVISOR_LOCAL_SAVE',execution='authorized_20261126_4 cycle9; three bounded children completed, exit0/1/0; no Git writes'))
    dump(ROOT/'TRACK_HISTORY.json',h)
    text='''# Bounded C cycle — actual finite-pressure envelope (2026-11-26)

Started at02b9ca781bc3adb95848d97f0fd3f942472dc570. Supervisor local save PENDING;
no Git add/commit attempted or new commit claimed. Actual result:
product_prototype/stage12_integrated/validation/transmission/AK_pad_pressure_cycle1/summary.json.

Actual common Palm/pad faces contain two finite pi mm² patches balancing
1N compression/My14Nmm with positive pressure and3.56e-15 residual. Centroid
basis needs-0.04N and rejects that case; this is a new pressure-redistribution
analysis, not a repeated geometry scan. Exact x support[-28,15.5]mm excludes
old40Nmm even for arbitrary pressure. All235AK source hashes verified.
Independent eight solid slices/cross products/virtual work and corrupted patch
rejection pass. Initial JSON serialization exit1 preserved with producer/log;
corrected verification uses new tag. Three4GiB/420s children exit0/1/0; no SOFA.

No elastic pressure/preload/strength/full Palm/6DOF/energy PASS. Pads remain
unconnected external candidates. Read-only release INTEGRATED_NOT_QUALIFIED.
Next C requires distinct finite positive side/torsion/lift-off retention and
connected ground path; no repeated patch scans. Independent A/B READY work
remains. Historical failures, CAD/BOM and unrelated untracked work preserved.
No RUNNING queue records or owned live analysis children at handoff.
Exact save manifest: product_prototype/stage12_integrated/runtime/authorized_20261126_4/save_request9.json.
No SDK,criteria,manager,Stage3,hardware changes, external launch or Git write.

'''
    for p in [ROOT/'CHECKPOINT.md',ROOT/'AUTONOMOUS_RESUME.md',REPO/'reports/INTEGRATED_CURRENT_STATUS.md',REPO/'reports/INTEGRATED_NEXT_TASKS.md']:
        p.write_text(text+p.read_text())
    print(json.dumps(dict(status=status,release_status=release['status'],errors=len(release['errors']))))
if __name__=='__main__':main()
