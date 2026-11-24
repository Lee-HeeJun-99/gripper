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
Actual source snapshot,source commit,plugin binary hashes,commands,scene and
process logs are stored per result. No SDK change,old evidence overwrite or push.
