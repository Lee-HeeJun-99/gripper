# B3 proximal cable terminal — bounded topology contrast

Review: the earlier distal-profile,sector-route and precurvature trials261–375
already cover offset/curvature changes.1321 identifies active materialstation100mm
loading;1323 rejects extra root pitch. This candidate changes ONE actuation
topology: each cable ends at existing90mm guide instead of98mm. Material contact
station100mm is NOT the same quantity as guide station98mm.

All six98mm guide bodies,masses,mappings and collision models remain present.
Only six CableConstraint index lists lose their last index. An inverse-edit XML
comparison equals1298 exactly,including initial FEM,all collision and solver
settings. Initial wire is a subset of the old path;no new initial segment is
introduced. Dynamic clearance and a manufacturable90mm wire anchor are NOT
QUALIFIED. Baseline config is copied as provenance;scene indices and preflight
describe the intentional changed terminal,not a shared production CAD config.
This is an ideal mechanism hypothesis,not adoption into300partCAD.

1326:actual Native0.6s,240outputs/finger,42.2453s,4GiB/180s child. Minimum saved
signed volume ratio0.9881299;no errors/inversions observed.1327 compares actual
common0.6s states with1298:Skin Fz0.689683→0.679044N;root-tip tangent angle
roughly46.5–47.0→43.8–44.2deg. Supporting normals remain upward,but no performance
improvement or distributed Wrapping follows. This window is before unsupported
Holding. No time/mesh/energy or hardware qualification.

1328 extends the same topology to1.2s,using measured1326 cost with2x safety
factor:forecast168.981s versus180s bound. This tests contact/support-withdrawal
entry,NOT the1.6–2s Holding protocol. Result recorded after actual completion.

Commands (do not reuse existing tags):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_proximal_terminal.py --tag b3_proximal_terminal1326
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_terminal_assess.py --tag b3_proximal_terminal_assess1327
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_proximal_terminal.py --tag b3_proximal_terminal1328 --duration 1.2 --pilot b3_proximal_terminal1326
```
## Completed follow-up

1328 completed1.2s/480outputs in98.5207s;minimum saved volume ratio0.9880716.
1330 actual common1.2s Skin Fz:baseline0.658925N,candidate0.638500N,below
100g weight0.981N. Active-normal nz0.5382..0.5718;5rows are NOT contactarea.
This pre-Hold point alone is not a formal Holding FAIL,but fails the proposed
early support-force improvement. Do not extend this candidate blindly to full
Holding or increase force/shift terminal repeatedly.

1329 independent constant-tension initial length gradient matches centralFD
within8.79e-11. Ideal force at98mm guide changes1.5→0N. This proves a changed
force topology,not actual Native impulse or dynamic causal sufficiency.
Next diagnostic:identify actual active materialstations in1328 with the frozen
provenance observer before deciding whether contact distribution changed.
The force/centerline proxy alone cannot establish distributed Skin contact.
Actual hardware90mm anchor strength and wire replacement remainNOTMEASURED.

1331 reuses frozen1242 observer,no rebuild,1.2s in79.8036s. All nine480row
journals exactly equal1328.1332 uniquely matches104normalrows.1333 maps all10
active Point/Line Skin rows in sampled previous-times1.195/1.1975 to material
station100mm;none unmapped. Object normal impulse error0;previous-parent error
at most3.47e-18m. Thus terminal relocation did NOT produce distributed active
material contact in these windows. Stop terminal-position-only family;do not
infer unseen whole-time contact distribution or a unique physical cause.
NextREADY reviews a finite compliant contact interface rather than another
force/offset/angle/terminal sweep. Requires explicit material assumptions and
finite initial-clearance checks;no hypothetical pad-performance claim.

Actual source snapshot,source commit,plugin binary hashes,commands,scene and
process logs are stored per result. No SDK change,old evidence overwrite or push.
