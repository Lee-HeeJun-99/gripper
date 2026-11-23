# Sampled previous-state matrix and impulse1142–1149

Startingc7cd39d,clean. Newread-onlydiagnosticbuild1142 usesinstalledSDKonly,
4GiB/120s,actual6.191s. No newForceField/ODE/constraintlaw. FrozenProbe.cpp,
CMakeCache,ldd,binarySHApreserved;build_step_probe1142/libReGripStepProbe.so
SHA500640ecd9c00c97b87428f38d1ada902a54bdc82d85df5ae4972ab524fd57f0.

AnimateBeginrecordsactualPREVIOUSacceptedq/v/Guideframes andprivatelyqueries
NativeFEMforce/Katthatq. BuildConstraintSystemEndandSolveConstraintSystemEnd
recordactual/freeq/v,NativeparentJandlambda. AnimateEndrecordsacceptedstate
andactualeffectiveAfromtheSAMEstep. No invalidcheckpointorstatewrite.

ActualsampledNative1143(50ms,24outputs),1144(300ms,124outputs),1147(halfdt50ms,
44outputs)complete0.606/1.811/0.840s,noERROR. Allq/v/mappedGuideprefixerrors
EXACT0vsunchanged1129/1130. IntegrateEndeventwasnotobserved;no fabricatedevent.
Previousclock→end:47.5→50ms,297.5→300ms,48.75→50ms. Intermediatebuild/solve
clockremainsbeginclock;theirorderingisrecorded,notinferredfromtimestampsalone.

1145/1146/1149 independentlyreconstructAfrompreviousG,mass,Rayleighandprevious
NativeFEMK. TT/TR/RT/RRrelativeerrors≤1.739e-15. This extendsinitialidentity
toTHESEdeformedsamples;notfullpathassembly,exactnonlineartangent,orenergyPASS.

Sameactualstepconstraintcorrection:
`A_free Δv = (Jᵀ lambda)_free`,usingactualNativebuildJandendmultipliers.
Guide translation/rotation/freeVec3velocitycorrectionrelativeerrors≤4.80e-9
acrossallthreecases,gate0.1%. Actuallambda=T*dt exactly. At50ms,T=.0214N,
base lambda5.35e-5Ns/cable,half2.675e-5Ns. At300ms,T1.7064N,lambda.004266Ns.
Do notcallthesevaluesN. No unknownforces/reaction/workinvented.

Actualeventordering:atBuildEndactualvelocitiesstillprevious;freeVelocitycontains
free-motionprediction. AtSolveEndmultipliershaveupdatedbutactualvelocityhas
NOTchanged. AtAnimateEndactualvelocityequalsfreeVelocity+constraintcorrection.
At50msGuidetranslationpositioncorrectionalsoequalsdt*Δv within5.12e-18m.
Largeopposingfree/correctiontermsarenotbythemselvesproofofinstabilitycause.

FournewscopechecksPASS. ExistingtimeFAILs,100gFAILs,mesh/energy/material/joint
unqualificationunchanged. NEXTactualone-stepinputpausecontrast toseparate
free-motionfromCablecorrectionWITHOUTq/vmanipulation. Pauseisadeclarednew
inputexperiment,NOTanobserverpuritytest orperformancecandidate. Continue
immediatelyafterfeaturecommit;do notrepeatfullgrasp/dt/force/frictionsweep.

Read-onlycommands:
`python -m json.tool product_prototype/results/b3_step_assess1146/summary.json`
Reproduction(newtag/newhypothesisonly):
`python product_prototype/sofa/b3_step_probe.py --tag UNIQUE --sample .3`
