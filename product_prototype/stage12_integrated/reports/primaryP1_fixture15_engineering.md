# P1 fixture15: actual key-root CAD and conditional compliant joint

This continues the one P1 Motor→Drum→Tendon→Finger→Root→Frame→Ground→Base specimen.
Failed AO, adopted AA and the original three-finger/cartridge/jamming extension
remain unchanged. There are 78 actual parts, with only Ground and Base STEP/STL
changed. The full assembly and BOM are in cad/exports/primaryP1_fixture15.

Ground has four R0.5 concave key-root fillets. Base has a 0.6 mm, 45 degree
underside pocket entrance relief, retaining its prior R1 blind corner reliefs.
The upper nominal zero-gap key still exists; the shared vertical contact areas
are now 24 mm² on each x face and 14.4 mm² on each y face. The shared seat is
2380.036048703312 mm². Actual reimported inventory, 190 final Boolean pairs,
52 fixture assembly samples / 79 comparisons and 10 tool checks pass their
bounded nominal checks. Independent original-module assembly/identity checks
and one saved loaded cable/rotor pose also pass. This is not continuous CCD,
thread tightening, machining tolerance or full three-finger Stage1 approval.

Ground material design intent is explicitly 304 stainless, continuing the
original steel-fixture function. Base remains a 6061-T6 design intent. Neither
is purchased or certified. Reference E/density and nominal Pololu 1101/1996
masses are documented in models/materials/primary_joint_sources1/reviewed.json.
All 78 actual CAD volumes/centroids are enumerated and independently reimported.
Conditional total mass is 0.9898950917863771 kg. The old 69-part module including
Ground is 0.6725756943965662 kg. Its 68 upstream parts excluding Ground weigh
0.29609879426836144 kg. The mass producer's field named module69_conditional_mass_kg
actually represents that 68-part subset; this naming defect is preserved and
explicitly corrected by primaryP1_cycle6_closeout/summary.json. Whole-product
mass and wrench arithmetic are unaffected. Nominal mass is not a guaranteed
upper bound; smooth fastener/thread envelopes and motor COM remain uncertain.

For g=-Z, the required external Base wrench from all masses plus the prior
operating port is [-0.408610416667, 0, 9.707554701867, -0.076586225227,
-0.224076809482, 0] in N/Nm about the repository origin. This combines rest-CAD
mass coordinates with the earlier gravity-free operating wrench. It is a
frozen-state boundary reference, NOT a gravity-loaded Finger equilibrium.

The full finite Ground and Base are separate elastic bodies with conforming
surface geometry and duplicated interface DOFs. Frictionless unilateral key
and seat contact supplies compression only. Four distinct tension-only axial
connectors couple area-averaged actual head and nut footprints. Their basic
minor-core compliance and half-nut length are explicit sensitivities, not ties
on nominal major cylinders or validated thread engagement/bearing capacity.
Non-Base hardware weights are transported to the Ground port; local connector
selfweight distribution is approximate. The Base receives an explicit finite
surface traction wrench. Six volume rigid-motion gauges carry negligible
resultants; they do not certify any physical bench grip or anchorage.

Seven completed elastic solves span old/new geometry and one 10 N initial
preload contrast. Final fixture15 has 18,696 / 42,066 / 76,473 DOFs. Independent
direct tetra forces/energy, contact gap/complementarity, bolt laws and perturbed
field rejection verify the seven saved states. Fine new bolt forces are
[4.554146615454, 5.049198234153, 4.579677830884, 4.879686707392] N. Fine conditional
Ground/Base peaks are 0.731691712122 / 0.626477440881 MPa. No strength or allowable
is inferred. R0.5 fillets do NOT demonstrate lower peaks than old geometry.

New h=3.5→2.5 mm differences are Ground stress 46.53155%, Base stress 19.27347%,
Ground motion 13.25255%, Base motion 3.44205% and elastic energy 11.88496%: FAIL
unchanged 1%. Old 5/3.5/2.5 and historical LP/Frame/Rail failures are retained.
The new fine Ground hotspot is near [-47.7732,5.0804,46.7385] mm; Base hotspot
near [-39.7977,-4.8137,49.1] mm. Contact edges, finite bearing and load ports
need resolution; blanket further mesh runs would not establish qualification.

Failures preserved: first result JSON serialization, first verifier path typo,
and first CAD edge-duplication assertion. All have original source/logs and new
terminal summaries. The prior-geometry 0.02 mm contact-law gap contrast timed out
at 420 s, was killed/reaped and was not retried. No gap-state result exists.
Only save-only closure and the unchanged release audit followed the timeout.

All 22 system gates remain UNQUALIFIED. Release8 returns INTEGRATED_NOT_QUALIFIED
with 24 errors, exit2. No Stage3, hardware, strength, physical mass/inertia,
source-minimum preload/engagement, global energy or powered-operation claim.

Next exact task: goal_primary_gravity_loaded_chain. Use the existing finite
Rail/PET model to derive gravity potential and actual terminal/swivel mass
pullbacks, verify virtual work/zero-g controls, then solve gravity-loaded
Finger equilibrium and deformed mass centroids. Carry its paired Root/Motor
forces and couples through the actual Frame and current joint, with finite
bearing/thread/anchor definitions and the existing mesh failures retained.
