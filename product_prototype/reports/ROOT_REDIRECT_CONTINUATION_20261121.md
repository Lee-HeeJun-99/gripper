# Root redirect continuation778–781

Source baseline5234ccef1879a12bfac87592560c144edd2ae083; no SDK edits or new
SOFA dynamics. Previous CAD/raw/FAIL records remain unchanged.

## Implemented and measured

- 778: six actual ASCII STL root wheels, OD6mm, pitch radius2mm, wireD0.5mm.
  Root direction comes from actual first Eyelet centre and existing perimeter
  lead-in, not an assumed90-degree turn. All six turns are76degrees.
  Actual Manifold screen against280 prior parts: zero solid intersections.
  Runtime13.8742s. Conservative wire probes overlap intended wheel contact:
  516 nonempty results retained; status ROOT_REDIRECT_REQUIRES_REDESIGN.
- 779: independent right-angle reference and two degenerate rejection cases.
  Arc radius error<=6.89e-15mm, ideal barrel radial clearance0mm (contact),
  flange side clearance0.15mm nominal. This explains conservative-probe hits;
  it does NOT change778 or establish tolerance/friction/physical clearance PASS.
  Conditional resultant1.846984N at ASSUMED equal1.5N branch tensions.
- 780: six wheels plus six finite forks and six pin proxies,18 actual STL
  readbacks. Existing280 parts plus new module pairs: zero solid intersections.
  Wire hits only on intended wheels, none on forks/pins. Runtime14.2356s.
  Still UNMOUNTED and unretained; NOT complete hardware or product PASS.
- 781:47 design/software tests PASS in3.3156s; not time/mesh/holding qualification.

Each new fillet shortens this reference path by0.4722757145mm relative to
the sharp ideal Root corner. Existing Native pullpoint/control cannot be
transferred without explicitly changing the physical model and validating it.
Supplier minimum bend radius, material, friction, bearing loss, actual
mount reaction and physical tolerance remain NULL/NOT MEASURED.

## Evidence and reproduction

Raw:product_prototype/results/product_root_redirect778,
product_root_reference779,product_root_fork780,product_root_regression781.
Each analysis preserves executed producer snapshot and source/input hashes.
778 producer predates explicit degeneracy guard; its saved producer is the
executed identity, not the later working source. 780 includes the new guard.
CAD:meshes/b3_root_redirect_v30 and meshes/b3_root_fork_v31.
No STEP, no physical fabrication readiness, no new Binary/SOFA execution.
Commands (use unique new tags/names; existing outputs are immutable):

```bash
ulimit -v 4194304
timeout 480 /home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/cad/root_redirect_candidate.py --tag UNIQUE_ROOT --name UNIQUE_ROOT_CAD --fork
```

## Next executable work

Design a finite Palm-to-root-fork mounting and retention path; screen against
all280 obstacles and both sides of the wire BEFORE Native integration. Avoid
adding another large outer tower: latest bridge already reachesR94.6495mm.
Then jointly simplify the support architecture and check fastener/tool access,
axle extraction, material-dependent frame deflection and tolerance stack.
Do not remove wheel/guide collisions or promote nominal tangency to assembly
qualification. Native contact/time/FEMmesh failures,100g/Lift and STEP remain
open. No automatic execution after session exit.
