# Immutable element-refined curved contact — EXPERIMENTAL

Independent `PatchRefinedContact`,generated from the hash-bound frozen
`CurvedMaterialContact`. Original components/binaries remain unchanged.

`edgeSpacing` is empty by default (the exact parent grid). Otherwise it has
one positive finite spacing per reference element. Each element still uses
the parent's immutable midpoint material sites,reference-length weights,
birth-aware Coulomb return,spatial Hermite virtual-work map and Commit.
No integration point moves with the contact patch. No interpolation,history
remapping,changing contact law,additional force or modified physical gate.

The old global `historySpacing` minimum remains unchanged. Explicit per-edge
resolution is a new numerical interface,limited by the same one-million-total
material-site bound and per-element `materialCells` guards. Its entire vector
is included in the frozen parameter signature,so mid-run changes are rejected.

The first research contrast refines fixed reference elements90--100mm on all
six layers of the21node scene. Background spacing .00125mm remains fixed.
Local .000625/.0003125mm gives528000/624000total states,below the preserved
one-million limit. This region was selected from prior actual contact traces;
it is NOT a claim of uniform interface-resolution convergence or a universal
contact location. Arbitrary future contact can leave the refined region.

Actual SDK API tests exercise explicit edge resolution,analytic plane loss,
force/Jacobian FD,addDForce/stiffness/query purity and invalid/mutated grids.
Uniform-grid actual dynamics must match the parent before a local refinement
trial. Profiles determine bounded cold-start prefix runs. No checkpoint
trajectory restart is permitted. Passing a prefix is not full grasp approval.
