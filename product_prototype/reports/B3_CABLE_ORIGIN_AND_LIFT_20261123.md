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
