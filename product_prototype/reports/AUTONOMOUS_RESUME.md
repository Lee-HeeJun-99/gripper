# Autonomous resume — 2026-11-24

LATEST1363 supersedes below. After commit5ab1755,the nextmechanism was actually
screened1362:nominalequalvolume proxrail2.2mm/distal1.533mm loses12of108realguide
footpoints by.466667mm. REJECT beforeNative,not a solverfailure. Noanchor moved.
NextREADY footprint_preserving_proximal_reinforcement;preserve2mmexistingfootprint
or explicitly declare newjointassembly. Useactualproximalrotation1360,reviewold
railaspect/attachmentdata;no stiffness/forcefitting,no arbitrarywidthsweep. Added
volume/mass mustbeexplicit. Latestfinalcommit gitlog;feature5ab1755/7ccf1ea.
1363finalregressionsummary authoritative. Nativeallcompleted,noRUNNING,oldRaw/
SDK/FAILs preserved,no push. ReadCHECKPOINT andupdatedfinitecontactlayerreport.

Historical1361 resume retained below:

LATEST1361 supersedes older notes below. All children completed,noRUNNING.
Finite-contact-layer hypothesis implemented;separate internalbond contacts
failed1337,corrected exactexterior union preserved ALL originalexterior except
24bondinterface faces.1352actual1.2s savedvolumespositive,bond0,layerE/rhoassumed.
1355active sampled layercontacts stillmaterial100mm. At1.2s compositeFz.66122N,
Support.219394N,objectspeed137.286mm/s;not unsupported100gHolding. Fullholdwindow
NOTMEASURED,noLift,newmaterialnotbareSkin. Time/mesh/wholeenergyFAILs unchanged.
Stop uniform-layerthickness/force/offset/angle/terminal sweeps. NextREADY
proximal_shape_retention_hypothesis:1360 shows~90percent finger0projected tipangle
loss0.6to1.2 in0–70mmspan;1358 frozen profilebudget at95mm inadequate. Review
prior railaspect/attachment evidence before a physicalgeometrycandidate;do not
claim intrinsiccurvature or uniquephysicalcause. Existing300partCAD unchanged.
Read B3_FINITE_CONTACT_LAYER_20261124.md. Feature7ccf1ea;latestfinalcommit gitlog.
Recheck gitstatus,actualsummary1361 andqueue beforedoinganything;tags1336–1361
alreadyused,neveroverwrite. Old1242observerbinary preserved,newoptionalphase1344
was built separately. SDK notmodified,nohistoryrewrite,pushorautomaticbackground.

Historical1335 resume retained below:

LATEST supersedes next-task text below:1326–1335 completed this continuation.
Read CHECKPOINT first. Terminal98→90mm candidate executed.6/1.2s without
saved inversion,but1.2sSkin Fz0.6385N lower thanbaseline0.6589N. No new
Holding/LiftPASS.1331 read-only replay ninejournals EXACT,1333 all10sampled
active materialpoints still100mm. Stop terminal-only family. NextREADY
distributed_contact_interface_hypothesis;review finite compliant contact
interface mechanics/material before newNative. Do not rerun existingtags.
No RUNNING children after completion. Feature commits626172e/1f18df4;
latestfinalcommit fromgitlog. Commands:queue script and test_proximal_terminal.py.
See B3_PROXIMAL_TERMINAL_20261124.md for actual commands and source hashes.

Historical1325 resume retained below:

Compare this note with actual Git, queue and results before acting. Never
reuse an existing result tag. All Native children have completed; RUNNING is
empty. Last feature commit:122f4ed (final checkpoint commit:see git log).
Last completed task:root-pitch geometry rejection1323 and local margin1324.
The source mount ALREADY has14deg;extra14deg means28deg and causes18.44mm
initial Skin penetration. No Native trial for this rejected geometry.

100g railback1.5N and2N both FAIL original Holding protocol (1300/1307).
Saved elements remain positive;this does not certify material/physics.
No100g Lift. No real layer-jamming,STEP or hardware qualification.
Same-dt1311 prefix equality is NOT time convergence.
Existing frozen observer reused:1315early442steps55.326s,1319late574steps
78.271s. All9recorded-journal prefixes EXACT0. Unique joins1316/1320 and
material mapping1318/1321 show active Skin contacts at station100mm in
both measured windows;normal Z changes roughly+0.80 to−0.30. Do not call
this distributed Wrapping or unique physical causality.
1322 checked21297 prior immutable Raw/evidence/CAD files,zero mismatches,
7SDK hashes unchanged;original oversized CSV still preserved locally.
1325:96 software tests PASS only;all old physics FAILs remain.

Next READY:`distributed_contact_mechanism_hypothesis`. Review earlier routing
and precurve candidates before selecting a nonduplicate one-variable change.
Use measured distal-tip loading and tight initial root clearance as constraints.
No more force increments or angle/offset sweeps. Required before a new Native
candidate:complete initial Skin/Guide/Wire geometry,consistent rest frames,
clear hypothesis and cost profile. Existing300partCAD is a separate model.
Read B3_ACTIVE_MATERIAL_PROVENANCE and B3_ROOT_PITCH_REJECTION_20261124.md.
Queue script now checks prerequisites and exposes RUNNING,metadata/cost
defaults are explicitly unmeasured. It never starts background work.
No task may loosen .1%time/1%mesh gates. Old raw,scene,manifest immutable.

Resume checks (inspection,not an automatic experiment restart):
```
git status --short
git log -2 --oneline
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/tools/research_queue.py
```
Git repair completed previously;no further rewrite or push. New stageguard
rejects detector.csv AND layer_pairs.csv of ANY size;history check preserves
old smaller journals and checks100MB limit. Old timestamps/verdicts retained.
## Latest continuation1378 — 2026-11-24

Feature d80265b,then actual frozen-observerNative1374(63.210s) andmaterialjoin
1377/1378.9journalsEXACT480outputs;9active samplednormalrows areSkin100mm,
NOT addedbacking.1375analysisassertionFAILretained;1376actualallfingercomparison
mixed −.895,+.800,−1.288°at1.2s. Candidate notselected;fullHoldingNOTMEASURED.
No Nativepending. NextREADY reinforcement_discrete_bending_contract; inspect
sofa/proximal_reinforcement_geometry.py and1364/1368/1370Scene before building
same-root/same-load discrete composite-bending comparison. Do not rerunexisting
grasp or increaseforce/damping. Currentqueue/checkpoint/report authoritative.
Reproduction of newanalysis(useNEWtag):
`python product_prototype/sofa/proximal_reinforcement_compare.py --tag NEW_COMPARE`
`python -m unittest discover -s product_prototype/sofa -p test_contact_layer.py`
