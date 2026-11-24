# B3 active material/contact provenance1314+

No observer reimplementation or new build. Existing frozen1242 binary and
compiledsourceSHA checked,installedSDK dependencies verified byldd. B3 Scene
uses actual `@nativeNarrow` link.1314wrong-name producerassertion failed
beforeNative,retained;1315uses actualexistinglink. Window≤5ms,read-only
BuildConstraintSystemEnd previousclock. NoSDK/Solver edits.

1315actual442steps1.105s55.326s under120schildforecast111.6s,4GiB.
9journals×442prefix:allnumericdifferencesEXACT0 andallrecordfieldsequal
to1298.116actualdetectorfeatures,870childJentries.1316existingjoincode
linksall114normalrowsuniquely bymodel/statepaths,points andsignedJnormal
atidentitytol1e-12. Noassumeddetectororder orpoint-countarea.

1317firstmapsactiveSkinPointrows only;nonpointrows explicitlyunmapped.
1318addsexplicitSceneLineedgeindices+SubsetMapping,verifiedatprevious
acceptedparentcoordinates. SixactiveSkincontacts in2sampledframes:
finger2Point(parent245),fingers0/1Line(parent245/248). All materialstation
100mm,topSkinz0.1mm. Previouspointidentityerror≤6.51e-19m;normalimpulse
pullbackerror0Ns. Nextacceptedpointdifference0.093–0.135mm,so silently
joiningdetector toendstatewouldNOTsatisfystrictAPIidentity. Clockjoinuses
actualstoredindexsuccessor,notstep*dt orroundedtime.

This window showsloadatdistaltip,notdistributedWrapping orcontactarea.
BothPointandLineareactualSkincontacts;Guide/RailforcesnotreclassifiedSkin.
No physical/time/mesh/graspPASSfromtheseprovenancechecks.

Lateprobe1319uses SAME frozenobserver atprevious1.4249–1.4298s,574steps.
Full1298profileforecasts144.7s,180schildlimitchosenbeforelaunch (below
global420s),4GiB. Checkactualcompletionandfreshjoinbefore interpreting.
No relaxationofphysicsgates. Latebodymovementandnormalsremain diagnostic,
not unique evidence thatsolver ordesignalone causesloss.

Completed1319actual78.271s:9journals×574prefixallfieldsEXACT0.102features,
726childJentries.1320uniquelyjoins100normalrows.1321mapsall8activeSkin
Point/Linerows in2lateframes tomaterialstation100mm,parent245/248. Normal
onobjectz is−0.3403…−0.2923 instead of early≈+0.79…+0.80. Both measured
windows carryloadatdistalendpoint,notproven distributedWrapping. Previous
parentgeometryerror≤1.39e-17m andnormalimpulseidentityerror0. Nextaccepted
point differs22–47µm;clockalignmentmustremainexplicit. No trial rerun merely
to turn FAIL into PASS. These areobservations duringunqualifiedcontactdynamics,
not a uniquely identifiedphysicalcauseorrealhardwaremeasurement.

Reproduce ONLYwithNEWtags,Pythonrobot_ws:
```
product_prototype/sofa/b3_existing_provenance_probe.py --tag NEW_EARLY
product_prototype/sofa/contact_provenance_assess.py --source NEW_EARLY --tag NEW_JOIN --lines 3
product_prototype/sofa/b3_active_material_point.py --source NEW_EARLY --join NEW_JOIN --tag NEW_MATERIAL
```
`--late`selectsboundsabove. Scriptsnevercheckpoint-restoreoralterstates.
ExistingoldRaw/CAD/manifests/SourceCommitfields remainunchanged.
