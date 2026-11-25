# Composite acceleration API and direct tendon continuation

Start HEAD f804e4f. No SDK changes or new Native execution in these cycles.

1811 BLOCKED (current mapping graph only): installed Mapping/Multi2Mapping
declare acceleration callbacks including dJ*v, but their default overload is
empty. Selected RigidMapping/ArticulatedSystemMapping files do not override it.
Actual source locations/hashes are in composite_api1811/summary.json. This is
not proof that every SOFA plugin lacks an alternative. Reuses actual1806/1807
finite-velocity failures and1808 independent reference, not another flag replay.

1812 REJECTED: a different direct root-to-terminal tensile mechanism was built
as six finite radius0.25mm spans, without intermediate guides. Initial sphere
gap reaches -5.294722mm; actual material-cell CSG gives48 positive intersections.
Own terminal last0.5mm is explicitly a hypothetical bond domain. Curved/rerouted
wires are not ruled out; such candidates need independently qualified routing
and attachments. No full Native expansion is justified by this failed geometry.

Reproduce into NEW tags only:

```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/native_composite_acceleration_audit.py --tag NEW_API_TAG
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/direct_tendon_span_screen.py --tag NEW_SPAN_TAG
```

Original Raw/SDK/verdicts preserved. Next actual work: matched1586/1741
per-Finger object impulse inventory (1813), not a repeated grasp or force scan.
