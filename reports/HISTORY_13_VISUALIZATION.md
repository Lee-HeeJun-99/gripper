# HISTORY 13 — optional measured-state replay

`tools/history_replay.py` creates `results/history_20261115/replay/` from the
actual repeated24s SOFA state, using the existing `scenes/closure_replay.py`.
Headless replay checks scene loading,measured frame9 and commanded ON/OFF
markers; final status is in `replay/metrics.json`. The generated
`gui_command.json` and `environment.json` support optional SOFA GUI playback.
GUI is NOT automatically launched; no optimization trial runs a GUI.

Finger/object poses and contact marker positions are real saved states. Markers
come from normal quadrature, not a complete tangent wrench distribution.
Commanded pressure labels are not a measurement of physical vacuum.
Replay uses installed SofaPython3 with its own isolated CPython3.12 runtime;
it does not mix that SDK into matched headless physics and is NOT a physics gate.
