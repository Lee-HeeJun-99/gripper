# Actual cable-origin contract and Lift exploration — 2026-11-23

Starting clean HEADccb89c1. Historical50g functional Holding retained;100g1059
Holding FAIL/time/mesh FAIL retained.300-partCAD is a DIFFERENT model.

## Read-only actual PullPoint1075

Compiled small separate NativeCableOrigin public-data component against ONLY
installed SOFA26.06.00. Source,CMake,compile logs and actual binarySHA saved
in1075;no SDK edit,new ForceField,ODE or contact solver. Read-only mode never
writes any Data. It reads actual CableConstraint.pullPoint at AnimateEnd.
Added to moving-Root fixture1068 for4steps,all24origin outputs present.
All three Film q/v and mapped guide arrays match frozen1068 within1e-12.
Actual origins stay fixed while Root rises0.1mm:maximum discrepancy0.1mm.
This is direct API evidence,not inference from XML command values.

## Controlled cable origin1076

Reuse EXACT compiled1075 binary/source;enable explicit prescribed cable-origin
travel on the same accepted clock as Native free-subset Root motion.
Controller writes ONLY pullPoint at AnimateBegin;no q/v/force/impulse writes.
Actual24end outputs:maximum origin-vs-Root schedule error4.40457e-20m.
This is changed fixture boundary data,NOT observer purity or a dynamic Lift.
Frozen NativeCableSequence still sets tendon force;component order is validated
by actual end-state PullPoint readings,not assumed. Neither fixture qualifies
continuous path,time convergence,motor coupling or a physical actuator.

Reproduction (unique tags and immutable compiled identity guards):

`/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/run_cable_origin.py --tag UNIQUE_OBSERVER`

`... run_cable_origin.py --tag UNIQUE_DRIVE --reuse b3_origin_observer1075 --drive`

## Next actual performance trial1077

Independent50g free-object B3 Lift exploration launched from485. Native Root
free subsets and actual cable origins rise5mm over1.6–1.9s,with explicit terminal
hold. Object states never prescribed. Gravity9.81,friction assumption0.3,
force1.5N/cable,allcollisionhardware and original withdrawal fixture retained.
No source/CAD transplant;no claim that this represents final motor hardware.
Protocol saved BEFORE launch:minimum object rise4mm,relative downward slip≤2mm,
end speed≤5mm/s in1.95–2s,supportgap≥5mm,support force≤1e-5N,Skinweight fraction≥.8,
Guide/Railvertical load≤1e-5N,Root/origin APIerror≤1e-12.
480s/4GiB guard;estimated88.88s from actual485 baseline,not a runtime guarantee.
Result must be evaluated from completed actual journals;launch alone is NOT PASS.

## Completed actual Lift1077/1085

800steps/2s in101.108s,zero SOFA ERROR. Corrected1085 satisfies ALL preregistered
functional Lift tests:minimum end-rise4.980463mm,maximum relative downward slip
0.110716mm,end speed4.00943mm/s,actual Root rise5mm,Root/origin position errors
4.01e-18/4.34e-18m. End mean Skin support0.488022N vs gravity0.4905N;Guide/Rail/
Support load0. Direct response partition residual2.17e-19Ns/Nms. Actual force
command1.5N/cable retained. First1.6s Film/guide states match original485 exactly.
Saved guide-sphere minimum gap0.194739mm;no overlap at saved800states1082.
1083 saved tetra minimum ratios0.98149/0.98261/0.98218;no inversion observed.
These are NOT solid-support clearance,mesh or time-convergence qualification.
1080 still has9iteration-limit frames during early contact;hold0/161limited.

Analysis defect preserved:1079 assumed5mm support radius while actual Scene
has35mm. Append-only GEOMETRY_CORRECTION.json records the error;corrected1085
uses actual Scene radii. Real minimum gap41.61058mm,NOT71.61058mm;unchanged
5mm protocol still satisfied. Old summary/source/figure bytes retained.
Actual accepted-state plot:results/b3_lift50_corrected1085/actual_lift.png.

## Lift then Release1081/1089/1091

Independent fresh3s run,NOT an unvalidated checkpoint splice.1200steps completed
in130.501s;no SOFA ERROR. Native Root held5mm,force unloaded by original C2
control2–2.5s. First800Film/guide states1089 and object q/v/impulses1097 match
1077 EXACTLY. Corrected1091 evaluates the SAME preregistered1.6–2s Lift window
and passes functionality,not physics. Original1088 mistakenly included intentional
Release fall in Lift-slip metric and produced FAIL;preserved with explicit
WINDOW_CORRECTION.json. No threshold or physics output changed.

Actual last Skin impulse2.385s. After2.8s all object Skin/Guide/Rail/Support
resultants0;object falls2387.568mm after2s. Late velocity increments match
gravity within3.16e-16m/s. Tendon commands end at0N. This is observed Release,
not a claim of safe real-world dropping or repeated hardware operation.
1090:all1200saved guide-sphere gaps positive(min0.194739mm),not swept solids.
1097:maximum object momentum defect1.58e-17Ns,angular3.92e-21Nms;maximum Lift
rotation2.32216deg,lateral drift0.081924mm. Full Root/cable energy/work remain NULL.

