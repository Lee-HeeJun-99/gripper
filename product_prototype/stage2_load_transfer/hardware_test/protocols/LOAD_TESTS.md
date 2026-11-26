# Load test execution preparation — NOT AUTHORIZATION TO LOAD

All hardware tests NOT MEASURED. No equipment was operated or purchased.
Fixture `fixtures/split_end2` contains four actual STEP/STL split grip parts;
initial `split_end1` interference remains FAIL. Revised grip geometry has no
mutual solid common; actual machine adapters, bolt preload and fixture proof
are NOT yet qualified. M3 through clamps / M4.5 adapter clearance holes are
fixture design features, NOT a declaration of a universal machine interface.

General prerequisites: calibrated force/torque and displacement sensors,
shield, secondary catch, emergency stop, approved machine adapter, actual lot
certificates, independent fixture proof. Derive T_design and tau_design from
qualified Stage2 envelope BEFORE assigning proof loads. Never use catalog
wire breaking force as the permissible load of the finished assembly.
First contact <=0.1 N is a planned setup limit ONLY after safety review, not
a currently certified safe force. Stop on fixture motion, cracking, strand
damage, loss of calibration, unexpected permanent motion or temperature rise.

| Test | Fixture / instrumentation | Sequence and acceptance to freeze before test |
|---|---|---|
| Tendon extension | Opposed split grips + verified machine adapters; 0..10 N cell, <=0.005 N resolution; clip extensometer <=5um; actual gauge length | Seat at0.1N; ramp0.1..T_design; unload; >=5 repeats. Fit EA from local gauge extension, NOT crosshead compliance. Record hysteresis/creep; acceptance depends on allowed stroke error, not an invented solid-wire E. |
| Finished-end pullout | Same grips; shield and spare specimens; camera <=0.02mm/pixel | After fixture proof, ramp to2*T_design; hold60s; migration <=0.10mm, no permanent slip after unload. Destructive test separate authorization; no passing strength inferred from untested catalog cable. |
| Split coupling slip | Actual two jaws, actual5mm D shaft and4.4mm output; fixed torque-cell adapters; 0..0.1Nm, <=0.0001Nm resolution | Record bolt torque and actual jaw gap; apply +/-2*tau_design, hold60s; relative shaft slip <=0.5deg and no permanent jaw motion. Actual adapters still required. |
| Shaft / cross pin | Actual two bearing supports, actual drum and retained pin; tension load cell at released wire tangent | Ramp T_design then2*T_design after fixture review; measure shaft displacement <=5um; residual after unload <=0.02mm; inspect bore and pin. Coupon FE does NOT waive proof. |
| Bearing rotation | Actual co-bored housing, shoulders, nuts and caps; micro torque sensor | Record actual endplay before/after load; breakaway/running torque must fit derived motor budget. No numerical free-spin limit invented before budget. Do not clamp floating outer ring. |
| Idler transfer | Actual3mm axle, shoulder, metal washers and POM idler; TWO0..10N cells, <=0.005N resolution | Measure T_in/T_out at specified direction/speed; compare journal-friction model and washer drag; record actual gaps under load. Required loss limit derived from motor margin. |
| Finger force–displacement | Actual root + terminal from Rev AA, distributed padded force applicator; two-camera shape tracking | 0.001N beam control first; increase only within elastic/material and0..60deg verified geometry domain. Record layer-end migration, root reaction, local curvature; compare both locked/free-slip models. |
| Root retention | Actual PALM/root fasteners and finite clamp; load at measured terminal point | Test distributed actual moment/force at2*qualified demand; permanent slip <=0.10mm, no cracking/rail release; bolt preload known. |
| Repeated load | Reuse qualified fixtures; force/displacement + temperature | Provisional1000 cycles to T_design, 0.2Hz; stop on10% stiffness/loss drift,0.10mm migration or damage. This screening is NOT a fatigue-life certification. |

Blank data schema: `inspection/TENSION_RECORDS.csv` (SI).
`scripts/hardware_records.py` rejects empty/NaN/mixed/reversed-time records.
It returns only VALID LOG or INVALID/NOT MEASURED, never hardware PASS.
Torque, sensor synchronization, fixture calibration and cyclic logs need
separate acquisition adapters. All numeric sensor ranges above are proposed
measurement requirements; no actual sensor purchase/specification claimed.
