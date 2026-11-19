# Extended local arithmetic experiment (not a production replacement)

Compile every translation unit of a separate standalone executable with
`REGRIP_FILM_EXTENDED_AD`. AD27/AD9 values, gradients and Hessians and the
projected element assembly use long double; public q/v and the linear solver
remain binary64. Never exchange these AD objects with a default-precision
module or mix this private compile-time ABI with an installed SDK.

Campaign1734 passes the original FD/objectivity/balance gates. However1732
still fails the1e-24Ns Newton test at0.9ms, and combining increment stage
variables with this arithmetic in1736 fails at0.85ms. This is NOT an accepted
precision remedy, performance optimization, SOFA implementation or grasp model.
Default compilation remains double;1739 reproduces1714 metrics EXACTLY.
