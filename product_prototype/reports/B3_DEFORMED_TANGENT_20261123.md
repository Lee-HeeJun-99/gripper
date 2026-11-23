# Native deformed-state tangent1120–1126

Starting63711a7,clean. Newdiagnosticmodule ONLY;no new ForceField/ODE law orSDK
edit. Build1120 sourceProbe.cpp+CMakeLists+CMakeCache/ldd saved. InstalledSDK
v26.06.00 only. Reusablebuild:product_prototype/cad/build_deformed_probe1120/
libReGripDeformedProbe.so;SHA cc416db54a5fe91a4979d4aa1731074f4077ca5462247f9085ebcd3e0841bc64.
Frozen sourceSHA119685ca21f8a9985cc18756adb5ff7cff12eeec933c3a6fea6bb432a1abbd10.
Build guard4GiB/120s,actual4.784s. SDK/binary not substituted into older cases.

Probe listens once atAcceptedEnd,usesPRIVATE force buffers andnormalized sine
direction. It refreshes the native force cache atactualq,queriesaddKToMatrix,
thencentralFD at1e-7/1e-8/1e-9m. Finalforcequery restoresactualq cache. Never
writes actualq/v/force;still requires external trajectory purity validation.

| Case | Sample | Max FD relative error | q/v/Guide difference vsoriginal |
|---|---|---|---|
|1121|100ms|0.02589645%|exact0 over44outputs|
|1122|300ms|0.48949466%|exact0 over124outputs|
|1123|470ms|0.94724021%|exact0 over192outputs|

All three Native runs complete,noERROR,actual0.808/1.910/2.713s. Observerpurity
passes1e-12 ONLYover testedprefixes;single-direction tangent exceedspredeclared
0.1% at300/470ms. This is NOT a timeconvergence test or fullmappedtangent gate.
Forcecache repeat check also journaled;matrix/state/FD files retained.

Installed TetrahedronFEMForceField.inl accumulateForceLarge recomputes rotations
frompositions;addKToMatrix/computeStiffnessMatrix rotateelementmaterialblocks.
Inference: the supplied corotational tangent neednot equal the full nonlinear
force derivative. Diagnostic failure alone is NOT a unique inversion cause.

## Native finite-strain material control

1124 actual single-tet smallshear patch:fixedbase,noCable/Guide/contact. Same
E250MPa,nu0.3,initialshape10mmtet,totalmass1g,1mNload,dt1ms. Compare stock
corotation and stock compressibleNeoHookean withmu=96153846.15384614Pa,
lambda=144230769.23076922Pa;parameterorder verifiedinstalledNeoHookean.h.
Independent linearBE reference Kxx=mu*length/6,mnode=mass/4. Fouroutputs each,
positionrelativeerror≤5.31e-16,velocityrelativeerror≤3.39e-11,gate0.1%.
PASS_SMALL_SHEAR_ONLY,not finite-strain/material/grasp qualification.

1125 changes ONLY the original1105FEM toNativeNeoHookean withmatchedinitial
E/nu. Geometry,joints,2.5NCable,dt,mass unchanged. Physicalmateriallaw DIFFERENT,
not a numericalrepair or measuredmaterial. Materialoverride isexplicit alongside
inheritedconfigprovenance. Actual3.380s,192outputs;firstinversion480ms,tet504,
minratio−0.173551;thenjournal rejectsnonfiniteNative state andprocessaborts−6.
No validfull0.6stest. Preservelog;rejectpostinversionmotion andcandidate.

1126 probesNeoHookean atvalid300ms;actual2.074s,124outputs,exactq/v/Guidepurity0,
maxFDrelative3.10e-8 (fraction,notpercent). Bettertangent agreement didNOT
preventthelaterinversion1125. Therefore near-consistenttangent alone isnot a
sufficient stabilityrepair. No new100gHolding orproductPASS fromthisbranch.

Reproduce with NEWtags:
`python product_prototype/sofa/b3_deformed_probe.py --tag UNIQUE --sample .3`
`python product_prototype/sofa/b3_native_neo_candidate.py --tag UNIQUE`
Do not rebuildover1120oroverwriteoldRaw. Continue viaRailbackjoint report.
