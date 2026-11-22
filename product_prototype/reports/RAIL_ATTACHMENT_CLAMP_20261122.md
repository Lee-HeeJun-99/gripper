# Rail attachment / service continuation — 2026-11-22

914 final101softwaretestsPASS(1.991stestbody/2.542sguardedruntime). v50evidence
chain verifies12447priorimmutablehashes0mismatch;23newcases,not23physicalPASS.
No active researchchildren. Latestfeaturecommit recordedinCHECKPOINT aftersave.

Following featured7141b4,not a newsolver. 902actualgeometry audit found Support
vertex-sampled distancesSkin.239388mm,ownRail.04999925mm;CSGempty. SourceV21
support_design explicitlysubtractsexpandedownRail with.05mmbondline gap. No
actualjoint/adhesive/force-transfer certified. SampledistanceNOTwholetrianglegap.

New mechanical hypothesis:unloaded Rootregionx10..14mm Cedgeclamp around actual
.5mmRail/.1mmSkin,finiteweb/innerlip/boss/setscrew andpressurepad. No Rail/Skin
cutting,zero imposedpreload. .05mmbottomclearance/.01mmpadSkin gap remain.
Clampmaterial,thread/preload/friction/slip/filmindentation/fatigueNULL.
Padthickness.03mm in fittedcandidate is a DESIGNproxy,NOT fabrication-approved.
PadCADfootprint1.92mm2 isNOT actualcontactarea/pressure/holdingcapacity.

904 worldCSG savedSupport FAILS watertightness:main2848face body +two2face
zero-volumefragments. FailedSTL/POSTMORTEMpreserved,no triangledeleted.
905 same nominal union evaluatedinRootlocalframe producesvalidsinglebody;
not digitalidentity claim. Actualpad-body collision.01600039mm3 andtiny
screw-padboundary residual retained:FAIL.906 fits padinsideavailableSkinwidth
andaddsactual.01mmunloadedlip/screwgap;3closedSTLs,staticCSGclear,288parts.
These are real designchanges,NOT relaxed collisiontolerance.

907serviceFAIL:sideways extractionSupport hits ownRail andRootwheel.908
physicallyremoves inheritedinboard adhesive-saddle undercut fromoldSupport
before addingedgeclamp (localboundsx8..16,y0..12.05,n>-.55). This creates open
backseat whilekeepingnewinnerlip/Rail/Skin. Staticclear.909sameoutboardservice:
Rail obstruction gone,Rootwheelobstruction remains.910changes ONLY service
direction tooutboard+longitudinalratio1;7sampledassemblypositions clear.
This separates two causes,not a randomoffset/stroke search. Clearance is NOT
continuousCCD/reversibility/producibility. Wiresmustbeunthreaded andactuator
unloaded before screw/pad/keeper removal. Finite exactscrewsweep andassumed
R.8driver path included;realtool/thread/handaccess still unqualified.

911 actual .45mm wire throughsecondRoot/turns/drum vsactual288solids:no
unresolvedobstacles,19.694s. Intendedwheelproximity records allpreserved.
Not fullfinger/allwire/moving/actualfrictionlaw orNativeadoption.
912actualCADreviewpack:meshes/drawings/b3_rail_edge_clamp_v45;9savedSTLs,
288instanceBOM,parameters,actualsections andDESIGNexplodedrecipe. 913 adds
Rootstation12mmactualSkin/Rail/clampsections;visuallyinspected. NoSTEP.
v44keeperpack901 remainsunchanged. Native895 isONLYkeeper894axialcoupon,
NOT newRailclamp908dynamic orforce-transfervalidation.

## Required next qualification (BLOCKED where physicaldata required)

- Select/measure actual material/process,setscrew/thread/pad specification.
- Measure screwtravel/preload;do not infer forcefromunspecifiedtorque/pitch.
- In SingleFingerfixture,measure Support→Rail/Skin displacement/slip under
  knownloads andmoments;instrumentcalibration androotreaction required.
- InspectSkinindentation/permanentcrease andRailbending;cyclefatigue/recovery.
- Compare finiteRailclamp vs explicitlyspecifiedbondedsaddle under SAME material,
  geometry,load andmeasuredwork. Noholding superiority asserted.
- Onlythen define matchedNativejoint/mass/friction model fromNEWinitialstate.
  Remaining4Roots/12turns,movinginterference,time/mesh/100g/Lift/STEP stayopen.

Read-only resume:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_rail_clamp908/summary.json
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m json.tool product_prototype/results/product_rail_service910/summary.json
```
New geometry hypothesis reproducer with NEW tag (not instructions torepeatsuccess):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rail_edge_clamp.py --tag UNIQUE --local-csg --pad-fit --open-foot
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/rail_clamp_service.py --tag UNIQUE_SERVICE --case product_rail_clamp908 --longitudinal-ratio 1
```
Allfailures/rawhashes preserved,SDKunchanged,nopush/purchase. Child4GiB/420s.
Actualruntime/process/source/configfiles accompanyeverycase;peakRSS NOTMEASURED.
