# Free-object grasp scope

Status: guided research holding subtests **EXPERIMENTAL**, full qualified grasp **NOT PASS**.

Baseline actual sphere trials use F=1e-6 and T=5e-6force·mm, identical mass,friction,
cable,pressure,damping2,dt.0005,24s and phase times. Hold loads6..14s; pressure
starts3s/off15s,cables start.5s/off16s. Full24s includes contact release/restoration.
±Fx,±Fy,±Fz,±Tx,±Ty pass bounded hold; ±Tz fail angle/moment gates. Thresholds
remain displacement.05mm,angle.01rad,velocities1e-5,relative force/moment1e-3.
Recovery is checked separately (translation1e-4mm,relative rotation1e-5rad,velocity/
angular velocity1e-5,zero contacts). Existing negative-control .001mm unchanged.

Baseline μ0,μ.001,wire OFF,bad initial placement and1e-5 overload all fail as expected.
Failing trial objective is absent, never rewarded. Cylinder and box independent
+Fx/+Tx/+Tz experiments run24s: first two hold subtests pass, +Tz fails. Other
shape/direction combinations are NOT RUN; sphere results are not copied to them.
Shape-specific analytic inertias are in each config.

Three-finger improvement has12 same-condition actual wrench trials and independent
spatial/time/history sweep. `tools/closure_frame_evaluate.py` uses relative reference
quaternions, not absolute120deg finger placement, for recovery. Both translation
and load-induced object rotation are tested against1% spatial/history and.1% dt
diagnostics, with no denominator inflation. Tiny parasitic translations can remain
relatively mesh/history sensitive; record failures rather than hide them behind angle.

Raw directories: `results/closure_20261115/trials` and `threefinger/trials`.
Their `metrics.json` contains individual hold checks, original configuration,
free object index, explicit finger guides, contact cap ratio and failure reason.
`threefinger/gate.json` requires all12 hold+tail drift+recovery; it still does NOT
certify all shapes, unguided3D fingers, full energy or real hardware.

Whole-structure moment audit additionally FAILS in the three-finger+Tz case:
unbalanced Y moment2.26295e-5force·mm despite tiny free-object residual. This is an
independent blocking gate, not included in the12 local hold/recovery PASS. See
CLOSURE_03 and `balance_audit.json`; physical closure remains unapproved.
