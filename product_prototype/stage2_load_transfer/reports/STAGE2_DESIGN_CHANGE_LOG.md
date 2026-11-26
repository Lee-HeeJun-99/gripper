# Independent design correction, not an adopted product revision

Stage1 Rev A–AA and all release evidence remain unchanged. Current reference
is STILL RevAA. New `revised_cad/revAB_sliding_pet1` is a candidate only:
six actual changed STEP/STL parts and a real304-part ASSEMBLY.step.

The reduced locked-end model predicts PET−39.1408N and rails+19.5704N each
at0.817899N cable tension /16.91mm stroke. Therefore tiny external cable force
does NOT imply tiny clamp retention load. Assuming friction0.1 would require
~391.4N normal force at the controlling interface; actual friction/preload unknown.
This motivates a different mechanism, not a stiffness/force sweep.

Candidate: trim PET toZ−94.4 (remove distal indexing/capture); retain actual
steel rails; add integral3mm-wide rail pads to the front clamp and a finite
transverse capture lip/channel. No extra parts; nominal longitudinal gap0.60mm.
Maximum thickness-offset travel at60deg plus0.15mm cut/datum budget0.427507mm
leaves0.172493mm. Bounds are design requirements, not measured machining data.

All six changed solids valid/single/closed positive STL. New-vs-retained actual
304-part nominal common checks have no hits. Initial diagnostic FAIL retained:
it mixed maximum PET rear50.31 from a0.19mm rail with a nominal0.20mm rail
front50.30. That is not a coexistent stack. Independent audit
`validation/finger/sliding_pet_correlated1` tests EACH correlated thickness case,
including front clamp float, at unchanged1e-8mm³ common criterion. It passes
only local clearance; original failed summary is untouched.

The ideal free-slip control predicts0.440046N instead of0.817899N, and a
different shape. This is NOT actual performance of the candidate. Actual channel
friction/contact, PET peel/wrinkling, candidate-matched FEM, dynamic geometry,
manufacturing radii, thread/tool/service checks and mass/inertia updates are
still required before adoption. Selected volumes per Finger: PET611.396814→
591.275520mm³, front592.951277→662.097277mm³. No physical mass claim.

Separate fixture correction: `split_end1` interference FAIL, `split_end2`
revised split kerf and independent fit audit PASS geometry only. No product
geometry was silently changed to accommodate the fixture.
