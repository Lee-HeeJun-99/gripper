# Accepted Native primitive work inventory1241

Reuses1230–32 actual accepted states/impulses. No new Native trial or state
edits. Source12ba7c0;producer/source/input hashes in result summary.
Initial q/v is actual configured pose/rest;force sampled at previous time
as independently checked,alpha=1 from unchanged Native ODE setting.

BE translation identity:
DeltaK = dt F_begin dot v_new + I_contact dot v_new
         -dt alpha m |v_new|² -.5m |v_new-v_old|².

Report tangential/normal contact work separately. Last term is NUMERICAL
BE loss,NOT physical heat or calibrated friction. End-step implicit contact
work is not continuous-time energy convergence. q_new-q_old=dt v_new checked
independently (max1.25e-18m). Actual angular velocity0 in this lab fixture.
Fixture reaction work and whole system energy remainNULL.

Sliding1232 actual20ms inventory:
- kinetic change +2.614340096e-4J
- external work +1.346919171e-3J
- tangential contact work -1.077586809e-3J
- normal contact work -4.797760e-9J
- damping work -1.467320458e-6J
- BE numerical loss +6.426233460e-6J
- cumulative identity residual -8.30e-20J

All3controls have maximum step residual≤6.18e-20J. Scoped algebraic PASS
ONLY,not B3 energy,pressure/friction material or product qualification.
Static control's tangential work~2.4e-20J retained as floating residual,
not clamped to0 or interpreted as physical heat generation.

Reproduce: `python product_prototype/sofa/primitive_work_inventory.py --tag UNIQUE`
Regression: `python product_prototype/sofa/test_primitive_work.py`

Next READY: temporal feature-response attribution during actual line→face
transition~10–12ms(center frictionless case),or independent bending-reliable
layer discretization. No blind dt/normal/alarm/friction sweep;no full B3
100g rerun without interpretable new mechanism hypothesis.
