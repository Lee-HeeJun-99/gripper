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

##1728–1733: union-mass corrected candidate

1728 actual new material only (complete yoke minus old support weld domains)
adds12.874–12.922mg/finger at assumed1000kg/m3. Original guide/support masses
are inherited, not measured. Recomputed COM and full parallel-axis inertia;
no geometry/FEM/force/dt/solver changes.1729 actual Native initial tensor
response matches independently inverted full tensors to8.882e-16 in velocity.
1730 NEW actual0.6s:87.087s, minimum saved FEM ratio0.990450, terminal mapping
error1.388e-17m;1731 all cross-finger response rows0.1732 exact faceted CSG
at initial+8stored states/finger (828cell checks): no positive new-material
FEM intersection outside declared original weld domains. This is sampled,
not swept, and not real joint strength.1733 includes ALL75finite hardware
parts (the previous helper was explicitly extended to include3rungs):
450000pairframes, none inside unchanged0.2mm buffer; hardware/object gap
>=0.594283mm. No hardware/object active loads in this0.6s entry prefix.
Next actual1.2s withdrawal test, same1728 geometry/mass and1.5N inputs.

Commands (NEW tags only):
```
python product_prototype/sofa/yoke_union_mass_candidate.py --tag UNIQUE_GEOMETRY
python product_prototype/sofa/yoke_inertia_native_contract.py --case UNIQUE_GEOMETRY --tag UNIQUE_MASS
python product_prototype/sofa/dorsal_yoke_native.py --tag UNIQUE_PILOT --design UNIQUE_GEOMETRY --mass-contract UNIQUE_MASS
python product_prototype/sofa/mechanism_contact_inventory.py --case UNIQUE_PILOT --tag UNIQUE_PAIRS
python product_prototype/sofa/yoke_deformed_material_screen.py --case UNIQUE_PILOT --tag UNIQUE_MATERIAL
python product_prototype/sofa/actual_hardware_clearance.py --case UNIQUE_PILOT --tag UNIQUE_CLEARANCE
python product_prototype/sofa/dorsal_yoke_native.py --tag UNIQUE_PREFIX --design UNIQUE_GEOMETRY --mass-contract UNIQUE_MASS --duration 1.2 --pilot UNIQUE_PILOT --pair-case UNIQUE_PAIRS
```

##1734–1741: withdrawal prefix and declared full diagnostic

1734 actual1.2s480steps149.121s: min saved FEM0.989808, shared terminal
mapping1.388e-17m.1738 internal15nonzero rows at1.0575–1.0675s, exclusively
F0Cable1/F2Cable0 terminalEyelet5. Whole-motion zero-row gate remains FAIL.
1739 sampled new-material/FEM intersections0 (840cell tests);1740 all75parts,
900000pairframes, two frames inside0.2mm buffer but actual envelope SAT
separation0.199711/0.199881mm. This is NOT zero internal support.
Original1700 bracing starts0.7125s; yoke delays but does not eliminate it.
At1.2s actual object speed21.603mm/s; formal Hold window not yet observed.

1741 actual full2s diagnostic is now running, not a qualified unbraced trial.
Reason: short transient disappeared before1.2s; determine actual recurrence
and1.6–2.0s object performance rather than infer either from a prefix.
No collision, friction, force, dt, shape or physical gate changed. Full-path
UNBRACED is already FAIL due15earlier rows, even if later Hold has none.
Runtime estimate uses new measured stage evidence, not a physical gate change:
149.121s observed1.2s +2*(149.121−87.087)/.6*.8 =314.543s, hard420s/4GiB.
No initial-state checkpoint or object forcing; full run starts from original
initial conditions and common-prefix q/v must reproduce exactly.
Original2mm slip/5mm_s speed/5mm gap/1e-5N support gates remain unchanged.
Do not promote a functional observation to numerical/physical/hardware PASS.

1736 indexes all original102 task evidence:53PASS,24FAIL,15REJECTED,9BLOCKED,
1NOT MEASURED. Missing root causes stay explicit, not fabricated.1737 exact
scene-attribute whitelist confirms no undeclared original grasp input changes.
Four new producer contract tests pass; not physics certification.

Actual full diagnostic command:
`python product_prototype/sofa/yoke_holding_diagnostic.py --tag yoke_hold_diagnostic1741`

##1741–1753 completed: full Holding FAIL; new translating-guide contracts

1741 actual800steps/2s249.292s normal exit, min saved FEM0.989808;
common1.2s prefix q/v difference0 (reproducibility, NOT time convergence).
1742 original100g Holding: slip0.576782mm, maxspeed32.928255mm/s FAIL;
Skin meanFz0.983151N vsweight0.981N; Guide/Rail/Support/other object loads0.
Support gap42.0512mm; momentum residual4.337e-19Ns. Solver1001/1000.
1743 internal48rows total,30IN HOLD: actual repeated terminalGuide bracing.
Thus both FUNCTIONAL and UNBRACED FAIL. Compared with1700: fewer internal
Hold rows99→30 but speed25.5913→32.9283mm/s worsens; do NOT select as better
grasp design. No Lift.1747 all75hardware/1.5million saved pairframes:9within
unchanged0.2mm buffer, all separated SAT0.199056–0.199991mm, not swept PASS.
1748 initial+8samples/finger new-material/FEM overlap0;1749 actual18Guides
still fail straight radius0.25mm wire fitting, flexible-wire contact unqualified.

1745 quaternion swing/twist diagnosis: prefix max twist0.188811deg; removing
twist at SAME actual COM rescues0/300 unsafe own-sector samples. Therefore
torsion-only stiffening is not supported as the next cure by this geometric
reference. Counterfactual poses are NEVER actual deformation or grasp results.

Different mechanism: a physically keyed prismatic eyelet carriage, not a
different fixed-guide offset and not equivalent loose-bore wire contact.
1746 installed ArticulatedSystemMapping + NativeCableConstraint + stock
Vec1 Stopper:40actualsteps0.169s; free discrete position error9.758e-19m;
actual travel2mm, final velocity−1.324e-16m/s, keyed orientation/root errors0.
Fixture mass1g/T0.01N are explicit coupon assumptions, NOT B3 hardware specs.
1750 moving-root scene parse FAIL: input2 state defined after mapping;
1751 corrected base order but late RequiredPlugin caused ForceField factory
FAIL. Both preserved.1752 plugin/base before dependent components: actual
four-step free-force moving-root response error0, base error8.674e-19.
This initial collinear response is limited; next actual stop-transfer test
must cause a FREE root to move, excluding a hidden fixture/mass-coupling error.

1753 actual path/multiplier independent virtual-work reference: all4800
loaded terminal samples point OUTWARD; hold outward demand1.04319–1.04394N.
Necessary fixed-pose inward travel max1.87901mm, not a dynamic route or chosen
stroke. A freely passive slider alone is rejected as a closing mechanism.
Actual lagged Native J is NOT measured by this current-geometry reference.
Need an explicit cross-draw/cam/spring force source and real carriage geometry,
not assume the old cable automatically pulls the slider inward. No arbitrary
spring/force increase or whole-grasp trial justified yet.

Next executable native contract:
`python product_prototype/sofa/captured_prismatic_moving_cable.py --tag captured_moving_stop1754`
Then actual internal cross-draw cable action/reaction and finite keyed carriage
geometry are independent prerequisites before any new3Finger trial.
