# Separate AK finite three-pad support candidate

One fixed design evaluated: three radius3mm, height6mm cylindrical pads,
centers at radius25mm and60/180/300degrees; top z=-12mm, bottom z=-18mm.
New STEP/STL artifacts are external candidates only. AK235 parts and adopted
RevAA CAD/BOM are unchanged; no bottom foundation is specified or qualified.

All235 actual part source hashes verified before geometry analysis. Each pad
contacts the actual Palm underside over28.2743338823mm².702 exact other-part
intersection volumes and three Palm volumes are below1e-7mm³. No connection
of these pads to ground is implied. Independent .001/.002mm volume slices
reproduce contact areas within5.3e-12mm² and centroids within1.5e-13mm.

Normal unit reaction wrench is [0,0,1,y,-x,0], in N and Nmm about the Palm
origin. Uniform pressure yields a rank3 basis. Independent cross products
and virtual work agree; a1% area perturbation is rejected. Centered -1N
compression needs1/3N per pad. Uplift needs negative normal reactions and
is rejected. Fx and Mz cannot be balanced. A1N compressive case with My40Nmm
also requires a negative reaction in this basis. This is a conditional
pressure-basis test, not certification of arbitrary distributed contact.
The latter case is also outside the pad footprint x-extent; no allowable
or material strength is assigned. No actual assembly load envelope is known.

Thus the candidate identifies finite usable compression bearing surfaces,
but fails complete support: positive lift-off/lateral/torsion retention,
foundation attachment, preload/friction, compliance and strength remain open.
No full-Palm equilibrium, mesh convergence, global energy or release PASS.
Do not replace the old unsupported annular fixation with fixed pad nodes.

Failure records retained: first export used a double extension and exited1;
first verifier could not JSON-serialize NumPy bool_ and exited1. Original
producers, inputs, logs and partial artifacts remain under their own tags.
Corrected analysis and verifier exit0, with all stated checks inspected.
Four analysis children, each4GiB/420s and one thread; no SOFA run. The read-only
release audit remains INTEGRATED_NOT_QUALIFIED. Supervisor local save pending;
the worker did not attempt git add/commit, push or launch managers.

Next independent design must supply side/torsion and lift-off retention and
a finite connected ground path, with actual interference/load/preload bounds.
Do not repeat this fixed three-pad scan or refine the old unsupported P1 solve.
