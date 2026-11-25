# Supported winch to actual Skin/Rail Finger —1879–1887

Continuation after bearing-loaded component1876. This is a new ideal-bearing
research mechanism, not the rejected finite hub CAD1873. Actual material,
root bearing/contact/retention, return bond and wire termination unqualified.

1879actual internal two-ended Native CableConstraint couples supported rotor
to independent16mg translating load head under0.9N downward force. HeadZ
free, no imposed q/v/upward applied force; XY fixture cannot support vertical
load.6000steps/.6s normal/noERROR4.88360s, rise4.01743190149mm vs independent
constant-length target4.01743190182mm. Inputpeak0.948090N<1.5cap; actual
output row gives vertical0.9N within3.187e-14N, head momentum residual
<=8.824e-21Ns. No buckling pushrod. Output ideal tendon radius envelope0.25mm
has necessary rotor-slab clearance0.25mm; finite anchor/finite-wire contact
not qualified. Output deadweight port is not Skin or100ggrasp.

1878independent nominal bulk proof uses exact rational lower bound for
cos(pi/32), no CSG tolerance: shaft/sleeve98.31194um and sleeve/rotor42.52431um
lower clearances outside explicit root/cap socket joining domains. Does NOT
rescue1871/1872FAIL or1873REJECT: emitted STL interface artifacts unresolved.
Hollow axle stress references0.35908MPa shear,1.63459MPa bending; return root
bond1.03366MPa and cap0.826924MPa torsion references. All actual allowables NULL.
Controlled1876peak actual rotor speed1.52751rad/s, not1299rad/s uncontrolled.

## Actual single Finger integration and diagnosed failure

1880initial rotor1/support0 boxes overlap: insufficient AABB separation,
not proof of actual collision. No Native.1881exact closed-solid check shows
zero bulk overlap, but first Native factory fails on inherited coupon
ConstantForceField and missing plugin. Also that deadload must not remain
when actual Finger replaces the output load. Failed Scene/logs retained.
1882removes that inherited deadload, **not a Skin/Guide collision model**.
Two real mass-bearing rotor/BeamFEM winches at the original world pullpoints
replace force-only sources by physical C2 connections to existing six-guide
tendon paths. Skin/Rail/FEM/guide attachment/material/root/dt2.5ms unchanged;
other Fingers, object and Support explicitly removed for no-object isolation.
Added finite rotor Triangle/Line/Point collisions retained throughout.
Native100steps/.25s normal/noERROR3.18364s; saved FEMminratio0.99450216,
max Skin nodal motion10.1011mm. Only startup/deformation scope, not causal
actuation or bracing-free qualification.

1883matched zero-stroke Native control completes, then analysis fails its
incorrect4global-row assumption. Actual22/25rows include contacts; no force
assigned by exclusion.1884reuses frozen NativeCablePhase/ResponseRows/
DetectionPairs on the active trial, no reimplemented physics.100steps3.22125s,
exact0 q/v/all-multiplier difference from1882.
1885actual row ownership finds right rotor Line–Support0 Line contact:
309nonzero response rows, peak absolute row multiplier/dt0.366703N.
Count is not area; peak is not net vertical support or bearing reaction.
Actual inputpeaks0.865172/1.014377N, outputpeaks0.856523/0.863272N.
Reference min-z vertex moves inward8.80411mm vs zero-stroke control, but
mechanism **FAIL unintended root contact**, not unbraced actuation PASS.

##1886outward-handed mounting, not random offset scan

Root cause is same-handed mounting: right lever points toward existingSupport.
Right module whole-frame180deg aroundZ now mounts outward. Same dimensions,
moment arms, material/mass, commands and initial output origins; right initial
mass tensors transformed consistently, same free axial DOF. No collisions
disabled. Initial every rotor/FEM/Guide separating gap exceeds0.2mm contact
budget.100steps/.25s normal/noERROR1.94105s, saved FEMminratio0.99462615.
Actual contact response has **zero nonzero rows**, not hidden brace removal.

1887same outward fixture zero-stroke control:100steps1.81218s normal/noERROR,
minFEMratio0.99998158. Active-control reference min-z vertex dx=-8.966225mm,
dy=-1.611e-7mm, dz=5.090594mm; max nodal difference10.31055mm. Inputpeak
0.853520N, actual outputpeaks0.8449722/0.8449723N. Fouractual rows are verified
Cable rows, not assumed: input+output two per winch, no contact responses.
Input geometric error<=82.231nm; output C2 errors<=0.566488um.
PASS **incremental inward actuation of one no-object Finger only**. Zero-stroke
control retains gravity and taut length constraints; not a slack gravity model.
No full closing, wrapping, physical joint, energy/time/mesh or100gclaim.

Actual commands (environment Python, NEW tags only for any rerun):
```sh
python product_prototype/sofa/tensile_output_native.py --tag tensile_output1879
python product_prototype/cad/bearing_nominal_bounds.py --tag bearing_bounds1878
python product_prototype/sofa/supported_winch_finger.py --tag winch_finger1882
python product_prototype/sofa/winch_finger_control.py --tag winch_control1883
python product_prototype/sofa/winch_observed_prefix.py --tag winch_observed1884
python product_prototype/sofa/winch_transfer_assess.py --tag winch_transfer1885
python product_prototype/sofa/supported_winch_finger.py --tag winch_outward1886 --outward-handed
python product_prototype/sofa/winch_finger_control.py --tag winch_outward_control1887 --source winch_outward1886
```
1880/1881require their own preserved producers to reproduce failure.1879/
component children4GiB60s; actual Finger children4GiB120s. No old result
overwritten, no SDK/FF/ODE edit or q/v correction, no force/tolerance/dt scan.
Actual Scene/source/binary/commands in per-case preflight/summaries. Frozen
332journal/control and1831phase binaries hash checked; Raw stays local.
Latest full1741stillUNBRACEDFAIL;1586bracedOBJECT-ONLYPASS unchanged.
