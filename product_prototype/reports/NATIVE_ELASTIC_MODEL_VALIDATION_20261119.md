# Native elastic validation continuation — trials380–405

## Scope and decision

B3 functional50g Skin holding344/351 and release375 remain unchanged. They are
NOT promoted to physically converged/product-qualified results. No B3 geometry,
material,actuation,collision model,SDK,old Raw or old verdict was changed here.
No100g,Lift or new grasp optimization was run. Existing time.1% and mesh1% gates
remain in force. The bounded static diagnostic family is checkpointed after repeated
force-residual/mesh failures;this is NOT OS exhaustion or completion of ReGrip.

Detailed machine evidence: `evidence_native_elastic_v7/manifest.json`.
Actual Native scenes,commands,stdout/stderr and states:
`product_prototype/results/` named trials380–405 below.
Older `evidence_native_elastic_v6` is retained,not overwritten.

##372 failure and actual Jacobian

372 starts at residual2.88675e-5N. The first Newton step reduces it to3.72033e-9N,
then failed line searches fluctuate around4–5e-9N rather than meeting1e-12N.
Those partial states are not accepted static results.381 translates the SAME
straight bonded Skin+rails to remove its50mm world offset and separately changes
to consistent mm–N units (E scales by1e-6). Both fail the unchanged force criterion.
394's installed EigenSimplicialLDLT contrast also fails.403's native method=large
contrast has failed line searches and ~1e-9N residuals despite process exit0 and
some native CONVERGED messages using default successive-ratio stopping. It remains
FAIL. Production B3 uses method=large;small-method diagnostic results do not certify it.

NativeElasticMatrixObserver is a separate INITIAL diagnostic BaseObject,NOT a new
ForceField,ODE or contact solver. It queries existing native addKToMatrix/addForce
into private buffers,never injects a force or modifies q/v. Build400 links ONLY
installed v26.06.00 libraries;402 preserves ldd,source,CMakeCache and binary hashes.
Native force queries can alter internal caches:do not claim general query/history purity.
402's two-step solid tetra/hexa q/v and absolute times match the corresponding
unobserved389 states EXACTLY (difference0,STRICT1e-12). Thin372 still fails,so
no thin-model trajectory equivalence or accepted static state is claimed.

402 projected initial native energy-stiffness spectra:

| Case | Minimum eigenvalue N/m | Maximum eigenvalue N/m | Symmetric-part condition |
|---|---:|---:|---:|
| Solid tetra21 | .0864176 | 43893.4 | 5.07922e5 |
| Solid hexa21 | .0588662 | 17387.4 | 2.95371e5 |
| Thin bonded tetra21 | .125527 | 3.72092e8 | 2.96424e9 |

Symmetry errors are0–1.58e-16 relative. At FD displacement1e-7m,the native force/K
relative errors are1.53e-11,3.28e-11,1.97e-11 respectively. Errors grow as FD
epsilon shrinks (recorded1e-8/1e-9,not hidden with floors). This supports severe
conditioning/arithmetic sensitivity,NOT a uniquely proven bug or permission to
relax gates. Cases differ in section/material/boundary details;do not interpret
their eigenvalue ratios as experimental B3 stiffness ratios.

## Native model availability and reference tests

380/382:100×10×10mm straight solid,E1MPa,nu.3,root face fixed,no contact,cable,
guide,gravity or time integration. This intentionally differs from B3's250MPa
thin bonded section. Native tetra and hexa both actually execute. Small load1mN
and.5mN yield nearly proportional response;strict relative1e-12 diagnostic fails
one tetra41 pair at8.95e-12. That is not the project's absolute state-API test.
All measured11/21/41 mesh pairs fail1%. No equilibrium stiffness ratio is inferred
from a failed run. Native strain energy/reaction were NOT measured in these runs.

383 hit the CSV parser's131072-character limit after actual execution. It has no
complete producer summary;Raw is preserved.384 fixes parsing prospectively and
sets all Newton stopping options explicitly.386 hexa161/321 fails1e-12N with
~1.70e-12/4.95e-12N late residuals;neither result is used as converged reference.
387 failed an unsupported Mat6 sparse template;388 uses the installed scalar
template at an explicitly smaller10uN load. Native circular BeamFEM11/21 gives
6.790610875/6.790610874um versus approximate Euler6.790610905um.41 fails
~1.35e-12N residual. Not a completed beam mesh gate or B3 substitute.

392 runs the INSTALLED primary examples for TriangleBendingSprings,
TriangularBendingSprings and FastTriangularBendingSprings for2 batch steps without
errors. They are AVAILABLE,not calibrated thickness-based shell/grasp models.
This factory/example probe is not treated as physical bending validation.

393 is a separate exact AXIAL patch:nu=0,uniform consistent end traction,
u_x=F*x/(E*A),u_y=u_z=0. Actual tetra/hexa11/21/41 all nodes at BOTH saved
static outputs match the exact solution to≤1.39e-17m,passing1e-12m.
This isolates basic elastic/load assembly;it does not validate bending/contact/time.

## Pure bending,thickness and independent inventory

