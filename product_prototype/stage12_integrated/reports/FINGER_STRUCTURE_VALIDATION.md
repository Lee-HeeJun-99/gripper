# Separate PET finite-rotation work — bounded, not a release

`finite_pet1` FAIL: node contacts missed a3.33nm inter-node radial violation
at60deg/n32 against the unchanged1nm geometric criterion. `finite_pet2` uses
exact circular-arc distance extrema instead; stored independent PET angles,
energy, normal multipliers and projected end-stop reaction are available.
Three angles15/30/60deg;8/16/32segments; energy16→32error<=0.0652%.
This is an inextensible PET / **prescribed rigid circular rail fixture**,
friction0, typical modulus. It is NOT a solved flexible Rail, actual friction,
3D shell, complete finite guide contact or material certification.

At60deg the RevAB end-stop constraint consumes0.600mm, with~0.071N reduced
reaction. Removing only that endpoint stop gives1.40643mm migration. The
simple offset-angle travel estimate used earlier does not bound this relaxed
PET shape. Actual endpoint-channel inequalities are not a full finite 3D lip.

RevAC candidate therefore trims3PET ends another1.20mm, nominal gap1.80mm;
actual304part STEP and3part STEP/STL generated, other301parts reference AB/AA.
It is NOT adopted. CAD nominal changed-vs-all solid intersection0.
The initial default-integral volume check FAIL6.99e-8 is preserved. Independent
adaptive integrals on SAME STEP give volume1.52e-11, centroid1.21e-12m,
inertia1.72e-11 relative errors;3newSTLs closed/positive. No threshold changed.

`finite_pet_AC1` at60deg gives1.36682mm migration; projected end-stop inactive
and energy refinement0.0474%. However **actual front/back BRep checking** in
`channel_geometry1` FAILS: reconstructed PET versus actual retained AB front
has positive overlap. At60deg AC gives17.7368mm3 vs AB14.7935mm3; both back
overlaps0. A shorter PET is therefore NOT an accepted solution.2→4loft
subdivision results remain positive, not tiny tolerance noise. These are
prescribed fixture shapes, not observations of physical collision/damage.

This is the required distinction between an internally consistent endpoint
model and actual finite geometry. Next diagnostic separates original front
body and new lip before changing either CAD or contact equations. No global
Stage1 approval, same-revision Stage2 qualification or real hardware claim.
