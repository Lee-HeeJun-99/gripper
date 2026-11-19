# Native Skin contact continuation — trials147–178

Start ddb452a; functional source fbc9754 plus final instrumentation commit in Git log.
Branch unchanged. No SDK/legacy solver edits, force law or custom ODE solver added.
All inputs remain research assumptions: E250MPa,nu.3,1g FEM/finger,
10mg/guide frame,mu.3,R30mm,50g,gravity9.81,8mm stroke.
Guide OD3mm/L2mm enclosing sphere and wire radius.25mm retained.

## Cable transition, actual native outputs

150/152 instruments existing physical input without altering native forces.
First nonzero finger-related impulse and maximum cable error coincide at1.07s.
Command8mm,actual7.785112mm,error−.214887867mm. Assembled child Jacobian
matches previous accepted geometry to1.25e-16; current gradient differs by.047115
at the worst sample. Native solver reported error3.33e-9,31 iterations.
Internal CableModel length.090408561m differs from accepted geometric.090559253m.
Largest observed incremental length-linearization remainder49.865um.
This distinguishes lagged/nonlinear geometric residual from linear solver error;
it does NOT establish that cable linearization is the only coupled-contact error.
The audit selects the cable row by previous-gradient match,not persistent row ID.
Native internal constraint violation remains NULL; no output correction was applied.

## One-factor mechanisms and rejection

-149:normal offset+3→−3mm only,still outboard14. All800 steps/2s complete,
 30.98s wall time. No finger impulse,object follows support down40mm;
 support carries.4905N. Holding FAIL. Steady cable tracking is excellent but
 useful inward wrapping is absent. Do not raise tension to hide this result.
-151:split exposed surface into252 Skin faces(all reference z>=0) and248 Rail
 faces(any z<0),using native SubsetMapping and actual original exterior faces.
 Same backside design gives identical no-contact failure.
-155:outboard14→4mm,normal+3mm restored; other physical inputs held fixed.
 This is compared with the original-positive-offset design,not claimed as a
 one-factor comparison with149. Hardware collision proxies are NOT disabled.
 Split boundary edges/points can change native detection; this is a separate
 contact-model experiment,not a passive-observer-only modification.

## Apparent Skin load is NOT qualified Skin holding

Prelaunch config declares minimum Skin vertical fraction.8 of gravity load.
159 reports row-load minimum.9989127,mean.99998785;Guide/Rail/Support contribution0.
161 correctly associates child collision rows with fingers:low speed1.5994mm/s,
 support gap56.70mm,support force0,translation drift.03616mm in1.6–2s.
160's earlier analysis incorrectly classified rows with an empty parent Jacobian
as support; it is preserved.161 fixes that analysis using explicit child masks.

**These functional/row criteria are not physical Skin-contact certification.**
166 adds actual child position journals;168 finds child/FEM subset error0,
but whole Skin nearest gap remains>=3.3937mm and is5.0324mm at an active-impulse
sample. Declared contact distance is.2mm. Consequently overall Skin holding FAIL/
NOT QUALIFIED. Detector provenance,geometry or linearized response remains unresolved.
Child Jacobian influence is insufficient to certify direct collision origin.
169 therefore uses ROW_LOAD_CRITERION_MET_CONTACT_NOT_QUALIFIED instead of an
unqualified PASS.159's limited row-only result is retained,not silently rewritten.
Wire sampled clearance is positive(~.518mm),but moving support-arm/wire swept
collision,pressure and contact area remain NOT MEASURED/unqualified.
165 actual-state PNG is not a qualified wrapping image;its legacy support timing
subanalysis assumes a linear command,so127/161 declared-command checks supersede
that subanalysis for smooth/end-clock scenes. Its included old010–012 time result
is historical,not the time qualification of155.

## Time convergence and mapping controls

162/163 complete1600/3200 steps through2s under4GiB/480s caps.
167 verifies same binary,canonical physics and declared command;all common times,
all pairs,no floors,unchanged.1% gate:FAIL. Worst velocity difference.107293m/s,
relative199.86%;object-motion worst-by-relative sample differs.1401mm.
No100g orLift run:antecedent physical gates failed.
171 compares155/166 query-only logging;172 compares split/unsplit model164.
See their immutable summary JSON for exact STRICT1e-12 comparisons. Split contact
must not inherit unsplit model accuracy. Stage work/full energy remain NULL.

