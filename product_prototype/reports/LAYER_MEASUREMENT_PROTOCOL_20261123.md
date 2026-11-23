# Layer coupon measurement preparation — NOT MEASURED

1202 creates a header-only SI CSV and metadata with all calibrations NULL.
No hardware was actuated/purchased,and no sample values were generated.
38 scoped software regressions1210 are not38 physical tests. Synthetic
unit-test data explicitly marked SYNTHETIC_TEST_FIXTURE cannot qualify as lab data.

Required before physical trials:material batch/thickness measurement,force
sensor calibration,displacement measurement,pressure gauge zero/span,clock
synchronization,fixture root/moment freedom,leak test,pressure safety rating.
Sensors/vendor/cost/resolution and safe load/pressure range NOT SELECTED.
Do not reuse arbitrary simulated1000Pa as a hardware operating instruction.

Sequence:unloaded→preload→load→unload→recovery. Record actual gauge pressure
(negative for vacuum),normal/bending load,tip displacement and monotone time.
Matched trials need same stack/geometry/load/history with pressure and friction
conditions declared. Static equilibrium,repeatability,slip and bending stiffness
criteria must be preregistered after apparatus resolution is known;currently
NULL,not relaxed surrogate thresholds. Free-slip/perfect-bond theory is not
pressure calibration or measured jamming. No automatic stiffness fit provided.

Tools:product_prototype/tools/layer_measurement_log.py validates schema only;
uncalibrated/non-lab records BLOCKED,emptyrecords NOT MEASURED. Even calibrated
format PASS does not qualify the mechanical test. Queue status and next task
are read via tools/research_queue.py,not a claim of unattended background work.
