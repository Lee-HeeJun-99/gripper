# Does jamming improve grasp in this experiment?

Status: actual comparison **PASS** as an experiment; claimed improvement **NOT DEMONSTRATED**.

Eight separate SOFA runs: pressure0/.0001/.001/.01 with identical two-finger
geometry,wire.001,mu.3,+Fx1e-6 or1e-5,18s. Pressure is an assumed model force/mm²,
not calibrated physical vacuum/PET friction. `results/closure_20261115/jamming.json`.

| Pressure | Load | Maximum displacement mm | Relative force residual | Holding subgate |
|---|---:|---:|---:|---|
|0|1e-6|.000931712043041|1.93481e-6|PASS|
|.0001/.001/.01|1e-6|.000931672033502|1.93352e-6|PASS|
|0|1e-5|.162582570568|.70072628|FAIL|
|.0001/.001/.01|1e-5|.162663697512|.70088219|FAIL|

Positive-pressure results are identical here: pressure sliders already stick at
the lowest positive test. Low-load ON/OFF difference≈.0043% is below measured
mesh variation≈.6%, so cannot support a meaningful grasp benefit. High-load
failure is not assigned stiffness or a favorable objective. Tested holding limit
is bracketed between1e-6 and1e-5, not an identified maximum. Torque support and
contact topology can dominate even when internal bending stiffness increases.
No claim that increasing pressure necessarily improves grasp, or that30mm stiffness
ratio certifies100mm friction/contact performance. Three-finger pressure/ultimate-load
sensitivity and cyclic physical hysteresis remain separate research tasks.
