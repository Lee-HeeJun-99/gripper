# BEAM12 — matched SDK with new full scene

Status: **PASS bounded120000steps/two reload cycles;240000single-run/hours NOT RUN.**

Existing SOFA source7c18e95 with official MappingGraph weak-parent fix reused.
New beam is compiled against matched headers/libraries; fresh clean ldd logged.
Installed SDK remains untouched. Native collision research is a separately
rebuilt installed-engine experiment, not mixed into this patched SDK process.

`tools/beam_memory.py` and `diagnostics/conservative_beam/Memory.cpp` run the
new conservative beam,6layers,3cable pairs,pressure,friction and free object in
one process:two60000step/30s simulation cycles with unload/reload. Physics
sequence through24s is retained; state-recorder I/O is removed and other output
stride60000. This is not a repeat of the prior empty/minimal scene certificate.
Execution478.276s under the unchanged480s/4GiB child limit.

MappingGraph18nodes percycle,retained weak targets0 afterclear for both.
Live heap last30000steps changes−185616/−185632bytes; unloaded heaps821424/
823040bytes (difference1616). FD8loaded/3unloaded in both cycles.
RSS loaded tail≈77864/78620KiB,unloaded76656/77552KiB. RSS cache retention is
reported separately from live heap and surviving graph ownership.
The late plateau is after release, not a continuous persistent-contact soak.
All samples include PSS,PrivateDirty,mallinfo2 and process provenance in
`results/beam_20261115/memory/summary.json` and stdout.

This bounded test does not establish zero leaks in all external engines,
240000consecutive steps,several hours,all shape/contact models or every solver.
No external private members were forcibly freed. Child-process limits remain.
Sanitizers cover the new forcefield translation unit only; BEAM02 retains the
initial sandbox LSan failure and successful unrestricted bounded rerun.
