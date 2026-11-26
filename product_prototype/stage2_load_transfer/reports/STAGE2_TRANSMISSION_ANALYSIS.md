# Conditional force transmission

`validation/integrated/transmission1` solves two-bearing reactions and
plain-journal idler drag under the0.05/0.25/0.5N in-domain force controls.
Actual bearing centresY−6/+11.5mm; cable planeY0. Equilibrium residuals pass
the frozen force/moment limits. This initial radial map omits component weight,
washer drag, actual coupling alignment/preload and shaft flexibility.

Idler rotates on a3mm journal. Fixed-capstan exp(mu*wrap) is NOT the correct
rolling-idler law. The implemented journal model balances
(T_in−T_out)R = mu_journal*R_journal*|T_in*u_in+T_out*u_out|.
Mu0/0.1/0.3 are assumed sensitivity conditions, not measured coefficient bounds.
Finite nominal pin double shear and1.55mm axle-runout bending references
are demands only, not stress-concentration/fatigue certificates.

Coupling required normal force tau/(mu*r_grip) is reported for assumedmu0.1.
This is NOT measured bolt preload or a slip capacity. Actual split-jaw contact,
thread stripping and motor/winch alignment are subsequent structural tasks.
No intermediate quantity is treated as continuous-system capacity PASS.
