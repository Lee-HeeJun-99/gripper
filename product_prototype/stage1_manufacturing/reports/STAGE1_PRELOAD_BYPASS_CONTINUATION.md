# Rev V → W: actual preload path and running clearance

2026-11-26; Stage1 only. Last implementation savefff8cba; later current HEAD
via git log. No Native/SOFA, hardware, SDK change, push or history rewrite.

The new42-path nominal thread-envelope inventory passed, but does NOT prove
actual threads or preload. Native dimension inspection then found **zero
nominal axial running gap** in Idler and receiver stacks. Nut tightening had
no explicitly independent metal path around the rotating body. This is a
design risk, NOT a measured seized bearing (`revV_preload_path_fail1`). Existing
Vstatic/motion/tool PASS raw remains unchanged and is not a preload PASS.

Actual Rev W304parts, real fullassemblySTEP/STL,0BRep bulk intersections:

- Idler custom axle is inverted:3mm journalY-2.5..3/head atY3..6. M2thread
  extends toY-7.6, with actual1.55root runoutY-3..-2.5. Inner shoulder washer
  OD5/ID2.1 atY-3..-2.5 and outer washerY-5.5..-5 clamp the bracket. M2nut
  sitsY-7.1..-5.5. Preload is transferred through the3mm shaft shoulder and
  metal washers, not through POM. Nominal thrust shims0.485/0.985 leave0.03
  total rotating gap around4mm POM. Real shims must be matched and inspected.
- Receiver actual bore becomes3.040 around stationary3mm compression sleeve,
  nominal7mm long. Inner OD4/ID3.1 shims0.485 each leave0.03 around6mm body.
  Right fork has actual4.20counterboreY5..5.5 with a real0.5washer, covering
  actual1.55root thread runoutY5..5.5. Original external axle head/nut positions
  remain unchanged. Counterbore nominal radial web0.9; right journal land1.5.
  Neither is a strength certificate. Nut preload can close on the steel sleeve
  rather than the rotating receiver; actual elastic closure requires Stage2.

`revW_preload_path1` PASS: actual nominal gaps0.030000mm, actual runout
intervals and contact-plane dimensions. Conditional matched acceptance:
running gap0.025..0.035, groove midplane±0.005. With nominal radial geometry,
max axial offset0.0225 still fits max0.52wire in R0.30profile by0.0025mm and
tip exit by0.1075mm. This is NOT a full combined tolerance/dynamic proof.

Actual Wchecks:304closed meshes,31prescribed0..60° own/fixed/interFinger
motion incl retainer translation-box PASS0hits; max0.52wire/rotor PASS0hits;
40keys and21nut methods PASS. New Idler head is accessed from+Y, and its
M2nut from-Y. Observers were explicitly updated for the new sleeve/washer
ownership: these are not hidden/omitted collision parts.

Next: fully formed thread-zone inventory after modeled runouts, source-aware
stock-length limits, finite tightening-motion pilot, then current Wselfcontained
manufacturing packet and final release assessment. Prior Vpackets are
intermediate review evidence, NOT the Wmanufacturing definition.

Relevant actual commands are producer snapshots in each validation directory.
Use4GiB/420s bounds and NEW tags; do not repeat old successful exports.