389/390 replace uniform-per-node tip forces with area-weighted loads,so cross-section
refinement no longer silently changes that nodal quadrature. For tetra this
tensor-product quadrature is NOT identical to consistent triangular face traction.
396 explicitly integrates actual triangle/Q4 face traction consistently.

396 exact linear3D reference at nu=0:
u=(-k*x*z,0,k*x²/2),sigma_xx=-E*k*z,k=.01/m. Root-face displacements are zero;
only end traction is applied. Exact tip=50um. No prescribed SOFA deformation is used.

| Native model/section |21 nodes field error |41 nodes |81 nodes |
|---|---:|---:|---:|
| Hexa,10mm,cross3 |11.1111% |3.03030% |.775194% |
| Hexa,10mm,cross5 |11.1200% |3.03425% |.776494% |
| Tetra,10mm,cross3 |45.6266% |35.7922% |Native solve FAIL |
| Tetra,10mm,cross5 |33.2808% |17.8927% |Native solve FAIL |
| Hexa,5mm,cross3 (398) |33.3333% |11.1111% |3.03030% |
| Hexa,5mm,cross5 (398) |33.3369% |11.1133% |3.03129% |

398 changes ONLY reference thickness and its consistently integrated bending load;
it is a distinct physical diagnostic,not a same-force product comparison.
For a restricted Q1 pure-curvature ansatz,the shear energy adds
G*A*dx²/12 to E*I. At nu=0,its tip ratio is1/[1+.5(dx/h)²]. Cross3 observations
closely follow that prediction. This is evidence of shear-stiffening in THIS
diagnostic,not proof that every B3 transient/inversion has the same sole cause.
81-node hexa's <1% exact-field error is an individual reference check;the21/41/81
ALL-PAIR mesh gate still FAILS. Failed tetra81 states are not plotted as solutions.

397/399 independently integrate standard small-strain Q1 hexa stresses/energy on
ACTUAL accepted Native states,without solving/correcting them. All12 inventories
meet their stated.1% linear-work and1e-12N free-residual diagnostics. Maximum
relative energy identity defect is~5.14e-10;free residual≤7.43e-13N. Positive
Gauss Jacobians and actual small strains are recorded. Reaction forces/moments
are independent QUADRATURE reconstructions,not queried native constraint multipliers.
Native potential energy and whole dynamic/root work remainNULL. This is not a
global grasp energy certificate.

## Skin/Rail initial-state decomposition

404 initially reversed Skin material classification because the mount maps positive
local thickness INWARD (world radial x=50mm-local z). Its raw scenes/data are retained,
but its component LABELS are invalid and excluded from physical comparisons.
405 fixes the classification prospectively and asserts analytic Skin volume210mm³.
Volumes are210/310/410mm³ for Skin/one-rail/two-rail. Positive reference tetrahedra
and root indices are checked;all six zero-load observed/control runs complete.
Initial q/v differences and rest-position errors are EXACTLY0 in all three cases.
Projected initial condition numbers are4.09510e9/3.31436e9/2.96424e9.
Thus poor initial conditioning exists BEFORE adding Guide constraints or even Rails.
This does not rule out additional Guide overconstraint in the actual B3 assembly.
These are INITIAL spectra/identity checks,not loaded bending stiffness ratios or
dynamic component validation. Added volumes are intentional;mass has no role in
this static diagnostic. No misleading identical-volume product comparison is claimed.

## Preservation,build and continuation

395 byte-verifies10613 prior immutable mechanism files with zero mismatches.
The final manifest hashes new Raw/scenes/producer copies and native binaries/SDK.
No long grasp rerun was used to obscure the failed mesh/time gates.4GiB/480s
per native child was retained;actual runtime is recorded per process. Matrix
inspection has a4096-DOF preflight bound. Memory peak was NOT MEASURED.

Observer binary:cad/build_elastic_observer400/libReGripElasticObserver.so,
SHA256 c2e3eac945fdbe6ccb4bb66817077db453f900d2d1092327238af03b5a1fb7f7.
Historical controller332 SHA3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0
is unchanged. Exact compiled observer source is preserved in402/Observer.cpp.

NEXT:initial Skin/one-rail/two-rail decomposition is now completed405;do not repeat
it as new research. Extend to physically small LOADED section reference tests,
separating thin tetra kinematics/force arithmetic from installed alternative native
elements,then add root/guide attachments incrementally. Distinguish bonded tetra
section discretization from rigid guide overconstraint. Do not tune force
tolerances or blindly double mesh/duration.
The remaining initial linear-algebra/force-arithmetic discrepancy needs a separate
reference/backward-error diagnostic;do not inject an independently solved pose.
Only after section/attachment mesh and time gates pass may B3 be requalified.
Full hardware clearance still fails375;100g/Lift/fabrication remainNOTRUN/NOTQUALIFIED.

Exact read-only re-entry:
```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
git status --short
git log -3 --oneline
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_matrix_assess402/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_hexa_inventory397/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_section_spectrum405/summary.json
```
Reproduction of the implemented diagnostic (NEW output name required;not a new
research result merely because it is rerun):
```bash
OPENBLAS_NUM_THREADS=1 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_matrix_assess.py --tag native_matrix_reproduce_next_unique
```
No background continuation or session restart is promised.