## Recovery reference1092–1095

Final stress-free-translated tip difference~0.150984mm alone is not plastic
residual. Independent actual full three-Film/Guide gravity reference removes
object/support and sets ONLY tendon input0;original fixed Roots/material/mass
remain.100steps/.25s1092 took3.211s.1093 comparison FAILS preregistered stability:
reference node speed0.009226mm/s exceeds0.001mm/s,despite small shape difference.
Failure retained. Identical physical input to1s/400steps1094 took11.594s;
reference speed≤4.25e-10mm/s.1095 comparison passes0.1% displacement gate WITHOUT
floor:relative errors≤1.43452e-8,max pointdifference≤2.185e-9mm after subtracting
measured5mmRoot travel. This is Native gravity-reference shape agreement ONLY,
NOT force-equilibrium/material/fatigue/time/mesh or complete hardware Recovery.

## Load-dependent contact entry1084/1086

75g short120step/.3s Native trial12.732s;ONLY mass changed from485. NOT Holding.
50/75/100g all have first SkinZ impulse0.2625s. Within0.3s,iteration-limit
outputs2/4/2:NOT monotonic. Last SkinZ~0.375/0.390/0.396N and SupportZ~0.116/
0.345/0.585N. Thus an immediate mass-threshold solver explanation is unsupported;
100g sustained failure requires later contact-geometry/cable coupling diagnosis.
Do not infer physical capacity from this transient or increase force/friction blindly.

## Current scope and next performance work

FUNCTIONAL LIFT:exploratory50g/5mm only. RELEASE:observed. GRAVITY REFERENCE
SHAPE RETURN:bounded comparison.100gHoldingFAIL,Wrapping/variable stiffness/
time0.1%/mesh1%/whole energy/actual joints and materials/product Gates remain open.
No100gLift or motor/CAD adoption claim. All seven Native launches finished.
Next:read-only isolate100g later support-withdrawal/normal-direction transition
against50g before changing structure. Validate continuous supported contact
regions and same-input numerical sensitivity before any final capacity claim.
If physical interpretability blocks new load experiments,independent layer/
pressure/friction model requirements and actual bench protocols remain separate.

## Withdrawal temporal audit1099–1100 and next one-input trial

Actual100g2mm slip begins1.0975s,first POST1s iteration limit1.2875s,first20
consecutive negative-normal-Z outputs1.325s. During1–1.2s there are0limited
outputs and Skin mean support0.706453N<weight0.981N. Thus late normal reversal
and late solver saturation do NOT by themselves explain initial loss of support.
No continuous-event-time or unique physical-cause proof follows from saved data.
50g comparison has no2mm slip,negative-normal persistence or post1s saturation.

This supports a preregistered SINGLE INPUT sensitivity1101:100g baseline1059
with each cable maximum1.5→2.5N ONLY. No geometry/material/friction/solver/dt
change. Raising force is explicitly NOT a structural fix or motor specification;
it tests the observed early support deficit,with old100gFAIL preserved. All
hardware collision remains enabled. Actual outcome belongs to1101 and separate
analysers after completion;launch alone is not Holding PASS.

## Higher-force disposition1101–1105

1101 actual progress at243outputs/.6075s took~173.734s since launch file;
linear800output forecast571.965s>480s. Tool interruption exit130. No final
Native child result exists,so actual child exit/runtime stay NULL;this is
CANCELLED_COST_FORECAST,NOT a timeout,OS exhaustion or completed Holding FAIL.
Raw stabilised at246outputs/.615s with object.csv SHA unchanged across reads.
Source/preflight/partialRaw retained.1102 records maximum upward object motion
47.5367mm,speed680.695mm/s,45limited outputs and max solver error0.01131.
Root never rose:that motion is NOT Lift or reliable capacity evidence.

1103 independently finds actual tetra inversion at.4325s in fingers0/1 and
.4475s in finger2;minimum ratios−1.955/−5.982/−2.115. Candidate adoption rejected
by append-only QUALITY_REJECTION.json,without changing the original cancellation
verdict.1104 localizes first bad elements to SKIN,not Rail:ids414/446 around
materialX68.75/71.25mm,f0/f1;f2ids504/505/536 around82.5–86.25mm.
Later high-force object behaviour cannot be treated as valid mechanical performance.

1105 actual single full Film/Rails/Guide/Cable system removes object/support and
other two fingers;same2.5N,Root,material,mesh,dt and Native solvers.240steps/.6s
complete in2.424s under4GiB/120s. Inversion persists:first.520s,minratio−21.957.
All240Native constraint outputs have exactly2rows,maximum residual0,3iterations;
all remaining collision models share group1. Thus external contact/otherfingers
are NOT necessary for this high-input failure. Linear constraint convergence
does NOT establish acceptable nonlinear FEM geometry. No unique FEM,Guide,
mapping,integration or cable-linearization cause is certified by this contrast.

Next bounded physics task:separate actual thin-Skin bending response from
Rigid Guide/force-cable coupling in a single-finger no-contact reference before
any higher-force grasp. Do not repeat2.5N/higher-force full runs or change
material/friction/tolerance to mask inversion. Current1.5N50g Lift remains a
functional observation,not a high-load or physical-validation certificate.
