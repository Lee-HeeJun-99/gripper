# Experimental distributed elastic attachment

Separate candidate; original five-clip lateral model is unchanged.
`Kernel.h` reuses the validated film/rail energies and the 5mm normal,
6mm outboard tendon route. The generated `Step.h`, SOFA Field and owner
are archived by `tools/film_distributed_attachment_build.py`.

- Mode 0 delegates exactly to the original five clips per rail.
- Mode 1 is a mathematical comparison only: 21 trapezoidal stations;
  its unconstrained attachment stiffness differs from the baseline.
- Mode 2 preserves the root clip at .001N/mm and distributes the original
  free stiffness sum .004N/mm over 20 stations, 5..100mm. Nominal total
  stiffness remains .005N/mm per rail. These are elastic joints, not
  rigid ties or a layer-jamming law.

Core volume, constituent material, mass, route and no-object C2 input
are matched. Adhesive/fastener volume and mass are NOT modelled; actuator
work is measured, not constrained equal. Material values are assumptions.

Campaign1504 API and1514 mode-zero dynamics match the old model exactly.
Campaign1515 actual 50ms mode-two coupon matches its independent integrator
at all stored states/stages. This is NOT time/mesh/contact certification.
Mean tip bends more and tendon work decreases, but centre-tip bending
decreases and transverse tip warp increases. No wrapping superiority,
holding, lifting or final design selection follows from these results.

Reproduce with unique tags and the source-bound provider1504 using
`tools/film_routed_run.py --design distributed --amplitude 2`.
The legacy CLI amplitude is dimensionless attachmentMode here, NOT mm.
