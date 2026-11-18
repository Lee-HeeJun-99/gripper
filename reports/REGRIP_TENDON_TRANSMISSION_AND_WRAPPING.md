# ReGrip tendon transmission and wrapping research —2026-11-18

## Current outcome and scope

Actual source starts atf70a46f. V12 integrity PASS19717 files;no preexisting
physics process. Separate single-film SOFA coupon isolates actuation from
object impact,using the SAME current material/geometry/root map/public nodal
mass/control. It is NOT a free-object/three-finger wrapping experiment.
Previous3-film38ms endpoint and all historical FAILs remain intact.

##1. Tendon→Rail→Attachment→Skin

Original Assembly.elements generates physical eccentric path forces from
T*dL/dq (five guides/rail). Coupling is ten objective point attachments,
not a rigid whole-surface tie or calibrated layer jamming.
At rest linearization,M*d2dq+C*ddq+K*dq=B*dT,withC=2M andB=-grad(L).
B_skin=0 does not imply no eventual control. For a step load and zero initial
perturbation,rail displacement starts atO(t²);throughK_skin,rail the skin
displacement starts atO(t⁴). For the actual C2 ramp beginning asO(t³),these
onsets change. Existing1136/1138 contact-reaction/three-mass tests remain
limited local analyses,not nonlinear transfer-time or actuator predictions.

##2. Actual nonlinear versus independent linear response

1141/1143 short actual API profile PASS;1144/1145/1146 same20ms endpoint,
100/50/25us,all q/v/time EXACT against nonlinear free-block reference.
Actual ForceField endpoint tension matches the common compiled C2 profile.
1139 FAIL was exact recomputed-vs-public nodal mass mismatch;use the archived
1002 mass on BOTH paths,not a relaxed identity test.1140 wrongly sought that
older mass entry in V12;correct immutable identity lives in V10.

1148 independent mass-scaled649-mode linearized midpoint model at rest:
nonlinear20ms displacement L2 difference7.8374266%,velocity12.4932183%.
This is MODEL linearization error,not proof of a Solver defect.
Minimum frozen omega1.1861257rad/s is not a dominant forced response or
nonlinear recovery time. The linear static skin tip prediction-41.5368mm
has large rotation and is not a validated nonlinear static equilibrium.

##3. Actual shape at20ms,baseline1144

|Quantity|Actual nonlinear result|
|---|---:|
|Skin width-mean tip z|-0.167328030mm|
|Skin centre tip z|-0.022899499mm|
|Skin width-mean midspan z|-0.000147723mm|
|Skin root-tip total tangent angle|0.02072185rad|
|Tip width z-warp|0.25434080mm|
|Left/right rail width-mean tip z|-0.28868749/-0.29114539mm|

The width-mean bend is not uniform skin conformation. Midspan motion is very
small and skin centre moves much less than edges. No object is present,so
continuous contact coverage,pressure andholding capacity areNULL/NOT RUN.
Curvature definitions:legacy signed xz tangent turning/chord-arc spacing;
additional3D total curvature uses atan2(norm(cross),dot)/mean chord length.
Centre and width-mean traces are separate. Analytic straight-line/discrete
circle metric checks pass in tests/test_transmission_shape.py.

##4. Force/work inventory,actual1152 observer

Read-only reconstruction at ALL200 actual accepted states;stored/kinetic
energy agrees with ForceField to4.07e-20Nmm. At20ms:attachment force norms
on Skin7.6080e-5N,on Rails5.9752e-5N;tendon force norm4.37328e-4N.
These are nodal-vector norms,NOT grasp resultants or holding capacities.
Attachment net-force residual2.40e-20N,net moment1.71e-19Nmm.
Stage-consistent midpoint tendon work1.00275627e-4Nmm,
damping work1.22364693e-6Nmm,signed energy defect1.02585e-10Nmm.
Root Work NULL;defect is not heat or full-energy certification.

##5. Time integration and computational cost

1153 midpoint100/50/25us ALL-pair endpoint Gate FAIL at0.1%:
max100→25 difference0.6291442%,50→25 difference0.1259985%.
Midspan displacement/curvature cannot be omitted as small absolute signals.
Separate Gauss order4 reuses EXACT constitutive force/Hessian and sameM,C,T.
1154/55 analytic errors1.4888e-7,9.3048e-9,5.8154e-10(~16x refinement),
nonlinear stage tangent FD8.38e-13.1156 short SOFA q/v/time/stages EXACT;
1157/58/59 actual20ms EXACT.1161 all-pair endpoint errors are0.00431148%,
0.00458128%,0.000269789% for200→100,200→50,100→50us:PASS0.1%.
This is ONLY the exact20ms free-coupon endpoint,not whole-trajectory,
contact,mesh or all-gripper time certification. Reference/actual runtimes
for1157/58/59 are31.83/36.73s,62.89/61.72s,114.99/135.56s respectively;
concurrent workloads differ,so no isolated speedup ratio is asserted.
Separate actual two-stage journal prevents applying midpoint work quadrature
to Gauss. No improvement in speed is claimed before wall-clock comparison.

##6. Structure candidates,one factor only

