# P1 integral ground frame — cycle55 engineering record

Primary product: **primaryP1_integral55e**,77 actual parts, separate from failed AO. This is the continuation of the same P1 Motor→Drum→Tendon→Finger→Root→Ground specimen. Official RevAA baseline is unchanged. No Stage3 or hardware measurement.

## Actual design and architecture decision

The unnecessary detachable ground stack was replaced by one actual continuous solid containing Root/Motor frame,9mm roof,four10mm-thick outboard arms,columns and base.47 former fixed-interface fasteners and four separate merged body IDs disappear from the77-part BOM. **76 retained STEP files are byte-identical**. Source-reviewed Pololu Motor/hub and retained lower-through hardware are unchanged; no new supplier part/rating or minimum is invented. Replaceable Finger/Root and Motor cap remain separate. PET distal sliding and future3Finger/jamming attachment intent are retained; final same-revision3Finger is not built or certified.

The new roof includes36×46mm open Motor access withR2 dogbone tool reliefs and two4mm RF driver holes. Root and Motor physical contact faces retain their original areas/positions. This is one-billet6061 design intent, **not a welded/bonded/rigid-tied stack**. It explicitly changes the prior mixedsteelGroundPlate/aluminum fixture intent.232×140×183mm bounding stock,setup/long-tool access,corner processes/tolerances,material minimum/stock condition and allowable stress remain unqualified.

Choice A: retain the old4mount18bodycontact search. Prior finite108DOF unit-load FAILs are preserved; they do not prove the entire product impossible. Choice B: integrate only receiver/stand (111parts); new actual CAD clears after correcting240mm³ TEST_BASE interference,but staged installation and retained upper-stack tools still fail. Choice C: integrate the fixed stack (77parts);55c passes current assembly but inherits0.01mm obsolete interface seams and fails mesh quality. Final55e replaces that obsolete upper stack by a simpler roof/arms. All trial solids/results/logs are preserved,not retagged as final evidence.

## Actual CAD, assembly and interfaces

Canonical CAD: `cad/exports/primaryP1_integral55e/summary.json`; STEP/STL,BOM,full ASSEMBLY and identity ledger are new files. All77 solids and assembly count independently verified. 207 nominal pair queries (four lower threaded BRep pairs excluded and unqualified),88 ordered finite assembly poses/657 queries clear. Fresh Finger lift/slide/lower,Motor/drive/cap installation,Root drivers and five prescribed0/15/30/45/60degree straight-wire positions clear. Finite samples are not complete CCD/thread tightening/cable threading or manufacturing certification.

Actual new-roof full continuous Motor and cap access prisms have zero blocked volume. Nominal clearances: drive≈1mm,cap0.6mm,RF driver0.5mm;new roof versus full Finger-stage envelope26mm. These continuous bounds apply to the newly constructed roof/arms,not all inherited body motion. Whole-module placement onto the reference host plate is checked at six finite heights. Lower-through thread/pin-forming/retention and ultimate host remain separate physical conditions.

Preserved actual interface areas: Root seat516.765949207mm²,Root wall159.64mm²,Motor bottom80mm²,each Motor side60mm²,reference foot31989.686822229mm². This is geometry/function continuity,not pressure/capacity proof.

## Physical loads and full-piece numerical results

The freshly recomputed geometry gives24.067120906mm prescribed stroke and positive minimum17.782638500mm/rad.183 explicitly conditional3Finger friction scenarios (μ0.2/0.4/0.8,100g weight,typical scalar curvature stiffness) give0.928497549..4.503698462N tension;45 ideal current-guideline screens FAIL. This is not a finite contact/Finger/support operating solution;stall is not protected peak. No motor substitution/optimization or actual protection is claimed.

The actual entire new integral piece was meshed at maxh8/5/3mm with P1 tets and the unchanged linear elastic law,typical68900MPa/ν0.33/density2700kg/m³. It receives a prescribed **100g downward vertical test at the actual Root seat plus its own distributed gravity**,not100g grasp/tendon demand. Given positive affine normal foot traction balances its free body. There are zero physical fixed DOFs;six algebraic rigid gauges are removed/restored only for solving. This is a normal-Neumann transmission reference,not solved host-plate contact/complementarity or a whole-product equilibrium.

