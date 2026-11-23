# Actual interface kinematics and Native termination1268–1275

1268 reuses actual1266 all500accepted states100ms:position step identity
qnew-qold=dt*vnew error≤6.91e-18m. Cq=upper-lower-restgap max13.928nm;
Cv=max relativevelocity126.797um/s. (Cq_new-Cq_old)/dt matchesCv within
6.36e-14m/s. Selected sampled peak2500Hz is Nyquist ofdt200us,NOT a proven
physical mode. No forcedq/vreset,damping or customODE introduced.

Installed GenericConstraintSolver exposes scaleTolerance (rowcount scaling).
Actual1266 last519rows,error3.29e-8;maxerror5.18e-8~519*1e-10,2–3iterations.
Evidence-based contrast disablesONLY scaling,keeps numericaltolerance1e-10,
maxIterations1000,physical model,dt,loads,E,mass and all collisions unchanged.
Old root815 combinedflags/LocalMinDistance trial not repeated or overwritten.

1269pilot10steps2.441s/1270actual100steps20ms22.148s retain FAIL_EXECUTION
producerverdict due inherited `Unused Attribute:solverName`,although Native
exit0 andstatesfinite. The100step trial was launched before that warning's
cause was diagnosed;do not call that a validated pilot progression.
Old large/free/interface scenes also containthiswarning. Old verdicts/Raw
unchanged;explicit API link now validated independently rather than silently
ignoring the warning to turn the failed producer PASS.

Installed header SingleLink and actual TorusFall.scn example use linearSolver.
1271 changesonly GenericConstraintCorrection solverName→linearSolver=@globalLinear.
10step q/v/constraintimpulse differencesEXACT0,0ERROR/UnusedAttribute.
1272 clean unscaled pilot10steps2.472s,1273 clean100steps20ms22.148s,source
7cc6671,guards4GiB/120s,exactcommands/source/scene/plugin IDs inpreflights.
1275 common ACTUAL100outputs20ms,nointerpolation or relative floors:

|metric|scaled1266prefix|cleanunscaled1273|
|---|---:|---:|
|maxCq|13.7505nm|7.7576pm|
|maxCv|125.233um/s|.0567517um/s|
|maxNativeerror|5.1665e-8|9.9977e-11|
|maxiterations|3|111|
|iterationlimitoutputs|0|0|

Reduction~1772.52x inposition,2206.69x invelocityresidual. Cleanexplicit vs
oldauto unscaled1270 ALL100q/v/impulsesEXACT0,not only first10outputs.
Thus sourceAPI cleanup separated from termination contrast. This is stricter
Native termination,NOT threshold relaxation or a new material law.
Actual dynamics DO change relative scaled case;do not claimstateidentity.
0.1%time/1%mesh/fullenergy/grasp/actualjamming Gates NOT validated here.

1274 oldwarning run's auxiliary FFT description incorrectly said100ms even
though100samples20ms;no physical-mode inference used. Primary same-window
1275 records actual finaltime correctly. Preserve that oldfile,fix producer
description before any future FFT-based qualification.

1276 actual accepted-state PNG/SVG generated and visually checked. Separate
panel scales explicitly labeled,no error floor or interpolation.1277 fixes
the producer prospectively to record actual time window[0,.02] and20msFFT
description using the clean actual1273states;not a new Native dynamics run.

Reproduce(unique output):
`python product_prototype/sofa/layer_correction_link.py --tag UNIQUE`
`python product_prototype/sofa/layer_correction_link.py --tag UNIQUE --unscaled`
`python product_prototype/sofa/layer_constraint_comparison.py --tag UNIQUE`
`python product_prototype/sofa/test_layer_constraint_scale.py`

Next READY:use cleanexplicit/unscaled configuration for an independently
justified coupled-reference test,not blinddt iteration or immediateB3adoption.
Section/bendingmesh reliability remains first physical prerequisite. Git
oversizedhistory issue remains BLOCKED pending explicit repair permission.
