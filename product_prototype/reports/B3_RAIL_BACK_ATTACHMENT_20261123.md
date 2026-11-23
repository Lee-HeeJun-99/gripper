# Three-point Rail-back candidate1127–1135

Newhypothesis:rigidly attaching atSkin/Railinterface canconcentratelocalstrain.
All36attachmentnodes movedfromlocalz0 tocorrespondingRailbottomz−0.5mm.
Oldnodes become free;new36nodes mapped tothesame12Rigidframes. All threepoints
perjoint retained,noncollinearityguarded;not the rejectedrank5two-pointjoint.
FEMgeometry/material/tets/mass/Cableinputs/Guidebodies/Rootconstraints unchanged.
Effectiveforcelever changes withthe attachmentplane. NewSupportconnection is
anUNQUALIFIEDmechanicalassumption;latest300partCAD is NOT updated/approved.

| Case | Native run | Savedminimumtetvolume ratio | Result |
|---|---|---|---|
|1127|0N,0.6s,240steps,2.409s|0.99996840|no savedinversion|
|1128|2.5N,0.6s,240steps,2.610s|0.77644713|no savedinversion|
|1129|sameinputto1s,400steps,3.976s|0.77644713|no savedinversion|
|1130|samephysics,halfdt,800steps,10.948s|0.87522926|no savedinversion|

All completeexit0/noERROR,finite states. Compared to original1105 inversion520ms,
this is a bounded structuralquality improvement,NOT validmaterial/wrapping/
holding certification.1128→1129first240q/v match exactly0;notcheckpointsplice.
MaximumabsoluteSkinprincipalGreenstrain0.250009(base),0.224456(half).
MaterialallowablesNULL,no inventedfailure/pressure/work data.

## Time-pair gate1131 FAIL

400actualcommonoutputs,timealignment≤5.50e-15s,nointerpolation orrelativefloor.
Maximum symmetricrelativeerrors:
Skin displacement140.427%,Rail displacement139.857%,velocity173.556%,
Skinwidth-mean curvaturechange56.732%. AllFAIL0.1%;not adjacent-pairPASS or
fulltimecertification. Curvaturevector is2(unitnext−unitprev)/(lnext+lprev)
onSkin-topwidthmeansections,subtractingreferencecurvature. No contactarea inferred.
AbsoluteL2differencesandworsttimes are in1131summary;do not readL2nodalnorm as
onepointslip. NoQuarterrun justified merely tosearchforPASS.

1132 normalizes ONLYdt/outputpaths:Scenes otherwise exactlyequal. Actualcommon
Cablecommands differ≤1.60e-14N;commandNs/dt equalscommandN exactly inboth.
Thus noobservedinputtiming mismatch orundeclaredScenechange explains thisFAIL.
NativeODE/mapping/constraint cause isnotuniquely identified.

## Geometric-mapping tangent hypothesis1133/1134 REJECTED

InstalledRigidMapping constructor defaultsgeometricStiffness0. Mode1exactblock
canbenonsymmetric;itwasNOTsenttothesymmetricLDLsolver. Mode2explicitly
symmetrizesandNSD-projects.NativeanchorRigidMappingonly changed0→2,sameforces/
mass/geometry/control. NOT anexacttangent claim ornewphysicsimplementation.

Actualbase1133 inverts525ms,218savedoutputs,3.225s;half1134inverts512.5ms,
417outputs,5.926s. BoththenreportSparseLDLzeroDfactorizationandguardstops−9.
Rejectmode2candidate. Postinversionenormousratios/motionarenotperformance.
No complete1stimecomparison forfailedmode2cases;donot fitSolver/tolerance.

## Continuation

No new100gHolding/Lift:single-finger stabilitycandidate stillfails timegate.
Keeporiginal50gfunctionalLiftandalloldFAILs. Variable-stiffnessmaterial/jamming
data remainabsent. Nextboundeddiagnosis should compareactualFEM/guide modal
response andNativeforce-vsimpulse integration onthefirst0–50ms interval,
NOT anotherfullgrasp orrandomdt/force sweep. Usevalidsavedstates from1129/1130
and firstfailuretimes from1131;do not promoteobservedstabilitytomaterialPASS.
If compatibleassembledinertia/tangent API is unavailable,markthatdiagnostic
BLOCKED andprepare a physicallyspecifiedlow-loadGuide/Railcoupon—notCADdetail.

Eightnewsoftware/scoperegressions1135;notphysicalgates. Newtags1136+.
Read-onlyresume:`python -m json.tool product_prototype/results/b3_rail_back_assess1131/summary.json`.
ReproduceonlywithNEWtag+newhypothesis:
`python product_prototype/sofa/b3_rail_back_joint.py --tag UNIQUE --duration 1`.
Allper-casecommands/source/binarySHA/SDK/resourceguardsarepreserved.
