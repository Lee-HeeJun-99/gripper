# Prepared tests, not executed hardware

Actual four-part split-grip STEP/STL: `hardware_test/fixtures/split_end2`.
Independent BRep/STL/maximum-end loading-path audit:
`hardware_test/inspection/fixture_geometry1` (geometry only).
Nine bounded test protocols: `hardware_test/protocols/LOAD_TESTS.md`.
Blank tensile and alignment records: `hardware_test/inspection/*_RECORDS.csv`.

Analysis: `scripts/hardware_records.py`, `scripts/alignment_records.py`.
Empty records actually returned NOT MEASURED. Synthetic valid logs may validate
a fit/budget only, never hardware PASS or power authorization. Software controls
also test nonfinite data, excessive offset and excessive measurement uncertainty.

Still needed: actual calibrated instruments/fixtures, machine adapters, guards,
torque/Root fixture qualification, clamping preload, approved proof limits and
supplier lot data. The current protocols and sensors are engineering requirements,
not claims of purchased equipment or performed physical tests.
