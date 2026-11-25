# Connected open-guide assembly1780–1782

Start c231571, clean worktree. Geometry-only new candidates, SDK NOT USED.
Source, scene, input geometry hashes, command and bounded measured runtime are
in each completed summary. No original scene/Raw/verdict has been overwritten.

1780 IMPLEMENTATION FAIL before completed assembly screen: default STL import
of1778link1 fails closed-volume assertion. Failure producer and exact source
SHA preserved. Old1778in-memory positive-solid test is unchanged; serialized
STL is not thereby a qualified topology-preserving downstream source.

1781 constructs fork/leaf/pin solids directly from original parametric build
and actual six-guide axes/pivots, not a tolerance-adjusted STL repair. Roots
connect all original three feet; Carrier connects actual collar and forks.
All54assembled parts are positive single solids, but26positive pair overlaps
and12wire overlaps: REJECTED_INITIAL_ASSEMBLY, runtime1.929s. Overlaps include
root/link0~.582–.605mm³, root/pin0~.255mm³, carrier/link0~.220mm³.
PLY and STL are visualization/interchange only: despite the old inline comment
in1781producer, no float64 PLY fidelity claim is supported. Exact topology
storage is explicitly implemented in1782, not retroactively asserted for1781.

1782 single physical change: machine NEW root/carrier bearing pockets with
hub radius.75+.05mm clearance and axial.4+.05+.05mm, plus .30mm pin holes.
Original tube and collision solid unchanged. First obstruction count reduces
to12but is not zero; one Carrier becomes two components. All18original feet
remain contained. Twelve wire overlaps persist: six old straight wire/tube
conflicts~.057085mm³, six new collar conflicts~.0002377mm³. REJECTED, runtime3.260s.
Do not treat a smaller interference volume as PASS or remove detached pieces.
All54meshes additionally saved as indexed float64 NPZ, exact array roundtrip
assertions pass. Real material density/mass/strength/friction NOT MEASURED.

Commands (new output tag required):
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_guide_assembly.py --tag NEW
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_guide_assembly.py --tag NEW --bearing-pockets
```
No new Native grasp justified. Do not repeat pocket/radius scans. Geometry
needs a different load-bearing connection path, not another enlarged cut.
Independent next trial: free6DOF root/open-joint initial mass/Jacobian contract,
using declared small fixture forces and stock Native mapped masses. This
does not adopt the rejected finite geometry or qualify wire contact.
Latest actual full100g1741 still fails speed and internal bracing; no Lift.

## Routed/axial alternatives1792–1804

1792 uses rear root spine and two axial cheek struts, rather than filling the
pivot cavity with a convex hull. REJECTED18pair/12wire overlaps, all54connected.
1793 combines true collar/hub surface stacks: carrier pivot distance1.9755mm
=outercollar1.1755+hub.75+gap.05. Root's first approximate stack1.10mm was
insufficient because its foot cubes are WORLD-axis aligned, not normal aligned.
REJECTED6root/link overlaps.1794 derives root height from the maximum projection
of every actual foot-cube corner, plus.75+.05mm:1.250231–1.294144mm.
All18feet retained,54positive connected solids, old/new solid pair overlaps0.
Twelve straight-wire overlaps remain, so whole assembly stays REJECTED.
1796 actually replays21rigid mechanism FK samples0..2mm (NOT actual FEM motion):
first carrier/link0 collision1mm; tube/link0 begins1.8mm,84pair-frame overlaps.
Kinematic closure2.342e-17m does not imply physical clearance. Coplanar rejected.

1797 new axial link plane: tube position/size unchanged, actual hinge/link plane
moves along its rotation axis1.25mm=originaltube half-length1+.2leaf half+.05gap.
Real root/cheek/rear axial ties are constructed, not rigid mappings across air.
Float32 CSG produced one zero-volume4face detached component; NOT discarded.
1798 implementation binding error before geometry, both failed sources saved.
1799 installed Manifold Mesh64 adapter with copied writable float64 arrays,
no merge/tolerance override or SDK/library edits: all54connected,18feet retained,
new/old solid overlaps0, initial minimum object gap2.188338mm. Twelve straight
wire overlaps still FAIL. STL/PLY visualization only; exact indexed NPZ checked.
1800 actual21sample FK with same64bit CSG:0pair overlaps, closure2.168e-17m,
16.618s.1801 import error preserved;1802initial new-material FEM screen uses
all3finger meshes, only declared original support5 root-bond domains subtracted:
96broadphase cells,0positive overlap,0.770s. These are NOT dynamic FEM results.

1803 independent invariant axial slab bound: link/tube solid gap>=~.05mm for
any parallel-axis crank rotation/common rigid root motion. Actual unchanged
Native contactDistance.2mm => buffer FAIL, not contact/UNBRACED qualification.
No distance reduction, collision deletion or ignored contact row. Four64bit
kernel sanity tests (known box volumes/translation/empty/open-input) PASS.
No STEP, measured material, pin retention or hardware qualification claimed.

1804 independently reads actual1795Vec3 endpoint J and solver impulse/dt:
actual tension1e-7N, endpoint net force/moment0 at previous accepted geometry,
instantaneous power pullback residual1.564e-23W. Integrated cable work/global
energy remain NULL. parent_J in this audit is Vec3, not a full globalRigid3J.

Current axial geometry is BLOCKED for Native integration by straight finite
wire nonfits, .05vs.2mm contact budget and unretained pins. Do not launch new
100g from a kinematic PASS. Finite-motion mass/convective contract is separate.
Reproduce with NEW tags only:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_guide_assembly.py --tag NEW --routed-connections --clearance-stack --projected-foot-stack --axial-link-plane --csg64
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_guide_motion_screen.py --tag NEW --case open_guide_axial64_1799
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/open_guide_skin_screen.py --tag NEW
```
