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
