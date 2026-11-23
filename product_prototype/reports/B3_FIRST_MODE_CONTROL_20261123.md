# First-mode Native control1182–1186

1181 actual load participation implicated the lowest bending mode. New minimum
Native coupon removes Guide/Cable/contact and applies only first-mode projected
gravity spatial load to the SAME linear FEM/mass/root/ODE as1166. Mathematical
load diagnostic,not realizable tendon arrangement or changed-gravity grasp PASS.
1182/1183 FAIL: MechanicalLoad plugin declared after child component,so factory
could not create ConstantForceField. Guard stopped actual ERROR;1183 invalid
partial row also broke postprocessing. Original Raw kept,full failure copies
and hashes in1186. No partial state is performance evidence.

Fixed RequiredPlugin ordering and explicit Vec3d template,plus early failure
return before state assessment. Fresh1184/1185 actualNative100ms40/80outputs:
0.470/0.709s,no ERROR. Single28.5457Hz mode matches scalar backward Euler
to4.39e-7/6.10e-7 relative;continuous modal error still large.1186 compares
actual common outputs without floors. Thus large time error does not require
Guide mapping,Cable constraints or contact. It does NOT uniquely attribute
the entire nonlinear B3 failure. No solver/SDK/tolerance changes or production
modal filtering adopted. Do not repeat damping/dt search. Move to independent
grasp geometry and layer-friction research as requested.

Commands(fresh tags):python product_prototype/sofa/b3_first_mode_coupon.py
--tag NEW_BASE [--half]. Native4GiB/60s,hashes/preflight/logs preserved.
