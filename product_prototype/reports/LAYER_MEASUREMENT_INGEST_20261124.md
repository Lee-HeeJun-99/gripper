# Layer coupon data readiness — NOT MEASURED hardware

After113b229,implemented actual importer and8synthetic parser tests,not a new
layer-jamming performance simulation. No real readings areavailable. Baseline
Native/data-origin/material/calibration gaps remain. Do not fill templatewith
estimated pressure/stiffnessratio and call it measured performance.

CSV exactcolumns:
`time_s,specimen_id,condition,cycle,branch,steady,force_N,displacement_m,pressure_Pa`.
pressure_Pa is nonnegative measured pressure DIFFERENCE(atmosphere−chamber),
not absolute pressure;record instrument/calibration definition accordingly.
Atleast2pressureconditions,pairedcycleIDs,3distinct steady loading forces per
condition/cycle. Monotoneactualtime,finiteSIvalues,declaredbranch andsamecoupon.
Do not resample/delete failed/unstable measurements to make steady labels.

Metadata JSON requires data_origin(measured or synthetic_fixture),specimen_id,
fixture_id,operator,test_date,units:{force:N,displacement:m,pressure:Pa,time:s},
calibration_files:{force:{path,sha256},displacement:{path,sha256},pressure:{path,sha256}}.
Pathsrelative tometa;CLI verifies actualfilehashes beforeany resultcreation.
Store calibration certificates/rawzero/loadcell calibration,displacement scale
andpressure reference withoriginaltestmanifest. A hash proves identity,not
calibration accuracy/currency. Operator must independentlyconfirm instrument
range,traceability,zero,alignment,fixturecompliance andvaliddate.

Importer reports loadingcompliancefit+offset/residual+pressure range percycle,
NOT EI/jamminggain/Holding/hardwarePASS. Steadylabels areoperator annotations,
not independent equilibrium proof. Unloading/hysteresis data retained but not
fit into a loadingline. No pressureuniformity/friction/shear-lag assumption.
Realdata output remains NOT QUALIFIED BY IMPORTER. Synthetic fixtures always
NOT MEASURED hardware and never enterproductionphysics calibration.

Useunique resulttags only:
```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/tools/layer_measurement_ingest.py --input ACTUAL.csv --metadata ACTUAL.json --tag NEW_UNIQUE
/home/ubuntu/miniconda3/envs/robot_ws/bin/python product_prototype/tools/test_layer_measurement_ingest.py
```

Requiredexternalwork:build/calibratefixture,measure actuallayer thickness and
count,free length/clamp compliance,pressure leakage/field,load-unload repeat
cycles,material/fatigue andambientconditions. Fit uncertainty/repeatability
BEFORE proposing a pressure/friction law or transferring to3FingerNative.
Do not buy/operate hardware withoutapproval. No measured stiffnessselected.
