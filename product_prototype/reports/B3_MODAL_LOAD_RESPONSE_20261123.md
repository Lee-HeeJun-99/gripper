# Actual gravity/C2 modal participation1181

Started clean9d954a8. Implemented actual input/state forced-response analysis,
not another1137 spectrum. Read1159 Native restK/restCableJ/previous frames,
public Guide mass and actual1176/1179 q/v/Guide trajectories and C2 commands.
Mass-orthonormal modes on projected root,global ODE alpha1/beta1e-4. Actual
T(t) agrees with source C2 polynomial to1e-12N. Separate gravity/C2 modal
backward Euler and independent continuous polynomial forcing reference.
4GiB/120s worker1.631s. No Native rerun or state writes.

Lowest frozen26.7196Hz mode carries98.4841% gravity static compliance weight,
27.1432% Cable compliance weight,and83.0907% saved Native base/half squared
mass-displacement error summed over124 common times. Mode1(163.09Hz) carries
4.2078% of pair error;mode8(990.07Hz)3.3241%. Cable additionally strongly
projects onmode37(5911Hz),12.5245% compliance weight. These weights are not
contact area,measured energy or actual nonlinear eigenmodes.

Frozen linear comparison is conditional: rest chart reconstructs actual body
with max L2 error2.261/2.305mm by0.31s. Thus later mismatch is NOT uniquely an
integration defect. Initial stored velocity output is after first step,not
initial condition; reference initial q/v is rest/zero as actual scene.
Full per-mode input projections,error contributions in modes.csv;per-time
actual/reference mass norms and chart limits in trace.json. Old time FAIL,
energy/material/mesh/joint flags unchanged. PHYSICAL NOT QUALIFIED.

Next actual minimal Native control: linear no-Guide/no-Cable FEM coupon,
same mesh/mass/material/root/ODE; replace gravity by first-mode spatial force
projection. Compare actual single modal response with exact scalar reference
and backward Euler. Explicit altered load diagnostic,not gripper improvement.
Then proceed to one-variable grasp geometry and layer-friction coupon tracks.

Reproduce fresh tag:
`OPENBLAS_NUM_THREADS=1 python product_prototype/sofa/b3_modal_load_response.py --tag NEW_MODAL_LOAD`.
Actual inputs/source hashes and guarded process saved in results/b3_modal_load_response1181.

1199 follow-on actually projects accepted velocity/displacement at50/300ms and
actual deformed parent CableJ-transpose lambda/dt at297.5→300ms onto the same
rest basis. Mode0 contributes97.08% of base squared modal velocity at50ms,
79.17% at300ms;deformed Cable compliance weight88.33% (vs initial27.14%).
This change demonstrates why frozen rest load alone is not a complete late
reference. Initial scene q/v are truly rest/zero;first saved output is NOT t0.
Spatial angular velocity is not exact finite SO3-log derivative;reference
chart body error≈0.05µm at50ms and≈1.97mm at300ms. No energy/work certification.