Each final field passes original force/moment/residual/quality/static-work checks. Independent element assembly checks every DOF and strain energy;rigid motion invariance,perturbed displacement and wrong-load-sign controls pass. Finest h3 strain energy0.00202235436019Nmm,max restored-gauge displacement0.000952108494043mm,rawpeak VM0.361577946288MPa. These values are **not strength certification**. Original mesh1% FAIL:8→5energy34.5245%,8→3energy57.3373%,5→3energy16.9581%;objective Root motion33.6442/58.8946/19.4211%. All pairs,including coarse-to-finest,are reported. A convergent bending discretization and unchanged physical sourcefunctional are required before interpreting stiffness/strength. Time0.1% and global energy remain incomplete;static energy is not global closure.

Conditional actual-CAD mass: integralpiece2.473487078kg,module excludingreferenceplate2.648782526kg,totalincludingplate6.153906411kg. Source nominal Motor9.5g/hub2.8g avoid solid-metal proxy mass;COM/inertias remain CAD proxies and physical mass gate is not passed. Material change is explicit,not fitted density or a performance reward.

## Failures and qualification

Failure archive: `validation/integrated/primary_cycle55_record/failures/summary.json`. First240mm³ CAD collision,111part assembly failures,first section-gauge mismatch,post-compute stdout serialization error,55c direct factorization memory failure,55c quality FAIL,scalar common-volume identity failure and render ABI import failure are retained. Topological parent-minus-new empty-solid checks resolved the numerical containment question before55e intentionally simplified obsolete material. Existing AMD-CG/Neumann model was reused without a larger limit;renderer alone used the already compatible environment. No install/SDK or trusted-source change.

Newly qualified system gates: **0**. All22 remain **UNQUALIFIED**,operating product equilibria0,hardwareNOT_MEASURED,independent releaseINTEGRATED_NOT_QUALIFIED. Current full supported physical load field,material/process minima,Root/Motor/retained lower-through contact and capacity,protection,mesh1%/time0.1%/globalenergy/final3Finger remain. No failed trial is assigned a performance benefit or PASS.

## Concrete next mechanism

`goal_primary_integral55e_convergent_continuum_and_fresh_root_motor_operating_ports`

Continue SAME ONE77partprimaryP1_integral55e,canonicalSTEP/BOM/hashes;no return to AO or removed47groundstackfasteners. FIRST establish a convergent fullactualintegralpiece bending response using existingtetrahedralelasticity: predeclare a P2/order contrast or justifiedlocalrefinement with EXACTsame Rootuniform100gverticaltest/ownweight/affinefootNeumannfunctional and original1percentallpairs,not a changedpressure/source/coupon or tolerance. h8/5/3P1energy differences34.5245/57.3373/16.9581percent andobjectiveRootmotion33.6442/58.8946/19.4211percent are FAIL;do notinfer solecause ortransferstiffness. KeepallphysicalDOFs/freebodyforce/moment andindependentvirtualwork;algebraicgaugesarenot hostfixation. Inparallelplanning derivefresh77part100gcontact/friction/finiteFingerdeflectionRoot/Motorports andprotectedpeak separately;current24.067mmstroke/.9285..4.5037Ntensionareconditionalprescribedcurvaturebounds,45currentscreenFAIL. RecomputeactualRoot/Motorcontactforcesonpreservedfaces,notoldtractions;fourretainedBENCH_THROUGH/plate/ultimatehostcontacts,pin/thread/source/materialminima andONEbillettoolsetup/ligament/notchstrength remain independent. No uniform-rootload claim asrealgrasp. Finishactualsame-revision3Finger before release;mesh1percent/time.1percent/globalenergy/all22unchanged;NoStage3.

23 analysis children,471.551079s summedactual child time;all reaped,timeout0/STOP0.4GiB/420s per analysis retained. All source pins and8595 original untracked file hashes unchanged. No manager/security/guard/gate/criteria edits,recursive launch,subagent,git add/commit,push,purchase or hardware action. Supervisor saves only exact listed verified bytes.
