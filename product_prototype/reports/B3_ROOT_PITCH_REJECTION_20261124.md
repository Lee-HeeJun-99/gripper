# Root pitch geometry1323–1324 — rejected,not Native grasp

Actual sourceconfig alreadyhas root_angle_deg14.0,precurve40,start70mm,
rootradius50mm.1323rotates source reference by ADDITIONAL14deg,thus total
mountangle28deg. Its original pitch_deg0/14 fields are OFFSETS,notabsolute
mountangles;originaldesign_change text is ambiguous. Preserved rather than
rewritten. Producerfuturemetadata nowstatesadditionalandtotalangles.

ReferenceSkin spheregap1.39880mm,nearestmaterialstation91.8805mm.
Additional14deg gives18.4447mm initialpenetration atstation85.8508mm:
REJECT. NoNativeSceneoractuationrun. Same100mm materialmesh,rigid reference
rotation preserves volumes (roundoff≤1.78e-13relative),not prescribed dynamic
deformation. Three exportedSTLs are collisiongeometry ONLY,notmanufacturing
solids/Assembly/STEP. Hardware/wire/sweptinterference NOTMEASURED.

1324 computes envelope's localrigidrotation derivative onactualresttriangles:
−0.0814900m/rad,centralFD h1e-6rad error≤6.35e-12m/rad. With existing0.2mm
contactmargin,first-orderadditionalinwardpitch allowance≈0.84288deg.
This is NOT a certifiedglobalfeasiblerange ormanufacturingtolerance.
Do not anglesweep pastknowninitialpenetration or transferSkin-only clearance
toGuide/WireCAD. Larger inwardtilt is not a solution atfixed initiallayout.

New hypothesis must altercontactretention/momentdistribution while retaining
initialaperture,not merelyraiseT or tiltwholehand. Review earlier routing/
precurve candidates before selecting a genuinelynewone;actual Native must
validate bending/contact separately afterfullinitialgeometrychecks.

Commands withrobot_wsPython,NEWtags only:
`product_prototype/sofa/b3_root_pitch_geometry.py --tag NEW_GEOMETRY`
`product_prototype/sofa/b3_root_pitch_margin.py --tag NEW_DERIVATIVE`
Actualsourcehashes,referenceq0 andfailedcandidatecollisionSTLs preserved in
1323/24. OldCAD/Raw untouched;no new fabricatedcomponent orWrappingPASS.
