# Actual AK nominal-thread load-path diagnosis

One bounded geometry analysis cycle, starting HEAD
3c5e29cba13eeebb3b3496257f40bdd5e1280e63. Local supervisor save pending.
No CAD/BOM adoption or modification. Canonical result:
validation/transmission/AK_idler_cycle1/summary.json.

All 235 STEP references in the AK candidate match their recorded hashes.
The actual three sector axle/nut/washer/bracket solids were read and rotated
back into the common local frame. The 3mm journal/thread-major envelope and
2.38mm neck are extracted from native cylindrical faces, not a screenshot.
Each nominal nut bore is radius1.5mm. Five axial translations per nut
(0,-.01,-.1,-.5,-1mm) have zero volumetric axle interference. A .05mm
radial translation yields .35998333mm3 interference in each sector.

The separate verifier does not infer continuous clearance from those samples.
For each sector it clips the actual axle to Y=[-9,-5.5]mm, enclosing all
nut positions in the stated translation interval. No clipped axle material
lies outside the coaxial radius1.5mm cylinder; no nut material lies inside it.
Rotation about the same axis preserves these radial sets. Thus every axial
translation in [-1,0]mm remains non-overlapping against this axle. This is
an axle/nut proof only, not full-assembly escape or a hardware observation.
The touching cylindrical surface normal has zero axial component, so a
frictionless normal-contact solver cannot transmit the intended axial nut
preload through these smooth nominal envelopes. Helical flank contact or an
explicit independently qualified thread connector is necessary for that model.
A tied connector imposed without such evidence would merely assume capacity.

The neck area is4.44880936mm2, versus nominal-major area7.06858347mm2.
Their ratio .62937778 does not identify the controlling manufactured section:
actual thread core geometry is absent. Nominal d=3mm cannot substitute for
thread-root area, and neither area establishes stripping, fatigue, notch,
preload, washer/bracket bending, drag or protected-load capacity. No physical
thread allowable is assigned. The prior stack geometry PASS remains valid
within its original scope and is not converted to strength PASS or FAIL.

Next useful design choices are an explicitly specified/gauged M3 thread and
material with independently supported preload/strip/combined-load limits, or
a separately evaluated rated shoulder/double-supported idler. Choose a real
load bound first; do not repeat smooth-envelope translation scans or solve
preload on a frictionless model that has no axial thread transmission.
Independent root restraint and base attachment remain open mechanisms.

The read-only release audit remains INTEGRATED_NOT_QUALIFIED with24errors,
including22unqualified Stage2criteria. Analysis and verification each exit0
and their geometric checks pass; this is not SOFA execution, equilibrium,
strength, physical energy or same-revision system release qualification.
The default interpreter dependency probe failed with ModuleNotFoundError: OCP;
analysis used the existing /tmp/regrip_stage1_ocp path without installation.
All earlier failures and unrelated untracked files are preserved.
