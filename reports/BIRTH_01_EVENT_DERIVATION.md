# Birth validation 01 EVENT DERIVATION

Status: PASS (smooth prescribed-event kernel); EXPERIMENTAL trajectory model

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

For committed object-local material point a and current point b, define x(t)=a+t(b-a), g= SDF(x)-skin. Birth is the first transversal entering root alpha in [0,1]. End-state derivative is

`d alpha = -alpha n_birth dot d b / (n_birth dot (b-a))`.

This is the IFT for a frozen previous state and a local straight chord, not full SE(3) continuous dynamics. Root value uses double geometry; its AD derivative uses the same SDF normal. The transported post-birth increment is used in both scalar Commit and AD Force/Jacobian. A grazing denominator is explicitly rejected relative to chord length; no epsilon denominator is substituted. Full-step resolved birth/death chords are rejected and require actual substeps. ULP-scale unresolvable negative signed gaps are counted explicitly, not reported as resolved CCD.

60 smooth Sphere/Cylinder/Box birth force/Jacobian cases have max normalized FD error 1.3005749602279515e-9. Boundary branches are tested separately; no differentiability is asserted at contact, slip, endcap or corner transitions. The original .01-mm missing increment is recovered. See build unit stdout and independent math_events logs.
