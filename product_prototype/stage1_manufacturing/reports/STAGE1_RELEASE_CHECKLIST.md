# STAGE1_DESIGN_RELEASE_FAIL — revH, 2026-11-25

Actual gate: scripts/release_gate.py → validation/release_revH/summary.json.

- [x] Minimum architecture selected as engineering candidate
- [x] Actual3Finger CAD, individual STEP/STL and assembly STEP/STL generated
- [x] Real OpenCascade BRep validation and STEP aggregate-volume reread
- [x] revH157 single closed positive-volume solids; nominal bulk collisions0
- [x] Motor dimensional source, shaft and bearing boundary envelopes defined
- [x] All6 REST straight finite-wire spans clear; intended idler contact separate
- [x] Full-turn drum outer bound has no foreign obstruction
- [x] Declared unloaded cartridge extraction25sampled poses clear
- [x] Staged cylindrical driver approach clear; full assembly6blocked approaches
- [x] BOM maps each actual part ID to actual STEP/STL and manufacturing candidate
- [ ] Actual bearing/shaft axial capture
- [ ] Actual drum/coupler torque lock
- [ ] Positive retained tendon terminals/drum anchor
- [ ] Complete moving Finger/Wire/fixed-hardware verification
- [ ] Full purchased tool, recess, thread, washer and lock interfaces
- [ ] Supplier-specific fit/endplay and manufacturing tolerances complete
- [ ] Shop-ready dimensioned drawings and manufacturing process release
- [ ] Jamming extension interface/space verification
- [ ] Released Stage2 load-test assembly

Corrected prescribed motion uses actual Root endz=-7 and93mm flexible span,
including transported finite terminal hardware. Sampled interFinger collision
first appears at58degrees;0–56degrees samples clear, not continuous clearance.
Earlier bare-strip proxy below Palmz=-12 omitted that collision and is NOT
accepted as whole-mechanism motion verification. No actual closure law or
return mechanism is qualified. No motor is energized; no new Native or
physical measurement is claimed. Stage1 is NOT complete.
