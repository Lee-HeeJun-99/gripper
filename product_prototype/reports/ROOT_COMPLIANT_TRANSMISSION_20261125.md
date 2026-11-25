# Root compliant transmission — Campaign1850–1856

Alternative mechanism after rigid point-loop1844FAIL: use **physical elastic
deformation**, not state projection or a custom ODE, to supply rotor rotation.
Baseline source commitd55b386; exact per-case producer snapshots, scenes,
commands and logs are preserved. All new children capped4GiB/60s.

## Actual measurements and limits

|Case|Actual result|Verdict and scope|
|---|---|---|
|1850|3/5/9node circular BeamFEM,3mm length,r0.25mm,E250MPa,nu0.3. Pure moment1e-7Nm: angle0.000391139rad,tip0.586709um; mesh fraction4.407e-9|PASS small static reference/mesh only|
|1851|Same shaft, angle0.412800551rad required by1843four-mm linkage. Moment1.05538e-4Nm; max reference fraction0.00534665, mesh0.00490402|PASS1percent static comparison; reference outer bending strain3.4400percent, actual allowable NOT MEASURED|
|1852|Side-entry cantilever overlaps rotor by0.448708mm3 outside explicit0.7mm bond domain. Vertical axial shaft has zero positive hub-envelope intersection|REJECT side-entry drop-in. Vertical contact-only hub interface not qualified bond/retention|
|1853|Actual Native pure axial torsion,3/5/9nodes: angle0.412800551rad under8.118309e-5Nm; max relative angle error6.724e-16; centreline motion0|PASS static torsion reference only; reference shear3.4400percent, allowable NULL|
|1854|Three attempts fail RigidMapping factory creation because RequiredPlugin came after Node|FAIL retained; no valid physical result|
|1855|Plugin-order-only correction. Input1e-5N/output opposing0.5e-5N dead loads. Actual9node input moves-3.055774736um,output+2.185490077um; maximum reference fraction6.239e-8, mesh2.435e-9; last-state change0|PASS static mixed bending/torsion force-inversion reference/mesh only|
|1856|Two actual placements of1855: vertical shaft and oblique whole-frame rotation. Back-rotated all3saved states: position<=5.631e-19m,ports<=3.470e-18m,orientation<=4.441e-16rad|PASS static frame contract at unchanged1e-12 gate|

Each successful child ran3static steps, normally/noERROR, roughly0.10–0.17s.
BeamFEMForceField is installed Native circular Rigid3 implementation, not a
new user forcefield. Installed source sets shear areas tozero: reference uses
Euler bending and GJ/L torsion; not measured PET. Full root is fixed.
No contact, CableConstraint, dynamic mass or prescribed deformed state.
1855ports are rigid mapped loads, not a fully manufactured rotor assembly.

1851record's legacy status label says SMALL; outer status and configuration
explicitly identify finite angle. Historical result is not edited.
1854failure is not retroactively relabelled by1855success.

Energy, root reaction, actual material strength/fatigue, retention and bond
strength are NULL/NOT MEASURED. Pure reference strain is not a material
acceptance criterion. This **does not** resolve B3 thin-Tetra mesh/timeFAIL,
Native wire contact, supported output spine, Guide interference or100ggrasp.
Micro-load coupon is not proof of1.5N tendon capability; next check is actual
load scaling and output-interface feasibility before any Finger integration.

## Provenance / reproduction

SDK26.06.00; frozen journal binary
`cad/build_default_control332/libReGripProductSequence.so` SHA256
`3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0`.
Installed BeamFEMForceField.inl SHA256
`b594ef09dde3a658ab7d84f491cde64c12fd5f46d07856fc05038cff2dfb96b8`.
1857append-only manifest indexes154completed files, including local25CSV.
1849audit preserves original102task entries and2602selectedmanifestrecords.

Run from repository with `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`.
Actual wrappers invoked (use NEW tags to reproduce, never existing folders):

```sh
python product_prototype/sofa/root_flexure_coupon.py --tag root_flexure1850
python product_prototype/sofa/root_flexure_coupon.py --tag root_flexure_operating1851 --operating-angle
python product_prototype/cad/flexure_rotor_interface_screen.py --tag flexure_interface1852
python product_prototype/sofa/root_torsion_coupon.py --tag root_torsion1853
python product_prototype/sofa/compliant_rotor_static_coupon.py --tag compliant_rotor1855
python product_prototype/sofa/compliant_rotor_frame_coupon.py --tag compliant_frame1856
```

1854must use its immutable producer snapshot, not corrected current source.
Every child command JSON contains actual runSofa command and paths. All Raw
stays local, summary/scenes/producer/manifests committed without CSV. No SDK
edit, state correction, new damping, tolerance change, history rewrite or push.
