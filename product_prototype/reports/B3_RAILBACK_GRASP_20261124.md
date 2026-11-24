# Rail-back100g grasp and bounded force sensitivity1297–1312

New Native candidates,not reused old50g success. R30/100g,gravity9.81,
mu0.3 research assumptions. Change36rank6 mappednodes/finger frominterface
toRailback as single-finger1129,retaining Skin/Rail/Cable/Guide physics.
Ideal joint support remains not CAD/fabrication-qualified. AllRaw preserved.

1297 .25s pilot9.737s;conservative5xcontact forecast389.48s for2s.
1298 actual2s134.461s,800savedstates/finger,minvolume0.98517,finite;
no ERROR/unusedattribute.1300 original100g protocol FAIL:
Slip40.0282mm,speed0.06210mm/s,supportgap0.2mm,supportforce1.06158N;
SkinmeanFz−0.080216N,Rail/Guide0. Partitionerror8.67e-19Ns/Nms.
Hold solveriterations reach1001. Element validity is NOT grasp success.

1301 frozen earlycontact minnormal1.01209N vsmeasured0.77215N motivates ONE
2N input sensitivity at same joint,not an automatic tension sweep or motor
specification.1302 .25s pilot12.561s;its initial2sforecast502.43s exceeded
420schildbudget,so that full launch was NOT made. Instead1303 actual1.2s
contact profile65.036s followed .25s-based301.46s forecast.1305 canonical
Scenes identical exceptforce/outputpaths;early1.1s SkinFz0.75126→0.97699N,
optimisticbound0.75432→0.97975N. This partial run is NOT HoldingPASS.
1302 preflight's inherited hypothesis text still says1.5N;explicitchanges,
Scene and actualcommand contain2N. Preserved;fixed producer for1303/1306.

Contact-inclusive measured1.2s profile allows transparent2xlatecost margin:
65.036*(2/1.2)*2=216.79s forecast.420schildlimit unchanged,no exception.
1306 actual2s91.728s,all800/fingerfinite,minvolume0.93756,noinversion.
1307 originalprotocol FAIL:Slip40.39597mm,speed35.7558mm/s,gap0.199929mm,
supportmax1.69730N;meanSkinFz−0.39950N,RailFz−0.18158N,Guide0,
SupportFz1.56122N. Solver reaches1001. No physical or functionalPASS.
Do not continue force increments or run100gLift from thesefailed candidates.

1309 actualactiveSkin normal upperbound becomes nonpositive at1.425s for
1.5N and1.400s for2N,with231/241postwithdrawsamples. Within those active
directions,additional normal force cannot create upward support atmu.3.
This is not proof about future contact sets or unique failure causality:
object motion,contact transitions and solverlimits remain coupled.

1310 initial prefixparser issued NumPy suffix-parse warning,retained.
1311 strictcomplete-token parser compares9journals×480outputs:allnumeric
differencesEXACT0,textfields identical. Same dt prefix reproducibility,
NOT time convergence. No state reset/clock shift/after-the-fact adjustment.
1312actual topSkin width-mean centreline at1.1/1.4/1.8s,all3fingers;turning
proxy is NOT intrinsic shellcurvature,contactarea or WrappingPASS. Actual
motion/force plot1304 labels both1.5N comparisonsFAIL;not concept geometry.

## Preservation and reproduction

Eachcasepreflight stores sourcecommit/hash,actual command,Scene and installed
pluginbinary SHA;SDK v26.06.00 unchanged. Existing B3/sourceRaw/CAD/manifest
and oldPASS/FAIL remainunchanged. Detectorcsvlocalonly,notGitadded. Code,
Nativejournals,independentanalyses and failuremetadata retained separately.
Wholeenergy,contactpressure,realmaterials/joints/jamming NOTMEASURED.

Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`,NEWuniquetags only:
```
product_prototype/sofa/b3_railback_grasp_candidate.py --tag NEW_PILOT
product_prototype/sofa/b3_railback_grasp_candidate.py --tag NEW_FULL --duration 2 --pilot NEW_PILOT
product_prototype/sofa/b3_railback_grasp_assess.py --tag NEW_ASSESS --case NEW_FULL
```
Do not repeat unchangedfailed trial;above commands document reproducibility,
not a recommended rerun. Prefix/history/centreline producers explicitly use
the recordedcases;inspect before changinginputs. Original protocolfrom1059
preserved andhashed;Slip2mm,speed5mm/s,gap5mm,support1e-5N unchanged.

Next mechanical task:sustain lower-hemisphere contact during withdrawal.
First obtain unique active detector-point/response attribution;current
detector journal lacks materialelement/normal IDs. Do not infer a specific
Skin materialpoint from rowcount orJacobianforce alone. New bounded read-only
observer needs q/v/impulseprefixpurity before any furtherfullgrasp trial.
