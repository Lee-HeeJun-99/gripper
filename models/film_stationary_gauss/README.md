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