## Minimal native bridge API

158 isolates one Rigid3 MechanicalObject,DiagonalMass,RigidMapping and gravity,
four steps. TemplateRigid3d is rejected by this factory (availableRigid3d,Rigid3d);
fallback then reports associated-state/topology errors. Exit0 is NOT PASS.
This narrower failure does not prove SOFA cannot support native rigid diagonal
mass. Full bridge and SubsetMultiMapping/inertia verification remain BLOCKED.
No SDK patch,anisotropic-to-isotropic substitution or guard bypass was used.

## Reproduction and next implementation

Raw,scene,prelaunch config,source snapshots,SDK runner/binary SHA and commands:
`product_prototype/results/<trial>/`; process stdout/stderr/command.json/summary.json.
147/148 are pre-physics build-reuse guard failures,not physical runs. Runner now
resolves a reused trial's recorded actual build directory and retains SHA checks.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/sofa/contact_transition.py --case skin_baseline_audit_150 --tag UNIQUE_TRANSITION
$PY product_prototype/sofa/skin_geometry_audit.py --case skin_mapping_probe_166 --tag UNIQUE_GEOMETRY
$PY product_prototype/sofa/native_time_assess.py --tag UNIQUE_TIME --cases skin_inboard_trial_155 skin_inboard_half_162 skin_inboard_quarter_163
```

Do not repeat completed physics merely to produce another campaign. Next source
work:opt-in read-only logger using installed public NarrowPhaseDetection::
getDetectionOutputs and Contact::getCollisionModels. Record actual pair paths,
detector contact points versus same-time accepted Skin/Object positions,then bind
response rows to that provenance. Test query purity before a short onset trial.
Only after collision geometry is consistent revisit Skin holding and100g/Lift.
No candidate is selected for final CAD. Existingv5 sources/BOM/STEP-unavailable
status preserved;new unsuccessful paths are not published as fabrication-ready.
No automatic post-session execution or OS resource exhaustion is claimed.

## Follow-through:actual detector provenance173–178

The next logger above was actually implemented using public NarrowPhaseDetection::
getDetectionOutputs,CollisionModel paths and generic detector point getters.
173 completed160 steps through.4s:compiled3.47s,physics5.92s,zero SOFA errors.
174 matches prior accepted q/v exactly over160 steps.175 then completed800 steps
through2s;178 verifies full2s query purity (see actual comparison result).
176 finds1896 Guide–Object detector samples,129 Support–Object samples,
and ZERO Skin–Object/Rail–Object samples. Hold1.6–2s contains483 Guide samples
and no support/Skin samples. Counts are not area,pressure or force.
Thus the apparent Skin influence is NOT direct Skin collision:177 correctly
rejects it as FAIL_SKIN_PROVENANCE even though the row-load numerical criterion
is met. This resolves the geometry/Jacobian-source discrepancy without claiming
the new route has achieved Skin holding. Detector outputs are earlier-stage
native data labelled by observation end clock,not continuous impact time.

Next:bind response Constraint row IDs to actual Contact pairs,then revise
guide placement/support geometry with measured full-path interference. A backside
offset alone failed and an outboard reduction still contacts hardware. Do not
disable Guide collision or promote these unsuccessful paths into final CAD.
Full time167 FAIL and new Skin-provenance FAIL block100g/Lift.

```bash
$PY product_prototype/sofa/detector_pair_assess.py --case skin_detector_hold_175 --tag UNIQUE_DETECTOR_AUDIT
$PY product_prototype/sofa/scene_pair_audit.py --cases skin_inboard_trial_155 skin_detector_hold_175 --tag UNIQUE_QUERY_AUDIT
```

Reference build:product_prototype/cad/build_skin_detector_probe_173/;
libReGripProductSequence.so SHA4912e92513eb66f2eef8b426263c418f06da155e428265b6fc62922dd26c263e.
Source commit0ec92f0 plus final passive-journal snapshots in173/175.
Latest evidence/launch archival implementation572796d. Earlier trials preserve the
actual runSofa command in process/command.json and full effective scene/config;
Python launcher argv archiving is added prospectively,not fabricated retroactively.
171/178 full2s query-purity differences0.172 split-vs-unsplit object position
component difference.0135066m,so split detection cannot be treated as equivalent.
