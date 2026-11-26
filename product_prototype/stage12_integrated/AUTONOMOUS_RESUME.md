# Resume

Confirm actual Git HEAD/status first. Read CURRENT_BASELINE and RELEASE_STATUS.
Current integrated result is NOT QUALIFIED; no Stage3 handoff authorization.
No background runner exists. Do not regenerate RevAA/AB or old analyses.

Source reconciliation: scripts/baseline_registry.py --tag NEW
Gate: scripts/integrated_release_gate.py --tag NEW (expected exit2 currently).
Software controls: scripts/gate_controls.py --tag NEW.
Physics: scripts/jam_energy.py --tag NEW; existing jam_energy2 already completed.
All paths relative to product_prototype/stage12_integrated; Python robot_ws.

READY tasks remain in INTEGRATED_TASKS.json. Inspect actual outputs before
running anything; never reuse result directories. Hardware remains unmeasured.
