# Deformed wire and drive continuation744 onward

Baseline HEAD748915f,clean worktree on receipt. Read AGENTS/CHECKPOINT/NEXT;
no earlier successful or failed Native physics campaigns repeated.
No SDK changes,new custom solver,remote push,purchase or physical measurements.

## Cycle744–747 — finite reference hardware on old actual motion

Implemented `cad/deformed_wire_screen.py`:maps NEW V21finiteEyelets/Supports
through OLD485accepted Rigid3 transforms including body-to-part offsets.
Uses original object state at the SAME saved time;fixed pullpoint is explicitly
guarded against moving fixtures.2mm-radius filleted wire,0.5mm diameter.

- 744:4selected times(0.4725,1.6,2.0,2.355s),6wires each,24samples.
  No hardware intersection candidates;minimum wire/sphere lowerbound3.864451mm.
  Skin/Rails excluded in this first scope;27.922s actual runtime.
- 745 added actual deformable Skin/Rail nodal surfaces and reference ordering
  guard. **REJECT as qualified evidence**:canonical source was changed during
  execution;end-copy producer may differ from loaded code. Outputs retained and
  SOURCE_IDENTITY_REJECTION.json records the defect,NOT hidden or madePASS.
- 747 repairs provenance with `deformed_wire_run.py`:snapshot worker BEFORE
  execution,4GiB/480s bounded child,dependency before/after hashes.
  Actual worker hash matches summary producer hash;dependencies unchanged.
  Includes actual Skin/Rail boundaries:24closed-positive surface checks;
  24wire samples,0intersections,minimum sphere lowerbound3.864451mm;29.003s.
  Closed surfaces do NOT certify FEM no inversion or absence of self-intersection.
- 746*object-only* scans ALL1200saved times,6wires=7200samples.0invalidfillets,
  0nonpositive gap lowerbounds. Minimum3.85815941275mm at0.4775s(f0/c0).
  Actual runtime22.081s. Hardware NOT checked in this all-frame mode.
  Saved-time screening is NOT continuous CCD or actual candidate dynamics.

## Cycle748–752 — conditional drivetrain geometry

748compares finite direct lead-in with deliberate perimeter route atx70mm.
No random guide/stroke changes. Same V21parent160parts andwire0.5mm.
- Direct route:18obstacle intersection hits;FAIL as proposed directconnection.
- Perimeter route:0obstacle intersection hits.12intended generic-drum tangency
  candidates retained separately,NOT filtered as nonexistent collisions.
- Proposed groove heights56.75/59.25mm from actual generic drum geometry.
  Motor output axis/horn still UNVERIFIED;no supplier-fit/driveapproval.
- Turning radius2mm is a hypothesis. Perimeter increases product envelope.
  New pulleys/supports/extra friction were NOT in this initial route test.

751implements18actual finite turn-pulley modules at fillet centres andaxes.
Wire pitchD4,OD6,bore1.2,groovewidth0.8,overallwidth1.8mm.
18ASCIISTL actual readbacks:closed positive singlebody;0intersections against
160parentparts;2.773s. NOT mounted assembly:shafts,bearings,brackets/root
redirect,tolerances,strength,friction andphysicalmaterial stillmissing.
CAD:meshes/b3_lead_pulley_modules_v22;neutralrecipe andBOM included.
No STEP or fabrication-ready claim. Do not silently adopt in B3 dynamics.

750visualization uses actual OLDaccepted Skin with NEW hypothetical wire
overlay,explicitly labelled as such. X-Z projection is NOT contact proof.
Full saved-frame sphere-gap curve is NOT time-convergence/CCD qualification.
749/752design regressions only;not productGate or newHolding result.

## Next bounded investigation

753extends four-time wire screen to all distinct worst-times from742 andthe
746object-worsttime;also compares inter-finger finite hardware directly.
Expected cost from747~7.25s/frame,roughly160s for22frames;4GiB/480s guard.
Its final outcome must be read before choosing design changes;do not inferPASS
from this pending-run description. Any new collision is a frozen-path rejection,
not proof that a newly simulated mechanism would follow the same trajectory.

**Final753:**22saved times,132wire samples,0wire obstacle intersections,
0inter-finger finiteEyelet/Support intersections. Actual guardedruntime146.996s;
source/worker/dependency identity verified. NOT continuous CCD or new dynamics.

754continued with18finite fork modules+18pin proxies. Fork back faces away
from actual wire arc;pinD1/forkbore1.2,nominal axialwheel gap0.5mm eachside.
36ASCIISTLsreadbackclosed/positive;0parent/module solid intersections and
0wire-envelope/fork/pin intersections;9.847s. No collisions disabled.
STLs+neutralrecipe:meshes/b3_pulley_fork_modules_v23. No Palm mountingbridge,
pin retention,bearing orload-bearing material selected. NOT a mounted drive.
756actual finite-mesh orthographic SVG/PNG views generated andvisually reviewed,
nominal dimensions labelled;NOT production-tolerance/STEP drawing release.

757conditional elementary load budget,NOT actual measured stress:
at1.5N/two equal branches/90deg turn ->2.12132N wheel load;
ideal fork-arm stress10.6066MPa,pin bending15.1253MPa (assumed3x1mm arms,
5mmcantilever,simplysupported2.8mm pinspan).SF2 doubles these demands.
Materialallowable,fatigue,friction,termination,continuousmotor duty remainNULL.
These assumptions expose required material/joint tests,not justify approval.
758design regression includes analytic segment/sphere,force-budget references,
finite module readback,source identity,all-frame andeventworst scope guards.

Next priority:design actual Palm-to-fork mounting bridges andaxle retention;
verify full finite routes (including root inlet redirect),tolerances andtool
access. Use known conditional loads but do not pick material from unmeasured
strength. Then run separate Native candidate coupon with physically defined
mass/inertia/joints;do not assume new drive == old sixprescribedforces.

Motor/material approvals remainBLOCKED by actual continuous loaded duty,
interface drawings,wirebend/termination/bondfatigue data. Native contact/time
0.1% andFEMmesh failures unchanged.100g/Lift/recovery qualification not advanced.

## Commands (NEW tags only)

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/cad/deformed_wire_run.py --tag UNIQUE_SCREEN --candidate b3_manufacturing_bore_v21 --include-film --all-event-worst --hardware-pairs
ulimit -v 4194304
timeout 480 $PY product_prototype/cad/motor_lead_in.py --tag UNIQUE_LEAD --candidate b3_manufacturing_bore_v21
timeout 480 $PY product_prototype/cad/lead_pulley_candidate.py --tag UNIQUE_PULLEY --name UNIQUE_MODULE --candidate b3_manufacturing_bore_v21
$PY product_prototype/cad/manufacturing_test_run.py --tag UNIQUE_TEST
```

Raw:results/product_deformed_frozen747{,_analysis},product_wire_object_all746,
product_motor_lead748,product_pulley751,product_event_hardware753{,_analysis}.
Worker snapshots,commands,config/input/source hashes retained;unmeasured material,
mass,strength,bend limits andmotorcontinuousratings areNULL/NOTMEASURED.
