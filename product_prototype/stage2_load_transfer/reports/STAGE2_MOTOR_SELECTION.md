# Motor remains a candidate, not powered-release selection

[Manufacturer A0648](https://files.omc-stepperonline.com/17HS15-1504S1_Full_Datasheet.pdf)
specifies17HS15-1504S1 rotor54g·cm² (=5.4e-6kgm²), holding0.45Nm,
phase1.5A, dynamic axial10N and radial21N at20mm shaft location.
These are distinct quantities. Neither holding torque nor the6000h statement
at24V/300rpm supplies the missing running torque/thermal envelope.
No torque curve for a different suffix was substituted. Direct PDF download
returned403; manufacturer web-readable PDF and product page were inspected.

Actual seated-radius scenario R11.165..11.190mm gives tau=T*R before losses.
Conditional no-object closing demand from the current reduced model is NOT
the required motor torque for100g grasp. Driver, acceleration, bearing drag,
coupling slip and actual load duty remain to be qualified. No purchase/power.

Fixed-axis two-inertia results are in `validation/integrated/torsion_dynamic1`;
the model uses actual geometric inertia integrals plus nominal densities and
explicitly excludes several rotating items. It does not qualify motor heating
or full assembled inertia. Rigid coupling alignment needs separate load limits.
