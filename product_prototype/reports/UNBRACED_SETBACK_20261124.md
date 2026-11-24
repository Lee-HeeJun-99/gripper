# Unbraced Holding continuation — 2026-11-24

Start HEAD6930d85, clean branch development/regrip-autonomous-research.
No remote operations, SDK edits or original Raw/verdict changes.

##1681–1682: actual finite-model internal load

Frozen NativePairRows added read-only to original1586. Actual800steps168.061s;
all saved object/finger/Guide q/v and object impulse differences **exactly0**.
Not a repeated design test or new functional PASS: purpose was previously
unavailable per-body finite-hardware J transpose lambda.
15414 paired body contributions from7707nonzero constraint rows; maximum pair
linear impulse imbalance2.711e-20Ns. During161Hold outputs mean internal forces:
finger0(+.066718,+.000327,-.003293)N;
finger1(-.033172,+.056962,+.001497)N;
finger2(-.033546,-.057289,+.001796)N.
Net across fingers cancels, but approximately.067N outward support on each
finger is real internal bracing. Body contact moments peak.216–.222mNm.
This does not prove the object would fall without bracing; no causal claim.
Pair-origin angular impulse sum up to7.948e-8Nms is recorded, not hidden or
promoted to whole-system moment/energy closure.

##1683: new physical candidate, not a chamfer scan

All six terminal rings translate proximally by their existing2mm length.
OD3/ID1.2/L2mm, ring volume and collision features remain. Native cable points
translate with rings; finite support hulls rebuild from original three feet.
Support volume changes29.25–30.46 to29.42–30.75mm3; inherited mass/inertia are
NOT recalibrated or physical qualification. Attachment strength NOT MEASURED.
New STL in metres and candidate Scene saved separately; original unchanged.

OLD1586 motion replay checks422400inter-finger changed-hardware pair frames:
all AABBs separated beyond existing.2mm contact buffer,0narrow candidates.
Replayed finite-radius wire/Object gap>=4.16779mm. First saved object/hardware
surface gap1.97748mm is not a continuous initial/swept test. Replayed clearance
is not changed dynamics or Holding. Same-finger/skin/support joints, real
finite-wire bending/sliding and manufacture remain unqualified.

Actual next task1684 .6s Native pilot RUNNING; inspect completion before rerun.
No full2s until fresh positive-FEM/source-contact/runtime gates. This tests
ideal NativeCableConstraint mechanical exploration only, not a fix for1675
finite-wire surface crossing or1678normal refresh. Those failures remain.

Reproduce only with UNIQUE tags (existing1681–1684 must not be overwritten):

```bash
$PY product_prototype/sofa/unbraced_wrench_observer.py --tag UNIQUE
$PY product_prototype/sofa/unbraced_wrench_assess.py --case unbraced_wrench1681 --tag UNIQUE
$PY product_prototype/sofa/terminal_setback_replay.py --tag UNIQUE
$PY product_prototype/sofa/terminal_setback_native.py --tag UNIQUE
```

All producers freeze sources/inputs/scenes/SDK and binaries where executed.
Raw CSV stays local with SHA256; new >=50MB files excluded from Git, all CSV
optionally excluded through explicit research_git_guard --summary-only.
