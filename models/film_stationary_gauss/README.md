# Isolated stationary-origin Gauss pilot

Actual SOFA owner reuses qualified Gauss4 film blocks and the existing free
rigid midpoint rule. Input is the exact stationary FREE50ms checkpoint with
public mass,root map,quaternion and accumulated time restoration. Zero load,
zero tension,zero angular state and one200us step only. Original maximum-step
budget is unchanged;count!=0 rejects a second solve. Not a general integrator.

Actual1614 q/v and all film Gauss stage q/v/forces match the independent
same-nominal-dt reference EXACT. The passive observer ON/OFF endpoints match
EXACT. Older local-refinement coarse interval used endpoint-minus-clock,which
is1.2e-18s shorter than nominal200us;that cross-duration result is NOT used as
a strict API identity reference. Original1612 preflight rejection is preserved.

The Gauss position polynomial's derivative is the linear stage-velocity
interpolant. With a linear rigid midpoint position path,maximum nodal speed
and centre speed give a conservative1-Lipschitz whole-triangle distance bound.
This certifies the declared numerical path,not exact continuous ODE motion,
physical thickness,self-collision or friction. No contact projection is used.

Output `REGRIP_STATIONARY_GAUSS_PILOT_V1` is a distinct isolated-pilot schema.
No resume reader is qualified for it yet. Use the qualified stationary FREE
checkpoint at50ms for independent follow-up,not a silent schema conversion.
Global time/mesh/energy,recovery,holding and lifting remain unqualified.

## Explicit800us isolated transition

1615/1616 independent800us1/2/4/8/16/32 state/energy comparisons and1617
all film shape comparisons pass the existing.1% local gate.1615's old scope
text incorrectly says200us;its span_us800 and endpoint50.8ms are authoritative.
No historical result was overwritten to repair that label.

`StationaryGaussExpandedPilotODE` restores the original200us checkpoint first,
then explicitly changes dt to800us at unchanged accumulated time. Physical
q/v/quaternion remain EXACT;existing public clock traversal checks all11
contexts. No input state/time/dt/step token is edited to bypass the reader.
The transition is recorded separately in `.dt_transition.csv`.

Actual1618 endpoint and all film Gauss stages match the independent nominal
800us reference EXACT;gap lower bound+.289800mm,momentum6.39628e-23Ns.
Output `REGRIP_STATIONARY_GAUSS_EXPANDED_PILOT_V1` has NO qualified resume
reader. This remains a ONE-step pilot,not a long-trajectory accuracy/speed or
energy certificate. A cumulative same-seed window is tested separately.
