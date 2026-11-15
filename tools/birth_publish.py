"""Publish measured evidence without certifying incomplete downstream physics.

Run only after bounded children finish. Raw manifests are streamed, not loaded
into memory. Existing campaign raw and historical manifests are never changed.
"""
import csv,json,subprocess
from pathlib import Path
from birth_common import ROOT,OUT,BUILD,identity,sha,write_json

def read(p):
    return json.loads(p.read_text()) if p.exists() else {}

def main():
    pending=[p for p in (ROOT/'results/birth_20261115').rglob('process.json')if p.parent.parent.name=='grasp'and not(p.parent/'metrics.json').exists()]
    if pending:raise RuntimeError('refusing to hash running/incomplete physics outputs: '+str(pending))
    import birth_assess
    birth_assess.main()
    legacy=ROOT/'results/birth_20261115'
    evidence=ROOT/'reports/birth_evidence';evidence.mkdir(exist_ok=True)
    ident=identity();conv=read(OUT/'convergence.json')
    for name,path in [('v7_convergence',legacy/'convergence.json'),('structure_candidates',legacy/'structure_candidate_decisions.json'),('structural_study',legacy/'structure_refined/summary.json'),('optuna_workflow',legacy/'optuna_contracts/summary.json'),('event_math',legacy/'math_events/summary.json'),('sanitizer',legacy/'sanitizer/summary.json'),('energy_audit',OUT/'energy_audit.json'),('controlled_event_energy',OUT/'controlled_event_energy.json'),('memory_observations',OUT/'memory_observations.json')]:
        write_json(evidence/(name+'.json'),read(path))
    table=['| Diagnostic | Status | Translation relative | Rotation relative | Limit |','|---|---|---:|---:|---:|']
    for name,r in conv['comparisons'].items():
        d=r.get('relative_difference',{});table.append(f"| {name} | {r['status']} | {d.get('hold_displacement_mm','—')} | {d.get('hold_rotation_increment_rad','—')} | {r.get('limit','—')} |")
    convergence='The following statuses concern the historical **motion** diagnostic only; they do NOT certify convergence of dissipated energy or the full history field. Additional same-stage force/energy/loss comparisons are in convergence.json.\n\n'+'\n'.join(table)
    convergence+='\n\n| History friction-loss comparison | Status | Relative difference | Limit |\n|---|---|---:|---:|\n'
    for name,r in conv.get('history_dissipation_convergence',{}).items():convergence+=f"| {name} | {r['status']} | {r['relative_difference']} | {r['limit']} |\n"
    header='New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.\n\n'
    header+='Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.\n\n'
    header+=f"Birth plugin SHA256 `{ident['birth_build']['binary_sha256']}`; generated component SHA256 `{ident['birth_build']['generated_sha256']}`. Beam SHA256 `{ident['beam']['plugin_sha256']}`; SDK driver SHA256 `{ident['beam']['sdk_driver_sha256']}`.\n\n"
    chapters={
      '01_EVENT_DERIVATION':('PASS (smooth prescribed-event kernel); EXPERIMENTAL trajectory model',r'''For committed object-local material point a and current point b, define x(t)=a+t(b-a), g= SDF(x)-skin. Birth is the first transversal entering root alpha in [0,1]. End-state derivative is

`d alpha = -alpha n_birth dot d b / (n_birth dot (b-a))`.

This is the IFT for a frozen previous state and a local straight chord, not full SE(3) continuous dynamics. Root value uses double geometry; its AD derivative uses the same SDF normal. The transported post-birth increment is used in both scalar Commit and AD Force/Jacobian. A grazing denominator is explicitly rejected relative to chord length; no epsilon denominator is substituted. Full-step resolved birth/death chords are rejected and require actual substeps. ULP-scale unresolvable negative signed gaps are counted explicitly, not reported as resolved CCD.

60 smooth Sphere/Cylinder/Box birth force/Jacobian cases have max normalized FD error 1.3005749602279515e-9. Boundary branches are tested separately; no differentiability is asserted at contact, slip, endcap or corner transitions. The original .01-mm missing increment is recovered. See build unit stdout and independent math_events logs.'''),
      '02_SOFA_INTEGRATION':('PASS API scope; EXPERIMENTAL full model',r'''Independent `BirthAwareContact` is generated at configure time from the preserved production contact source plus new `BirthLaw.h`, `Crossing.h`, `HistoryCommit.inc`, `Journal.inc`. Old MaterialHistoryContact/Beam/golden/binaries are not replaced. Generated code and all transitive source hashes are checked before every run.

Actual addForce/addDForce/buildStiffnessMatrix accumulator tests include kFactor 0,2.5,-.25, finite differences, action/reaction and torque. Scalar Commit and AD next-state agree to 2.01e-17; scalar observer wrench versus AD agrees to 5.64e-18. Duplicate AnimateEnd at one time cannot Commit twice. Force/Jacobian/energy/record queries are pure. Pre-step implicit force evaluation still precedes end-state birth Commit: endpoint correction does NOT itself split the ODE event.'''),
      '03_GRID_BOUNDARY':('PASS unit scope; history convergence not implied',r'''Collapsed clipped intervals return the mathematically defined zero-capacity contact-boundary limit rather than dividing by u-l or replacing that denominator by epsilon. Exact and adjacent grid boundary cases, inactive state, recontact and finite derivatives are tested.

A second discrete-grid defect was found: nominal 10-mm edges were 9.99999999999999..10.000000000000014 mm. Strict ceil generated 1000 or1001 cells at .01 mm depending on rigid-frame roundoff. The new component canonicalizes a ratio only within32 machine epsilon times its scale of an integer; truly noninteger lengths retain ceil. 100 rigid coordinate transformations and a noninteger counterexample pass. This numerical-ID correction is NOT a relaxation of the1% history gate. New canonical-v8 results remain distinct from v7.'''),
      '04_FULL_CONVERGENCE':('FAIL / incomplete (see measured table)',convergence+'\n\nIndividual bounded-hold passes do not approve full grasp. Relative denominators and original limits are unchanged; absolute differences also appear in convergence.json. Every compared pair must have identical compiled identity, unchanged physical inputs and pass its underlying physics checks. A24-s base covers recovery, while18-s refinement runs do not cover final recovery. Same13.9<=t<14 measurements show history.005→.0025 friction-loss difference about26.3%, despite motion passing. A frozen planar analytic field diagnostic independently demonstrates return-map/interpolation noncommutation and energy representation error decreasing with refinement; it does NOT uniquely establish the full dynamic root cause. No artificial compensating dissipation is added.'),
      '05_EVENT_ENERGY':('PASS independent discrete contact scope; EXPERIMENTAL actual event energy',r'''Independent prescribed plane Stick/Slip/Birth/Death/Recontact tests verify the backward-step spring identity, Coulomb return loss and objective rotation transport. Born tangential elastic energy for kt=1 and extension .01 is .00005 force-mm. Resetting that stored state records a separate .00005 detachment inventory loss; it is not silently relabeled Coulomb heat. Large common rotation error is8.94e-17. See math_events/summary.json and run/stdout.log.

Actual SOFA controlled plane contact has only mass/contact/fixed zero-velocity object: no gravity, actuator, external load or damping. A single dt1 birth step restores history but adds about1e-4 force-mm to K+U, because its implicit force stage was still separated. Coarse dt.25 gives accidental near-zero error, NOT proof of exact energy integration. Further refinement dt.125,.0625,.03125,.015625,.0078125 gives energy defects about-1.2355e-5,-9.3112e-6,-6.2241e-6,-2.9242e-6,-1.5610e-6, tending down in magnitude. No-contact control is exactly0. These measured residuals are NOT relabeled numerical heat. See controlled_event_energy.json and actual per-event journal. The artificial coarse event dt is not the100-mm baseline dt. This distinguishes endpoint history correction from full ODE event resolution.'''),
      '06_COUPLED_ENERGY':('BLOCKED full closure; partial engine journal implemented',r'''Optional in-engine journal records actual begin, force-method query, pre-contact Commit, post-contact Commit stages with Beam/FrameLayer energies, normal/tangent contact energies, actual kinetic energy, plastic dissipation and separate detachment inventory. Ideal tension cable T*L is only a virtual actuator potential; endpoint work -T_begin DeltaL is logged separately.

Pressure parameter work, Rayleigh stiffness dissipation and global closure remain null, NOT zero. FrameLayer may commit before contact pre-commit. Recorder/init force queries are distinguishable calls but are NOT guaranteed Solver stages. No direct Solver transaction hook exists yet. Thus this is a synchronized CONTACT-owner journal, not an all-owner global journal. Unexplained residual is never defined to be numerical heat. See energy_audit.json when actually generated; missing outputs mean NOT RUN, not PASS.'''),
      '07_6DOF_GRASP':('NOT RUN qualified12-wrench campaign; BLOCKED approval','Actual +Tz research runs exist with the new component, but history/space/necessary-energy gates do not approve full12-direction grasp. No new12-direction campaign or force-closure certificate is asserted. Existing guided finger constraints and root radius~95.15mm remain explicit; the object is free6DOF. Rank6 alone would not establish unilateral/friction-limited closure.'),
      '08_OBJECT_SHAPES':('NOT RUN full shape grasp','Sphere/Cylinder/Box smooth birth kernels were tested, but actual full Cylinder/Box grasp/release with nonsmooth corner/endcap events is NOT RUN. Sphere outputs are not reused as other-shape evidence.'),
      '09_JAMMING_CAPACITY':('BLOCKED','No support-force/torque limit is approved while history/space errors remain. Pressure in the research scene is assumed, not a PET/vacuum measurement. Wire-only holding can physically succeed; OFF is not required to fail.'),
      '10_STRUCTURAL_OPTIMIZATION':('PASS candidate3 structure scope; FAIL candidate23; not grasp',r'''New separate true Optuna study:24 COMPLETE,0failed/pruned,3smoke trials then SQLite reload. Independent100-mm LINEAR FEM objectives are stiffness ratio and maximum across the ENTIRE piecewise-affine interface, refined21/41/81/161 until adjacent tip/slip errors<1%. It does not measure only connectors. Old Studies remain untouched. Separate workflow contracts exercise intentional FAIL/PRUNED with no objective values, seed and SQLite integrity.

Two Pareto candidates were independently run in actual conservative-Beam SOFA: repeat,dt-half,21→41 mesh, physical connector positions held fixed. Candidate3 k=33.20849634084168 at positions10,20,30,40,50,70,80,90mm passes tested structure gates, measured ratio1.6748830397189032. Candidate23 k=17.015359842717366 fails mesh maximum-slip change2.546736848039144%, so is NOT approved. See structure_candidate_decisions.json and all actual raw configurations. This is neither grasp optimization nor a global fabrication optimum.'''),
      '11_GRASP_OPTIMIZATION':('BLOCKED;0new grasp trials','No100-mm GRASP Optuna study is launched.24 independent structure trials and earlier30-mm trials are not counted as grasp trials. Required history/space/time/energy/grasp approval gates remain enforced.'),
      '12_NATIVE_MEMORY':('NOT RUN new Native campaign; EXPERIMENTAL bounded process memory','Existing Native contact is preserved as a different constraint law; no new Native force-equivalence claim. Actual new children have bounded4GiB/default480s; profile-justified single900s exceptions are recorded, not global defaults. Resource samples use same-parent verified child PIDs and include RSS/PSS/Private_Dirty/FD when available. Completed144000-step quarterdt is reported only if its raw metrics exist. No240000-step sustained-contact or hours-long leak-free claim; LSan is BLOCKED by ptrace, independent mathematical ASan/UBSan PASS is not engine-wide sanitizer coverage.'),
      '13_VISUALIZATION':('EXPERIMENTAL prepared replay; NOT RUN GUI','Headless is default. birth_replay.py prepared2401 measured actual state frames and a SOFA GUI command/environment under canonical_v8/replay. Existing closure_replay scene is reused; contact markers denote normal quadrature only. No synthetic animation or new UI is used as physical evidence. Neither a new GUI execution nor headless replay execution is claimed.'),
      '14_FULL_VALIDATION':('Mixed PASS/FAIL/BLOCKED; NOT full system certification','Clean new plugin build/unit/API/independent math and intentional source/binary/generated/physical-input mismatch guards are separate from full model convergence. Fresh original FREE golden checks run twice across600 frames at1e-10+1e-6|golden|. A direct Python invocation without the documented verification namespace FAILED (existing output directories and absent default build manifest); its log remains canonical_v8/python_final. Re-execution using the existing isolated validation launcher passed84 Python tests plus3 existing C++ executables; after the physical-input guard was added the final suite passed85 tests, logs canonical_v8/validation_unit_birth_guards_final. No failing test was deleted or relaxed. Old45gate is NOT summed with new birth tests. Existing Beam implementation and old models/golden/raw/Studies are unchanged. See final evidence manifest for exact hashes and individual logs.')}
    for suffix,(status,body) in chapters.items():
        if suffix=='12_NATIVE_MEMORY':
            mem=read(OUT/'memory_observations.json');quarter=mem.get('results/birth_20261115/canonical_v8/grasp/dt_quarter',{})
            body+='\n\nActual canonical quarter-dt memory observation:\n\n```json\n'+json.dumps(quarter,indent=2)+'\n```\nPSS depends on concurrent processes sharing engine pages; its range alone is not live-heap growth. A finite tail slope spanning contact/release is not a sustained-contact plateau certificate.'
        if suffix=='06_COUPLED_ENERGY':
            body+='\n\nActual24s contact-owner journal:194401rows,48000pre/post transactions, all known fields finite; contact normal+tangent split discrepancy<=1.23e-20. Journal ON/OFF state SHA256 both `330807bfd9237f66866620f400b55470dbf662421e6a5c0aa1e88a0bd00d1bc3`. Unknown columns remain null.'
        if suffix=='14_FULL_VALIDATION':body+='\n\nPost-physics plotting import initially failed because of a missing space in a Python conditional. analysis_restart.json records the incident; analysis_final contains the corrected actual execution logs. No physics case was rerun or its raw results changed to hide that orchestration failure.'
        (ROOT/'reports'/('BIRTH_'+suffix+'.md')).write_text('# Birth validation '+suffix.replace('_',' ')+'\n\nStatus: '+status+'\n\n'+header+body+'\n')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    final=f'''# Contact birth and energy — measured development report

Baseline `651a02ed24a11a9fce00fe3b437f188ded27266e`; branch `development/regrip-contact-birth-energy-validation`.
Publication-parent commit `{head}`; the documentation commit is obtained with `git log -1` (no self-referential hash). No push performed.

{header}
## Outcome

Independent birth/IFT/Jacobian and actual SOFA API integration PASS in tested scopes. Missing post-birth extension is restored. Exact-grid degeneracy and rigid-frame-dependent cell counts are handled without denominator regularization. Existing kernels/golden/Studies are preserved. Full history/space/time/energy approval is NOT inferred from kernel tests.

{convergence}

Full coupled energy, qualified12-wrench grasp and100-mm grasp Optuna remain BLOCKED. Native/other-shape full grasp and GUI are NOT RUN in this campaign. See BIRTH01..14 for measured scopes and limitations. Earlier failed prototypes and v7 diagnostics are retained, not replaced by v8 results.

## Independent optimization

New24-COMPLETE independent linear-structure Optuna study has two Pareto candidates. Actual SOFA approves only candidate3 in its tested structural scope (ratio1.6748830397189032); candidate23 FAILS mesh maximum slip. This is not actual grasp optimization or hardware performance.

## Reproduction

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/birth_assess.py
$PY -m unittest discover -s tests -p 'test_*.py'
$PY tools/birth_verify.py --raw
```

New experiments require NEW OUT/build paths; see NEXT_TASKS. Per-case command/config/identity/stdout/stderr/state/metrics/resource samples are under campaign/grasp. Compiled source/binary/generated hashes are in build_manifest and this manifest. Reports distinguish actual SOFA, independent FEM, independent math and assumptions; there are no new material measurements.
'''
    (ROOT/'reports/BIRTH_ENERGY_FINAL_REPORT.md').write_text(final)
    (ROOT/'reports/BIRTH_ENERGY_CURRENT_STATUS.md').write_text(final+'\nDetailed next steps: BIRTH_ENERGY_NEXT_TASKS.md.\n')
    entries={}
    # Include all completed raw files, never partial running case output.
    for folder in (legacy,BUILD):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and 'CMakeFiles' not in p.parts and p.suffix not in ('.o','.pyc'):
                if any(parent.name=='grasp' and not(p.parents[i-1]/'metrics.json').exists() for i,parent in enumerate(p.parents) if i>0):continue
                entries[str(p.relative_to(ROOT))]=dict(sha256=sha(p),bytes=p.stat().st_size)
    report_files=list(evidence.glob('*'))+list((ROOT/'reports').glob('BIRTH_*.md'))
    source_files=list((ROOT/'tools').glob('birth_*.py'))+list((ROOT/'tests').glob('test_birth*'))+list((ROOT/'models/structural_interface').glob('*.py'))
    for name in ident['birth_build']['source_sha256']:source_files.append(ROOT/name)
    for p in sorted(report_files+source_files):
        if p.is_file():entries[str(p.relative_to(ROOT))]=dict(sha256=sha(p),bytes=p.stat().st_size)
    write_json(ROOT/'reports/BIRTH_ENERGY_EVIDENCE_MANIFEST.json',dict(baseline='651a02ed24a11a9fce00fe3b437f188ded27266e',publication_parent=head,identity=ident,files=entries,scope='new campaign only; historical manifests unchanged; NOT full grasp certificate'))
    print('published',len(entries),'hashed evidence files')

if __name__=='__main__':main()
