# Actual separated SOFA scheduling pilot

Inherits exact50ms stationary FREE restore and explicit200→800us dt transition.
One step only; `filmWorkers=1|3` changes scheduling, not physics. Public graph
access, commit and journals remain on the main thread. New output magic is
`REGRIP_STATIONARY_GAUSS_PARALLEL_PILOT_V1`; no resume reader is qualified.

Reproduce with `tools/film_stationary_gauss_parallel_sofa.py --tag UNIQUE`.
1631 PASS requires byte-exact physical CSV/checkpoints across six same-binary
alternating-worker trials and physical CSV equality with qualified1618.
Full recovery, contact/friction, energy and grasp gates remain unresolved.
