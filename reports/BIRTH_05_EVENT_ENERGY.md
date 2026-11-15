# Birth validation 05 EVENT ENERGY

Status: PASS independent discrete contact scope; EXPERIMENTAL actual event energy

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Independent prescribed plane Stick/Slip/Birth/Death/Recontact tests verify the backward-step spring identity, Coulomb return loss and objective rotation transport. Born tangential elastic energy for kt=1 and extension .01 is .00005 force-mm. Resetting that stored state records a separate .00005 detachment inventory loss; it is not silently relabeled Coulomb heat. Large common rotation error is8.94e-17. See math_events/summary.json and run/stdout.log.

Actual SOFA controlled plane contact has only mass/contact/fixed zero-velocity object: no gravity, actuator, external load or damping. A single dt1 birth step restores history but adds about1e-4 force-mm to K+U, because its implicit force stage was still separated. Coarse dt.25 gives accidental near-zero error, NOT proof of exact energy integration. Further refinement dt.125,.0625,.03125,.015625,.0078125 gives energy defects about-1.2355e-5,-9.3112e-6,-6.2241e-6,-2.9242e-6,-1.5610e-6, tending down in magnitude. No-contact control is exactly0. These measured residuals are NOT relabeled numerical heat. See controlled_event_energy.json and actual per-event journal. The artificial coarse event dt is not the100-mm baseline dt. This distinguishes endpoint history correction from full ODE event resolution.
