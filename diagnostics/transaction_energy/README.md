# Synchronized mechanical energy diagnostic

This is read-only instrumentation,not a replacement force law or an arbitrary
energy-balancing damper. Historical v1–v6 sources and runs are snapshotted in
the external raw campaigns. Do not rebuild over an old binary/output name.

For the tested standard implicit Euler setup (second order,non-trapezoidal,
no velocity damping option,no velocity-dependent ForceField matrix),the SDK
solves,after projective elimination,

`[(1+h alpha) M-h(h+beta) J0] v1 = M v0+h f0`.

Here `J0` is the actual spatial FORCE Jacobian,not a symmetric chart Hessian.
On the tested planar structural/isotropic-object mass scope,this gives

`Delta K = h f0.v1+h² v1.J0.v1-Dmass-Dstiff-Dvelocity`,

where `Dmass=h alpha v1.M.v1`, `Dstiff=-h beta v1.J0.v1`, and
`Dvelocity=.5 (v1-v0).M.(v1-v0)`. The stiffness term is recorded with its sign;
nonconservative Jacobians do not guarantee a positive Rayleigh term generally.
The actual kinetic-step residual is independently checked,not called heat.
Do not transfer this mass/constraint scope to arbitrary 3D gyroscopic dynamics.

For each conservative component,independently record

`R = Delta U+h f0.v1+.5 h² v1.J0.v1`,

and the derived quadratic projection `-.5 h² v1.J0.v1`. `R` is a signed
nonlinear/rotation/integration remainder,not dissipation. Normal contact uses
the same fixed material points,Hermite map and virtual-work pullback with only
the normal force law. FrameLayer's measured remainder is NOT assumed to be a
conservative Taylor remainder during plastic return or pressure transitions.

Cable force is active work,not stored `T*length`. Euler uses its linearized
force,so its algorithmic work is `h f_cable0.v1+h² v1.J_cable0.v1`.
The former begin-force geometric-displacement work remains a separate column;
their difference is measured rather than silently omitted. This algorithmic
work is not an assertion about an exactly resolved continuous actuator ramp.

Tangent contact uses the separately tested radial-return identity in
`models/contact_energy/ReturnAudit.h`. Plastic loss,endpoint spring projection
and detachment inventory are distinct. Material-frame increment work has not
yet been globally identified for every moving/deforming contact case.

BEGIN,pre-child-Commit END,and post-all-Commit driver records have explicit
step IDs. Pure queries must leave actual X/V/R unchanged. The 8s comparison
matches a separate pre-Commit return journal only after exact trajectory
equivalence to the same baseline has been established.

Unknown pressure work/full release/other integration variants are not replaced
with zero. A bounded8s balance is not full24s energy/12wrench certification.
In particular,this root-level pre-Commit observer is NOT synchronized to the
later independent structural-compensation component:that component runs in
the child before history Commit. Such a trial needs a separately validated
observer location after the arithmetic stage. Do not reuse this energy result
as certification of that new integration-arithmetic contrast.

The later v7–v9 observer insertion explicitly validates that stage:retain the
same live accumulator instance,insert the observer immediately after it using
public node APIs,and leave every ForceField's order unchanged. Actual1s/8s
X/V/R equivalence is required;this is not assumed from the old root observer.
v9 also audits the Frame slider from its actual pre-Commit plastic state and
compares predicted plastic loss with the real post-Commit Data. Its endpoint
projection is distinct from frictional work. Fixed-state stored slider energy
does not explicitly depend on the pressure-controlled yield capacity;the
clipped trial/returned energy does. Never differentiate that returned candidate
as if it were fixed-state pressure work. Physical normal compression/vacuum
source thermodynamics are not represented by this prescribed-cap law.

Energy units are model-force times mm;they are not certified PET/vacuum
measurements. Full-phase and time qualification remain separate from the
query-purity/API and bounded algebraic-identity checks.
