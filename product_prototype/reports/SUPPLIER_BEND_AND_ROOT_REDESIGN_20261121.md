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

## 857–860 — actual module and neighboring parts

857 first module attempt FAIL:fork STL readback not watertight. Failed STLs and
logs remain in `meshes/b3_supplier_root_module_v40`/corresponding result. Inspection
found1438faces in the main solid and a separate2face zero-volume fragment;no
triangle deletion or acceptance tolerance change was used to make it pass.

858 constructs the same nominal fork union with ONE final through-bore instead of
unioning separately bored solids. V41 saves3closed singlebody STLs,0.74s. This is a
different CSG/tessellation representation,not a digital identity claim. Root centre
moves4.885720mm,trim4.570521mm,turn76deg. Local solid pairs and conservative finite
wire-vs-fork/pin probes have no reported intersections. Pin remains an unretained
proxy and fork is UNMOUNTED. All other18turn wheels remain undersized for these
catalog wire candidates. No Native scene was adopted.

859 checks module vs ALL292 original named parts,3.98s. New wheel overlaps first
Eyelet0.428231mm3 and first Support0.550588mm3:FAIL. Old replaceable Root wheel/pin
overlaps and integral mount overlaps are separately recorded,not silently hidden.

860 changes only first Eyelet+Support position by2mm along the original straight
incoming wire direction,keeping finite shape and volume. New translation is
(-0.483844,0,-1.940591)mm,not a random outboard-offset/stroke search. Actual module
neighbor CSG then reports no unchanged-neighbor obstacles,4.03s. StillBLOCKED:
old integral bridge interferes with new wheel/fork/pin and must be physically
rebuilt. Shifted-guide-vs-all-other-parts,attachment,6modules/motion/retention and
strength remain unqualified. An isolated clear module is not an assemblyPASS.

```
python product_prototype/cad/supplier_root_module.py --tag product_supplier_root858 --name b3_supplier_root_module_v41
python product_prototype/cad/supplier_module_neighbors.py --tag product_supplier_neighbors859 --candidate b3_supplier_root_module_v41
python product_prototype/cad/supplier_module_neighbors.py --tag product_supplier_shift860 --candidate b3_supplier_root_module_v41 --guide-shift-mm 2
```

Next:reconstruct the integral Root mount from the existing bolted compact bridge
plus the new fork,not by deleting its collision geometry. Preserve the shifted
finite guide/support and test all changed parts against their actual neighbors.
