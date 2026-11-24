# New mechanisms after1713 (start05252d7)

Original102 tasks reviewed: geometry/force/timing sweeps, mesh symmetry,
rail reinforcement, finite collision representations and blocked sliding
contract do not establish a same-finger closed transverse frame. Native
DiagonalMass bridge136–158 initialization failure is preserved; a supported
indexed UniformMass assembly is a separately testable path, not assumed valid.

##1714–1718: measured finite-envelope safety clutch

New mechanism: actual hardware vertices in accepted Rigid3 frames measure
signed distance to own120degree sector planes. A latching cable clutch cuts
ONLY that finger's next sequence maximumForceN at existing contactDistance/2
(0.1mm). All geometry/collisions and actual q/v remain native. No threshold
scan or material/solver adjustment. This is ideal sensing/instantaneous
clutch research, not qualified sensor/actuator hardware.

1714 passive4steps:1.241s, exact q/v/object impulse purity0; independent
Python sensor error1.952e-18m. Commitbc7d2f3.1716 completed integrity index.
1715 active480steps/1.2s:83.428s, minimum saved FEM ratio0.989512.
Finger0 clutch at0.465s; actual first zero force0.4675s; other two remain1.5N.
1718 next-step command error2.22045e-16N; pre-intervention q/v difference0.
All cross-finger nonzero response rows0, but loss of symmetric approach:
at1.2s object horizontal displacement8.34326mm, speed128.0478mm/s.
Candidate REJECTED FOR EXPANSION; formal1.6–2.0s Holding was NOT RUN.
This does not prove every feedback/clutch mechanism impossible. No full
trial justified without a different mechanism, no clutch-threshold scan.

1717 assessor assertion correctly rejected an incorrect cubic ramp reference;
frozen Native sequence uses quintic.1718 uses actual same-binary baseline
command history. No Native data changed or reexecuted for this correction.

Reproduction (use NEW tags; existing paths immutable):
```
cmake -S product_prototype/sofa/native_sector_clutch -B product_prototype/cad/build_sector_clutch1714 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
cmake --build product_prototype/cad/build_sector_clutch1714 -j2
python product_prototype/sofa/sector_clutch_native.py --tag UNIQUE_PASSIVE
python product_prototype/sofa/sector_clutch_native.py --tag UNIQUE_ACTIVE --enabled --duration 1.2 --control UNIQUE_PASSIVE
python product_prototype/sofa/sector_clutch_assess.py --case UNIQUE_ACTIVE --tag UNIQUE_ASSESS
```

Exact scene/binary/source hashes and actual invocation are in each case's
intervention/preflight/process/command files; all Raw local. Existing time,
mesh, contact-normal and finite-wire failures remain. UNBRACED goal NOT PASS.

Next actual work: separate native indexed rigid-mass contract, then finite
same-finger dorsal-yoke geometry. This closes a transverse structural loop,
not the previous external ring relief, beam width or axial offset family.

##1720–1726: same-finger dorsal terminal rung

1720 NEW Native indexed UniformMass contract (not failed DiagonalMass):
two distinct masses/inertias, known force/torque, four actualsteps; maximum
velocity error4.441e-16. Independent initial assembly scope ONLY.
1721 producer failed a SAT helper argument check before Native; preserved.
1723 corrected geometry: same terminal Guide5/11 share one COM body; original
six foot coordinates, existing support/rings and all collisions retained.
Finite0.8mm section,1mm dorsal offset derived from section+existing buffer.
Density1000kg/m3 and ideal rigid weld are research assumptions, not hardware.
Initial new object gap0.92047mm; wire capsule separation>=4.16868mm and
foreign hardware separation>=7.71536mm. Neither swept nor finite-wire PASS.
1724 actual0.6s/240steps:87.892s, minimum saved FEM ratio0.990448;
actual shared-body cable mapping error1.388e-17m, terminal pair distance
invariance6.939e-18m. This is a new structural mechanism, not width tuning.
1725 independent CSG audit subtracts declared original-support weld domains,
then intersects NEW material with all broad-phase FEM tetrahedra: no positive
new intrusion. Existing same-finger group is justified ONLY for those bonds.
Audit also identifies duplicated support material in the initial full-bar
mass calculation:3.38–3.42mm3/finger.1724 is therefore an uncalibrated mapping
pilot, NOT a mass-corrected grasp candidate. Next actual implementation must
use added-material-only mass/COM/inertia, not reuse1724 as that result.
No old data or verdict is changed. Actual physical weld stiffness/retention,
guide original masses, contact normals and global convergence remain open.
