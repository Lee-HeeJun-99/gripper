# Native layer-pressure/friction coupon — exploratory research

New independent track,NOT a Young-modulus change or calibrated layer jamming.
Two separate40x10x0.2mm strips,Native large-tetra FEM,2µm initial interface
gap,actual Triangle/Line/Point interlayer friction contact. Opposite outer-face
nodal pressure loads approximate pressure differential;no vacuum chamber,
membrane/seal model or measured pressure/friction data. Assumed E2.5GPa,
density1400kg/m³,nu0.3,mu0/.3,p0/1000Pa are RESEARCH INPUTS,not confirmed PET.
Both roots fixed;total bending load0.1mN,constant for this transient coupon.
Native global ODE Rayleigh1/1e-4,dt200µs;not measured damping or convergence.

1188 pilot50steps/10ms actualNative5.085s,0ERROR;both layers finite,
min volume ratios0.999922/0.999937. Native detector and multiplier journals
record actual contact;solver residual not automatically qualified byexit0.
Forecast500steps~50.85s each within4GiB/120s guards,atmost3physicschildren.
Next matched trials:zero pressure/friction;pressure withmu0;pressure withmu.3.
Same E/mass/mesh/root/bending force/time. Compare transient tip displacement,
interlayer slip,gap andsolver status. No static stiffness ratio unless equilibrium
confirmed,NO vacuum-jamming/holding/product PASS. Work/heat/pressure map NULL.

Actualcommands/source/binaryhashes/SDK in each preflight. No detector.csv used.
Reproduce fresh tag:python product_prototype/sofa/layer_pressure_coupon.py
--tag NEW_LAYER --pressure 1000 --mu .3 --steps 500.

## Actual matched runs1189–1192

Completed500steps100ms:free3.146s,pressure/slip5.954s,pressure/friction32.607s.
No NaN/element inversion/NativeERROR. BUT independent strict tetra-centroid
inside-other-tetra witnesses show interlayer intersection from1.4ms(mu0)
and1.8ms(mu.3).1192 flags both FAIL_INTERLAYER_INTERSECTION. Tiny final
velocity and near-unit element volumes do NOT validate layer contact.
Free case has no such witnesses,corresponding interface gap≈2µm. No stiffness
ratio calculated;contact force/energy/heat remainNULL. Simulator state-only
status was not a physical PASS and is not rewritten after assessment.

New testable cause hypothesis:step pressure allows free-motion surfaces to
cross before discrete contact resolution. One explicit NEW protocol uses
Native LinearForceField ramp0→1000Pa over10ms with SAME E/mass/mesh/dt/mu and
tip load. No state corrections,dt reduction,tolerance/alarm changes. Ramp is
not a retroactive cure of step-input failure or a calibrated vacuum model.
First50-step pilot1193,then independent accepted-state overlap assessment.

## Ramp and rigid controls1193–1197 — still FAIL

1193 actual50steps3.820s,1194 independent overlap from6ms despite pressure
ramp. Delay is not a cure. No500step ramp trial launched after this failure.
1195/1196 independent rigid thin-layer on thick fixed support controls,
normal preload ramp then lateral force,mu0/.3,100steps20ms,0.168/0.167s.
Actual rigid corner audit1197 proves both bodies entirely below support bottom;
FAIL_CONTACT_GEOMETRY. Thus even this component control is not friction-law
validation. It is not evidence that SOFA never supports friction;this specific
thin-geometry/pressure/input/scene path is unqualified. No coefficient tuning,
dt/alarm reduction,custom contact or artificial fixing used. Stop this direction
until a separately validated contact fixture/contract is available.

P2 pressure/friction simulation BLOCKED,actual PET/vacuum/friction NOT MEASURED.
Independent next task:conditional laminated cartridge/pouch CAD and theoretical
free/slip vs bonded stiffness bounds,not a jamming performance claim.
