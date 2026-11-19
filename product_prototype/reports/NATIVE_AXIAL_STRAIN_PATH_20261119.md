# Installed Native axial strain path — 2026-11-19

Feature commit7701d5b. Continuation of loaded tangent459–466;not repeated testing.
Scope:straight centered100mm rectangular Rail2×0.5mm,E250MPa,
41/81nodes,PRIVATE failed poses from454/455. Actual unloaded state remains unchanged.

## Source path and implementation

Installed AdaptiveBeamForceFieldAndMass.inl addForce computes endpoint transforms,
a spline midpoint frame,local endpoint transforms,and displacement against native
spline rest transforms. Default reinforceLength=false,shearStressComputation=true.
Axial stiffness is EA/L. This is not simply chord length minus reference length.
reinforceLength and shearStressComputation branches change the force approximation;
neither is changed here.

A separate BaseObject observer links to installed BeamInterpolation and invokes
its actual transform/rest API. It exports local/rest origins,u0/u1,EA/L,midpoint
axis,chord length and two projection orders. It does not implement a ForceField,
ODE,contact solver,alter the SDK or install PRIVATE positions into state.

467 build failed because installed CreateSpatialVector() is non-const.
468 did NOT run physics:missing binary rejected. Its frozen source and failure
summary remain.469 uses mutable local observer temporaries;no SDK workaround.
470 completes6 guarded native queries at41/81 base/±ULP PRIVATE poses.
Each actual unloaded run saves2frames,center-position error0;the observer asserts
full actual Rigid3 q/v unchanged. Native force queries reproduce455 exactly(error0).

## Actual Native measurements

At the previously selected axial node,one ULP is6.938893903907228e-18m.
The measured native force change and assembled axial-component reconstruction are:

|Nodes|Native force change N|Axial reconstructed change N|Reconstruction difference N(max ±)|
|---|---:|---:|---:|
|41|1.699674944388e-12|1.699674944388e-12|1.03720e-18|
|81|3.399349888779e-12|3.399349888776e-12|4.15696e-18|

Thus the axial strain path quantitatively accounts for this sensitivity.
It does not prove that no representable equilibrium exists. Baseline axial-only
vs full global axial force differs~8.81e-14/8.74e-14N because other force
components/rotations remain;we do not call this a complete force reconstruction.

Absolute-midpoint and relative projection orders differ by up to
9.54098e-18/1.23599e-17m.471 compares equivalent algebraic projection at70decimal
digits with exact input binary64 axis/position coefficients held fixed.
Baseline maximum strain-coordinate differences are1.01995e-17/1.10681e-17m;
assembled force contrasts3.80776e-12/1.01075e-11N.
This is not a fully high-precision spline/quaternion reference or corrected
physical force. No calculation replaces the Native force or accepted state.

## Validation decision and bounded stop

Native force provenance/sensitivity diagnosis is complete. Strict fine-mesh
static equilibrium remains FAIL;no relaxation,error floor,position correction,
or new solver is adopted. Recent unit/origin/FD/precision directions have not
established a permissible remedy. Stop this direction rather than repeat sweeps.
This is a numerical/model qualification limitation,not OS resource exhaustion.

B3 functional50g Holding344/351 and release375 stay preserved as observations.
Full mesh/time,complete wrapping/energy,Guide clearance,100g,Lift and fabrication
remain unqualified. New queries are NOT B3 actual loaded-state validation.

Next independent product task:inspect saved375 actual Guide positions and
collision geometry to identify the physical components responsible for recorded
inter-finger overlap(~0.864mm). Do a static read-only provenance/clearance audit
before any geometry change. Do not remove collision models or claim a prescribed
pose as dynamic clearance. Only a justified new hardware candidate may be run;
fine-mesh physics gate stays blocked independently.

## Identity and reproduction

SDK:/home/ubuntu/SOFA/v26.06.00,installed ABI only.
469 binary4f5aede3ad22bca3144ad442885a09ab1236684631c7a44dc57fec8691a6589c.
Compiled C++4bb9800d9b776799e7bdfa42c3d3247d10ae69ca1e2b24bad934ca6e6521aec6.
BeamAdapter binaryef50c3685a75de4e777f8225c13fc0ee039d53cca7f2899af35e7ac7dd389df9.
Frozen guard:observer_identity.compiled_strain_observer().
Raw:product_prototype/results/native_beam_strain468, native_beam_strain470,
native_beam_strain_assess471. Sources,configuration,commands,hashes,ldd,process
runtime and SDK header hashes are in these directories. Native runtimes0.137–0.172s
per child,existing4GiB/480s limits;no long process needed.
Evidence:evidence_native_strain_v18/manifest.json;1258prior immutable files
verified,0mismatches;new manifest1351files.

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/native_beam_strain_assess471/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_strain_probe.py --tag UNIQUE_STRAIN
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_beam_strain_assess.py --tag UNIQUE_ASSESS
rg -n '375|Guide|gap|interference' product_prototype/reports/SKIN_ROUTING_AND_PRECURVATURE_20261119.md
```

The first command is the read-only restart;do not repeat completed queries
without a new hypothesis. Root work/contact area/pressure in this coupon are
NOT MEASURED. No physics children intentionally left running;no automatic restart.

