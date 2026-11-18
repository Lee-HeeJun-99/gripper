# Bounded actual lateral release owner

This separate SOFA module reuses the existing material-edge dynamics,
projected mass and `AdmissibleRelease.h`; it does not modify the SDK.
`tools/film_lateral_release_sofa.py` binds the immutable actual27ms
checkpoint1509 and qualified128-subinterval independent reference1518.

The old contact is followed by compressive collocation, acceleration-LCP
RK4 release and a free implicit-midpoint remainder. The 32/64-subinterval
normal-velocity failures are preserved. The128 reference satisfies the
existing gap/velocity/momentum bounds; this is not whole time convergence.
The exit bracket is a numerical admissibility boundary, not a certified
continuous-time contact-death root.

Input schema: REGRIP_LATERAL_CONTROLLED_V1.
Output schema: REGRIP_LATERAL_FREE_V1, with no active rows and released
material-edge geometry. Edge birth history is explicitly UNMEASURED.
It is never replaced with an invented birth time or an old route's history.
`LateralFreeODE` now reads this schema, validates exact public mass/root/time,
and checks the numerical dense path for reimpact before committing. It is
bounded to the original C2 unload end30ms; no arbitrary clock or step reset.
1527 actual27.2..27.6ms agrees exactly with the independent midpoint reference;
1530 mid-checkpoint suffix reproduces all q/v, stage rows and full checkpoint
tokens exactly.1531/1532/1534 extend the actual separated trajectory to30ms.
The malformed-schema test1528 rejects six active/topology/history/clock cases.
1525 missing-header compile and1526 component-registration failures are
preserved; neither is a completed dynamics trial.

The actual journal records pre-contact stages, all512 RK evaluations,
free remainder and a sum-of-segment momentum-residual norm bound.
The latter is not a separately measured global vector balance. Root work,
whole energy, wrapping, holding and lifting remain unqualified.
