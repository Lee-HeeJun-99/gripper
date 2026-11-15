# BEAM13 — optional measured-state replay

Status: **PASS recorded-state batch playback; GUI NOT RUN.**

`tools/beam_visualize.py` verifies the newTz_v2 state/contact artifacts before
building `results/beam_20261115/replay/replay.json`. Existing
`scenes/closure_replay.py` displays actual measured6layer/finger poses,actual
wire guides,free sphere and sampled contacts,with commanded jamON/OFF labels.
Coordinates are never synthesized into a claimed physics result.

The generated batch replay completes withoutERROR and verifies frame progression
andON/OFF events using the working isolatedCPython3.12/SofaPython3 environment.
It is playback,not a second physical simulation or independent energy proof.
No GUI is opened for every trial or optimization. No web dashboard added.

Exact GUI argv and necessary environment are preserved in replay/gui_command.json
and environment.json. Execute them only when a display is available,using
`GRASP`/`CLOSURE` replay solely as an optional visual diagnostic. The displayed
candidate is EXPERIMENTAL +Tz research,not a certified Pareto grasp design.
