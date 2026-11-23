# B3 grasp-first continuation1059–1072 — 2026-11-23

Starting HEAD4a9c65d,clean branch. Latest300-part CAD preserved and NOT used as
the Native model. Functional exploration is explicitly separate from physical
qualification. Existing time0.1%/mesh1% FAIL and old50g functional results unchanged.

## Frozen baseline and100g actual Native run

Baseline485:50g,R30,gravity9.81,assumed friction0.3,B3 distal40deg,1.5N/cable.
Old actual489/490:slip0.0323588mm,max speed0.272144mm/s,SkinZ0.490513315N,
Guide/Rail/Support0N. No unnecessary50g rerun. Baseline375/485/controller332
and alarm observer binaries retained;1059 preflight records exact SHA and SDK.
1060 normalizes only output paths and confirms the physical Scene differs ONLY
in object mass0.05→0.1kg;normalized inertia unchanged,physical inertia scales.
Initial saved geometry PASS is reused because geometry is identical,not new CAD.
Source Controller directory was copied from baseline for existing analysers;
runtime plugins come from frozen Scene,not rebuilt current working-tree source.

Actual command:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/run_b3_mass_exploration.py --tag b3_mass100_explore1059`

800steps,dt2.5ms,to2s,4GiB/480s guard. Estimate88.88s from485;actual140.446s.
Exit0,no SOFA ERROR,800outputs per finger/object. This is execution completeness,
NOT constraint convergence. Hold protocol unchanged except mass;predeclared1.6–2s,
slip≤2mm,speed≤5mm/s,supportgap≥5mm,supportforce≤1e-5N.

1062 functional Holding FAIL:slip40.021865mm,max speed0.052629mm/s,
supportgap0.1999999999mm,peak support1.055792651N. Object lands on the withdrawn
support,so its low speed does NOT imply unsupported Holding.
1063 actual Contact-pair→Constraint→row partition residual8.67e-19Ns/Nms:
Skin meanZ−0.073929375N,Support+1.054929281N,weight0.981N;
Guide/Rail0N.1067 Skin normalZ−0.283884719N,tangentZ+0.209955344N.
No invented missing forces,contact area or pressure. Momentum residual1062
~2.60e-18Ns is a local inventory,not full energy/time certification.

1064:264outputs hit Native iteration limit,including ALL161 hold outputs;
first at0.280s,max reported solver error4.21119e-6,hold2.21099e-6.
Thus failed load support cannot be uniquely assigned to material,friction,
curvature or cable transmission. No force/friction/tolerance increase adopted.
1070 saved tetra minimum ratios0.98229/0.98337/0.98333,no inversion observed;
not mesh independence.1069 accepted Skin geometry check FAIL:active gap
0.201024692mm at1.190s exceeds0.2mm contact buffer;retain this discrepancy.
1065 proximity arcs/curvature are geometric metrics,not Wrapping/area PASS.

1071 legacy Barycentric cable analyser BLOCKED:missing coupon-only
cable_audit.csv. No fictional journal supplied.1072 replacement reads actual
mapped guide paths and fixed PullPoint:hold shortening1.742–2.161mm across
six cables;max internal-vs-accepted difference0.103132mm. Force-controlled
1.5N input is not a prescribed shortening target. Actual force journal Tdt/dt
remains1.5N during Hold. Mechanical work/pressure remain NULL.

## Actual Native Root fixture and failed-clock repair

1061 removes object/support and uses original free-subset Root indices;
Native LinearMovementProjectiveConstraint replaces FixedProjectiveConstraint.
Only Root is prescribed,not full Film or object.4steps/10ms;nominal0.1mm motion.
Unshifted Native begin-clock schedule appears25μm late at end outputs.
1066 shifts keyTimes−dt but last output leaves the last key interval and Root
deviates18.55μm;STRICT1e-12 position check FAIL,retained.
1068 adds explicit terminal hold key,not position postprocessing:
maximum Root API error4.06576e-19m,12records across three fingers;position-only
STRICT check PASS. Runtime0.406s. This does NOT certify Root velocity/work,
PullPoint synchronization,cable geometry during motion or loaded Lift.

Reproduction:
`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_root_fixture_probe.py --tag UNIQUE --end-clock --terminal-hold`

Lift remains BLOCKED pending actual PullPoint API observer and consistent
moving-root/cable-origin contract. No object state was directly moved.
Variable stiffness NOT IMPLEMENTED in this Scene:single bonded Skin/Rail FEM,
no pressure,layer friction or vacuum state. Modulus sensitivity is not jamming.

## Next performance experiments

1. Instrument actual PullPoint and Root velocity in the small Native fixture;
   validate both against the SAME accepted clock,then a loaded exploratory Lift.
2. Isolate first iteration-limit interval near0.280s using actual contact/cable
   row data and frozen50g comparison before any new full-grasp parameter sweep.
3. Only after numerical interpretability:single-variable distal contact-geometry
   candidate that keeps lower-hemisphere Skin contact during support withdrawal.
   Do not treat increasing force/friction as a demonstrated structural fix.
4. Recovery and variable-stiffness tests need independently defined reference
   equilibrium and actual layer/pressure/material assumptions respectively.

All generated cases are separate directories. No SDK edit,push,history rewrite,
new CAD refinement or fabrication claim. All launched children completed.

## Continued diagnosis1073–1074

Read-only1073 applies the SAME solver-limit audit to original50g485 outputs:
11limited outputs over3s,zero in161hold outputs;hold max error1.94971e-8.
100g has264limited outputs over2s and161/161hold limited,hold error2.21099e-6.
This is a load-sensitive coupling symptom,not a proof of a unique solver cause
or measured hardware capacity. Frozen50g execution was NOT rerun.

1074 independently reads all12Root velocity records from actual1068:
ramp-interior0.01m/s,terminal right-side hold0m/s,maximum error0.
Root position+velocity API are now narrowly checked;PullPoint API,moving cable
length,fixture work,acceleration kink and loaded Lift remain unqualified.
All Native probes use the frozen485 plugins whose SHA identities are in1059
preflight and the immutable baseline Scene;no new compiled physics model.
