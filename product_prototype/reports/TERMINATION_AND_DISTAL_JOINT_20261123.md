# Terminal and distal joint continuation — 2026-11-23

Starting local HEAD `3f780a7`; clean working tree. Cases971–987 were reused,
not rerun. These are new CAD/reference studies, not Native SOFA physics trials.

## Supplier inputs and real incompatibilities

The [manufacturer's swaged terminal table](https://www.carlstahl-technocables.com/gb/en/products/assembled-ropes/swaged-terminals/)
lists NI000001 for rope0.27–0.45mm, brass, finished diameter2.5±0.3mm and
length4±1mm. KU000016 is a stainless ball for0.45–0.50mm, diameter1.5±0.3mm.
Dimensions are after swaging; assembled-rope procurement and reduced completed
breaking load must be checked with supplier. No pullout/fatigue rating, price,
availability or loose DIY crimp qualification is assumed. Inputs saved in v48.

988 rejects robust direct fit of both maximum terminals into the existing1.5mm
drum channels. Its initial1.2mm bore assumption came from a Root insert, not the
actual distal part. Append-only CORRECTION preserves988. 995 independently
sections all6distal Eyelets: mesh opening minimum1.3983136387mm (nominal1.4mm,
polygon discretization). 997 recalculates using that actual mesh opening:
NI minimum radial shoulder0.400843mm; KU minimum shoulder−0.099157mm, so ball
retention is not guaranteed across its catalog range. Neither result proves
physical fit, bearing strength or manufacturing tolerance.

## Candidate sequence and failures

- 989: six maximumD2.8×L5 cylinder envelopes placed on actual Eyelet distal
  faces. Wire pull must point back through the guide. Support overlap~0.690mm³
  each: REVIEW/failed placement, retained. No hardware collision disabled.
- 990: explicit R1.55 exit relief removes that bulk obstruction. It exposes
  pre-existing Eyelet/Support overlaps~2.13mm³ each; not newly created by relief.
- 991: independently records those six ORIGINAL interface overlaps.
- 992: explicit R1.55 socket from localX−1.05 removes the original overlap,
  nominal0.05mm radial gap aroundOD3 Eyelet. All6Supports remain single closed
  bodies, but bond/keeper/retention are UNSELECTED; this is NOT a load-bearing
  joint. Six small terminal/Eyelet world-CSG intersections remain REVIEW.
- 993: common declared frame and shoulder plane exclude open interiors in
  rigid mathematics. This does not erase world-CSG faces or certify real fit.
- 994:18STLs saved, then selected Z=0 plane did not intersect Support. Failed
  drawing and partial v49 pack preserved; no geometry moved for appearance.
- 996: actual localY=0 section succeeds; v50 contains18actual closed STLs,
  subassembly recipe/BOM, PNG/SVG. Visually inspected. No STEP/CAD kernel.
- 998:166software tests PASS,5.115s test body/5.684s guard.

## Assembly order is not automatic

995 shows a nominal free0.45mm end can pass the distal mesh opening, but both
factory-preterminated NI/KU ends cannot. Conditional sequence: procure one
distal end swaged; feed the free end through guides toward Root; route openable
pulley hardware; install a validated reusable drum termination afterwards.
The latter is missing. Fraying, all other bores, process dimensions and actual
threading trial remain NOT MEASURED. No forced terminal compression assumed.

## Local web issue: geometry alone is not success

999 measures four f0/c0 localX lines at localY0. Socket992 leaves Z-material
thickness0.017449/0.041643/0.065837/0.110924mm where the old intersecting proxy
had0.842607/0.899661/0.956715/0.955187mm. This is a local line-section reference,
not global minimum wall or a strength test. It identifies a thin web requiring
redesign; no invented stress/material/physical strength or threshold PASS.

## Independent motor/CAD constraints

The [official HNX330-N101 product description](https://robotis.us/products/hnx330-n101-set)
confirms XL330/XC330 compatibility and supplied M2×4 fasteners. It does not
validate our drum's generic D6 opening or motor pose. Current browser drawing
links resolve to landing/category pages; a dimensioned horn/output-axis drawing
was not validated. No hole pattern or torque fit guessed from thumbnails.
FreeCAD commands and Python FreeCAD/OCP/OCC/cadquery are absent. STEP remains
BLOCKED; no installation/purchase/SDK change or remote push performed.

## Reproduction (new unique tags only)

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY product_prototype/cad/distal_terminal_candidate.py --tag UNIQUE
$PY product_prototype/cad/distal_terminal_candidate.py --tag UNIQUE --exit-relief --seat-relief
$PY product_prototype/cad/terminal_mating_certificate.py --tag UNIQUE
$PY product_prototype/cad/terminal_review_pack.py --tag UNIQUE --name UNIQUE
$PY product_prototype/cad/termination_installation.py --tag UNIQUE
$PY product_prototype/cad/termination_contract.py --tag UNIQUE
$PY product_prototype/cad/distal_web_section.py --tag UNIQUE
$PY product_prototype/cad/manufacturing_test_run.py --tag UNIQUE
```

NEXT: explicit thicker distal socket base as a new design variable; check its
interfaces and section changes, not just closedness. Actual insert retention,
wire pullout, reusable drum termination, complete moving clearance, material,
Native time/mesh/100g/Lift remain unqualified. Old B3 functional Holding does not
certify this new joint or terminal candidate.
