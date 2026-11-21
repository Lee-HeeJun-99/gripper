# Supplier bend limits and Root module redesign

Baseline `c2d42a7`. Original CAD, simulation data and qualification results remain
unchanged. This is a new supplier-compatibility screen, not a retrospective change
to old PASS/FAIL scopes. No purchases or supplier messages sent.

## 855 — primary-source design-input check

Manufacturer pages checked2026-11-21:
[pulley design](https://www.carlstahl-technocables.com/gb/en/products/pulleys/),
[wire catalog](https://www.carlstahl-technocables.com/gb/en/products/wire-ropes-and-strands/stainless-steel-wire-rope/).
Normalized facts are in `config/wire_bend_supplier_v40.json`; this is NOT a saved
HTML/PDF archive or specimen measurement. For uncoated ropes, manufacturer
recommended groove-root diameter ratios are42 for6x7-WSC and25 for6x19-WSC;
cross-section groove radius guidance is0.53 times wire diameter.

Existing catalog candidates SE000005/SE000022 are0.45mm. Derived required root
diameters18.9/11.25mm both exceed actual V39 barrel diameter3.5mm. These two
candidate-wire/current-wheel combinations FAIL the new recommendation screen.
Do not substitute pitch diameter4mm or flange OD6mm for groove-root diameter.
No service life, physical fatigue or exception for R2 is established.
The old CAD0.5mm generic wire is not automatically the0.45mm catalog candidate.

## 856 — actual CAD drop-in hypothesis, rejected

`cad/supplier_root_wheel.py` creates a real revolved U-groove mesh for the6x19
candidate: groove-root radius5.625mm, wire-centre pitch5.85mm, cross-section
groove radius0.2385mm. Width1.8mm, bore1.2mm and flange projection1.25mm are
research CAD choices, not catalog-purchased pulley dimensions.

Only f0_c0 wheel is replaced at its old centre/orientation; all291 other assembly
parts retained in actual Manifold CSG. Saved STL is closed, positive and singlebody.
Intersections: Palm2.995005mm3 and its Root mounted bridge7.763093mm3.
**FAIL_DROP_IN_RETROFIT_INTERFERENCE**. Runtime5.07s (bounded4GiB/420s child).
No physically invalid SOFA assembly was executed. Original wire path also remains
R2, so a larger wheel alone cannot be adopted. No STEP or fabrication PASS.

Commands (robot_ws Python, repository root):

```
python product_prototype/cad/wire_supplier_audit.py --tag product_wire_supplier855
python product_prototype/cad/supplier_root_wheel.py --tag product_supplier_wheel856
```

Next hypothesis: recalculate the actual Root single-corner fillet and wheel centre
at pitchR5.85, with a larger finite fork. Validate this as a separate unmounted
module, then redesign the Palm connection. A clear isolated module must NOT be
reported as a clear full assembly, new mechanical equalizer or Holding PASS.
