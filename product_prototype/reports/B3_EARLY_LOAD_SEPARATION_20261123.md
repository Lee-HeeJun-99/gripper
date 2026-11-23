# Early transient and gravity control1156–1158

Continued after rejected footprint1155, not another force/dt sweep.
1156 reads saved1129/1130 no-contact trajectories. First common2.5ms:
Skin difference17.6253%,absolute L2 difference18.0859µm; largest node
difference3.79964µm at distal Rail node240. Minimum volume ratios near
0.999997; max principal Green strain≈2.2e-5. Initial Cable command only
3.10161e-6N. Thus neither contact nor inverted elements are necessary for
the early time-pair error. Relative threshold is unchanged; absolute error
is retained, not hidden by a denominator floor.

New hypothesis: abrupt gravity loading from rest contributes strongly to
this early response; Cable correction may not dominate its first sample.
Reused zero-Cable base1127 unchanged. Executed ONLY missing zero-Cable half
control1157,480steps/0.6s,4.714s runtime,4GiB/120s guard. Same Native SDK,
restshape/mass/material/Guide/root/gravity; only dt and declared zero actuator
input differ from driven cases. No saved inversion,no ERROR,minvolume0.9999637.
Regression checks full serialized Scene identity after normalizing ONLY dt,
maximumForceN and journal destination.

1158 controlled nonlinear trajectory differences at2.5ms:

- Driven base/half Skin L2 difference18.0859µm.
- Zero-Cable base/half difference18.1017µm.
- Difference of actuator-induced trajectory increments0.0162719µm.
- Zero-Cable base displacement L2 norm102.638µm.

At100ms, driven/zero pair differences54.9451/54.6517µm; difference of input
increments1.31614µm. These are trajectory contrasts, NOT a linear
superposition assumption, energy balance or unique proof of a Native defect.
The original early relative failure largely persists without Cable input.
Do not attribute all of it to Cable impulse timing. Later nonlinear failures
and inversion remain separate. No repair or numerical/physical PASS claimed.

Source snapshots, original hashes and actual command/runtime in Raw. Reproduce
with fresh tags, preserving all old cases:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_rail_back_joint.py --tag NEW_ZERO_HALF --zero --duration .6 --dt .00125
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_early_divergence.py --tag NEW_EARLY_AUDIT
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/sofa/b3_load_separation.py --tag NEW_LOAD_AUDIT
```

Next hypothesis: compare actual zero-input first-step response with independently
assembled discrete gravity RHS/A (including projected root and mapped rigid
gravity moments), using previous-state mass/mapping. This separates expected
startup integration error from an assembly/force defect. Do not ramp gravity
or pre-equilibrate silently to make the existing gate pass. Full100g remains
blocked for this joint candidate; existing50g functional results preserved.
