# Finite eyelet/support conditional union moments

Cycle658–659 follows Native matrix fix3a5844b;it does not change the simulation.
Existing v11 polygonal eyelet and convex support overlap intentionally. Summing
their component masses double-counts that region if they are manufactured as ONE
homogeneous solid. If separate materials/join are used,another inventory is needed.

Implementation:decompose annular polygonal prism into disjoint convex sectors;
intersect each with the actual proposed convex support via halfspaces. Signed
simplex integration computes volume,first and second volume moments. Apply
inclusion/exclusion BEFORE dividing by volume and moving inertia to COM. No
Monte Carlo,voxel replacement or invented density. Tangent/degenerate intersection
is explicitly rejected instead of silently dividing by an arbitrary small value.

658:12 geometrically distinct finger0 parts,64facets;other fingers are rigid
rotations. Overlap2.352837–2.364746mm³. Naive additive-volume overcount reaches
3.325943% of union volume;conditional COM bias reaches0.332201mm.
These are geometric quantities,NOT measured hardware mass or inertia.

659 bounded4GiB/480s children:
-Analytic intersecting-box and union-box volume/COM/inertia reference PASS.
-Disjoint solids give zero overlap;tangent degeneracy explicitly rejects.
-Rigid rotation/translation of intersection moments PASS.
-Annular sector decomposition and nonzero-overlap reference PASS.
-32/64facet conditional union sensitivity measured on all12parts:
 volume≤0.0595521%,normalized inertia≤0.0802508%,COM≤0.0612448%.
 This is NOT Native FEM/contact mesh1% qualification or a new physical Gate.
-Worker runtimes1.715s/2.719s;tests0.710s.RSS NOT MEASURED.

658 exploratory geometry worker was not run through the child guard;659 repeats
under the required guard with new analytic/objectivity/facet hypotheses. All Raw
retained. No SOFA child is represented by this geometry calculation.

Source/Raw:product_prototype/sofa/finite_union_moments.py,
results/b3_finite_union658 and b3_finite_union_reference659[_facets32/_facets64].
Evidence:evidence_product_union_geometry_v32/manifest.json.

Reproduce with unique tags:
```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/finite_union_run.py --tag UNIQUE_UNION_REFERENCE
```

Not generated:CAD Boolean BREP,STEP assembly or physical mass calibration.
Material density,joint geometry/strength,manufacturing tolerances remain unknown.
Do NOT replace B3 lumped mass/checkpoint from this conditional geometry result.
Next:keep Native contact policy/time failure652 separate;no more blind dt/alarm
sweeps. Physical union inertia adoption needs an explicit manufacturing/material
specification and separately qualified Native body/contact model.