1150 changes onlyattachmentK:.001→.01N/mm,same material/volume/mass/route/T.
At20ms Skin mean tip-.170860635mm,centre-.030781645mm,width warp.248589499mm.
Some control reaches centre more efficiently,butthis does NOT certify wrapping
or stronger holding. Attachment stiffness is an assumed mechanism parameter,
not a fabricated material modulus or measured joint property.
1151 reverses guide offset+5→-5mm only;Skin mean tip changes sign to
+.166542595mm. The original sign drives towardnegative localz,where the
reference target sphere would lie;blindly reversing it does not improve wrap.
Comparison is fixedT/control/time/volume. Work is NOT constrained equal;work-
normalized observations must not be represented as matched-work trials.

##7. Nonlinear static attempts and alternatives

1147 fixed16 load stages and force-residual globalization fail atNewton60
before first accepted load. Small accepted steps~1/512..1/2048 suggest stiff
geometric strain/poor residual merit,not inability to bend under any load.
1149 physical constant-T potential Armijo reachesfirstload6.25e-6N,
force residual6.08e-13N,then fails nearsecondloadresidual1.11e-11N.
Potential differences approachroundoff;force Gate1e-12 stays unchanged.
1165 hybrid physical-potential/force-residual globalization PASS at16 loads,
maximum residual9.98265e-13N (unchanged1e-12N gate),runtime46.99s.
AtT=.0001N/rail:Skin mean tip-43.05871mm,centre-43.00656mm,
midspan-11.38046mm,root-tip angle0.827697rad;rail angle~0.9184rad.
Combined cable length190.06874mm versus200mm at rest. Thus the same structure
CAN have a substantially bent no-object force equilibrium,whereas20ms is
far from that equilibrium. This is an independent nonlinear static result,
NOT actual SOFA dynamics,stability,object wrapping,contact clearance or grasp.
1147/1149 failures remain preserved;no physical stiffness/damping was changed.

1164/66/67 independent38→44.4ms64/128/256-step all-pair endpoint subset
PASS in1173,max0.02999976%. Separate actual Owner1174 then passes first
8step API1176 and4step resume1177:q/v/time EXACT,field error0,checkpoint
bytes identical.1178 seven remaining actual V5 plans reach44.4ms.
1182 ALL64 actual q/v/time match preserved same-plan reference1134 EXACT.
Reference1118 lacks the `plans` clock mode:1181 rejected before integration;
that failure is preserved,not conflated with a physical Solver failure.
Independent common-end clock and actual eight-plan accumulated clock are
different numerical plans;no1e-12 bridge waiver or actual cross-grid time
certification is claimed. Original38ms Owner cap is unchanged;the new class
has a separately admitted44.4ms cap. All paths reject reimpact,not mask it.

##7b. Actual pulse energy and physical control hypothesis

1169 actual no-object Gauss250step50ms cycle API/stages/time EXACT;
reference78.76s,actual90.03s. Skin mean tip-.38082105mm,centre-.57327854mm,
midspan-.10098897mm,root-tip angle.03102525rad. Still moving,not recovered.
1175 actual shape/static comparison distinguishes those two result types.
1179 integrates ACTUAL two Gauss force stages (not midpoint interpolation):
tendon work.00012119183184Nmm,damping.00000771352625Nmm,
remaining stored+kinetic.00011347832209Nmm,signed defect1.64990e-11Nmm.
Root Work NULL;not whole-gripper energy certification.
1185 conditional energy analysis:the pulse injects23.2744% ofthe.000520708899
Nmm stored energy of1165's static configuration. With T=0 after30ms and
passive damping,merely extending this unloaded trajectory cannot reach THAT
configuration under the stated model. This does NOT prove all possible
lower-energy contact-guided wrapping configurations impossible.
1180 overlays those no-object static shapes with the ORIGINAL fixed sphere
using all320 triangles/ClosestPrimitive:maximum-load buffered gap-29.6233mm.
This is geometric infeasibility of an unconstrained shape,NOT a contact
Solver failure,wrapping or pressure measurement. Contact must be solved.
Therefore a longer same-Tmax HOLD is a separate next control-design test,
not a higher tension,stiffness repair or deletion of the old pulse result.
1183 bondK10x static trial FAIL atNewton60 nearstage15 (force~1.0184e-12N);
the unchanged1e-12N equilibrium gate is not waived.

##8. Remaining contact/grasp/design boundaries

Existing1133 frictionless sphere normals have zero centre torque andwrench
rank3. No12-wrench holding certificate,measured friction or gravity lift.
Singlecoupon proves a transmission response exists,not full-surface wrapping.
The old3-finger geometry is rectangular with50mm roots,not tapered artwork;
thickness clearance,self-contact,mechanical equalizer/general friction and
all-gripper time/energy/mesh remain unqualified. Final design/Optuna BLOCKED.

##9. Reproduction and artifacts

Raw:results/autonomous_film_20261118_transmission_*1139..1168/ (each own
source snapshots,binaries,SDK/ldd,commands,exit status,actual CSV).
Actual Figure:results/autonomous_film_20261118_transmission_linear1148/actual_vs_linear.png.
Reusable baseline DLL:build/film_transmission_20261118_transmission_common_profile1143/libReGripFilmTransmission.so.
Reusable Gauss DLL:build/film_transmission_20261118_transmission_gauss_profile1156/libReGripFilmTransmission.so.
All children4GiB/480s;first8stepprofile before longer runs;max4 simultaneous.

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_transmission_run.py --tag UNIQUE --steps 200 --duration .02 --common --scheme gauss --reuse 20261118_transmission_gauss_profile1156
```

Run only with a NEW tag andmatching archived/current compiled source guard.
Existing runs need not be repeated.
The next research report update must replace pending status only after actual
completion. No automatic post-session continuation is provided.
