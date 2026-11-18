# Force-only assembly candidate

Uses the original AD2 element calculations and identical force accumulation
order. Only unused global Hessian allocation/assembly is omitted. It is not
the rejected gradient-only AD replacement. No baseline model is modified.

Probe1610 force bits and subsequent full Hessians match exactly across three
actual50ms-derived states. Alternating12-query totals:full .921053s,value
.848999s (kernel-only7.82% reduction in that run). Heap allocations are not
measured. This is NOT end-to-end SOFA speedup and has not been integrated into
the physical owner;actual state/force/energy/runtime A/B remains required.
Compile failure1609 from the wrong Element namespace remains preserved.
