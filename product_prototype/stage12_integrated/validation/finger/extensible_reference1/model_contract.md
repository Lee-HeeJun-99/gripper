# Finite extensible rod reference contract

Material coordinate s, planar tangent t=(cos theta,sin theta), independent
engineering axial strain e, and compatibility r_prime=(1+e)t. Energy is
integral(EA e^2/2 + EI theta_prime^2/2) ds - F dot r(L).
Root position and theta are fixed. Tip force is a spatial dead load; tip moment
is zero. Axial stationarity gives e=F dot t/EA, with no prescribed axial tip
position. The reduced potential is integral(EI theta_prime^2/2 - F dot t -
(F dot t)^2/(2 EA)) ds. Additive position origin is fixed at the root.

The discrete formulation uses nodal theta and midpoint strains and tangent;
positions follow compatibility. The independent continuous BVP instead solves
x,y,theta,M with M_prime=-(1+e) F dot normal and theta_prime=M/EI. Its mesh and
collocation algorithm are independent of midpoint energy stationarity.
Natural zero terminal moment is represented weakly in the discrete energy,
not by requiring the final midpoint curvature itself to vanish.

Free axial tip is a control. Real guide reactions, coupling and contact must
enter the uncondensed virtual work before any strain condensation is reused.
No claim of equal curvature, actual clamp slip, actual geometry contact,
full assembly energy, stability proof or system release is made here.
The engineering-strain energy is a declared rod constitutive approximation;
objectivity does not establish actual-lot material accuracy.
