# Optional measured-state SOFA replay

Status: headless replay **PASS**; interactive GUI **NOT RUN**; no physics certification.

`scenes/closure_replay.py` extends original replay separately for all six layers of
three fingers. Full2401 recorded frames from actual pilot+Tz24s are replayed with
world positions/quaternions,actual cable offsets,actual object pose and sampled
contact patch points. No fake trajectories. It supports sphere visualization only;
cylinder/box are explicitly rejected rather than drawn as the wrong geometry.
Jamming phase is a commanded schedule indicator, not measured vacuum pressure.

`tools/closure_visualize.py` checks every source artifact hash before exporting.
`threefinger/replay/result.json`: all frames loaded/replayed,error-free,ON/OFF phase
markers observed. The replay does not rerun Beam/contact dynamics and does not make
the pilot a fully certified candidate. Geometry skins are not fabricated film CAD.

No GUI was started for campaigns/optimization. Optional command and required isolated
CPython3.12 environment are in `threefinger/replay/gui_command.json` and
`environment.json`; invoke that saved argument list with those variables in a GUI
session. Existing `scenes/grasp_replay.py` and `tools/grasp_visualize.py` remain unchanged.

Prepare a new replay namespace/source by adapting the small exporter; do not overwrite
the measured pilot output. GUI results are for inspection only, not a numerical gate.
