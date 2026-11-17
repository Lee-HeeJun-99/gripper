# Three-film owner cost research — 2026-11-18

Scope: actual SOFA three-film/ONE FREE sphere REST/T=0/100us contact coupon.
This is NOT closing, wrapping, lifting, frictional grasp or full-cycle energy.
All material values remain research assumptions, not physical measurements.

## Passive instrumentation

- Field-only869/870: nine physical CSVs exactly unchanged against same-DLL
  control. These field timers do not measure the custom owner's internal FEM.
- Owner872/873/875: nine physical CSVs exactly unchanged, same DLL/physical XML.
  Wall time4.253756s OFF /4.229011s ON is one pair, not a speedup claim.
  Owner step3.872180s, implicit solve2.848298s, selected geometry1.351446s,
  material force/Hessian0.550743s. Timings are inclusive/nested: DO NOT SUM.
  10560 trial candidate AD evaluations,960 constructor candidate AD evaluations,
  8535 material AD dispatches. Process-wide heap allocations NOT MEASURED.

## Query-local high-precision value reuse

Hypothesis: repeated113/334-bit squared-distance calculations inside the same
immutable query are redundant. Cache one value pair per triangle and compare
the exact same rounded differences. No state-to-state coordinate cache, no
gap/gradient/Hessian/normal change, no tolerance or precision relaxation.
Unresolved precision/independent true ties still reject. All candidate AD
evaluations are deliberately retained in this first experiment.

876 compile FAIL (duplicate new type declaration), preserved; corrected before
877. Independent877 PASS, state.csv byte-identical to baseline871. Standalone
test_precise_distance_order covers recorded fixture, cached comparisons,
90-degree objectivity, interior face and degenerate rejection.
Actual878 PASS;879 confirms ALL nine physical CSVs byte-identical to873.
880 used-row/mapped-state/whole-stage audit PASS, minimum gap-1.42109e-14mm.
Nevertheless wall time4.891899s versus4.229011s baseline is worse in this pair.
This is not statistical evidence of a universal slowdown, but DOES NOT meet
the adoption requirement of demonstrated runtime improvement. **REJECTED**:
restored original preciseOrder/selection implementation in live source.
Archived877/878 contain the tested rejected implementation and binary.
Passive instrumentation and comparison tools remain, not an adopted speedup.
The original cadba8c/3985f8b archives and evidencev9 remain immutable.
