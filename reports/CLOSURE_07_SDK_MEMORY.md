# Matched patched SDK integration and bounded memory

Status: stated two-cycle240000-step adaptive-grasp memory experiment **PASS**;
unbounded/hour-long/native-pipeline/three-finger memory certification **NOT RUN**.

Official context independently checked2026-11-15:
[SOFA PR6259](https://github.com/sofa-framework/sofa/pull/6259) changes the MappingGraph
parent ownership to break graph cycles; [issue6230](https://github.com/sofa-framework/sofa/issues/6230)
records the engine leak. These sources explain the patch, not proof of this project's
full-model memory behavior. No installed engine was overwritten.

Reuse `build/grasp_20261115/sofa_patched`, source7c18e95 plus archived official patch.
`.runtime/closure_sdk` exports headers/CMake packages and links only libraries built
from the SAME source build. New closure and frame plugins compiled against that SDK.
`environment/frame_linkage/stdout.log` verifies no installed SOFA library mixing.
Headers alone were not swapped against incompatible binaries. Existing SDK binaries
remain frozen. Initial prototype binary separately recovered, not relinked in place.

## Actual adaptive full-mechanics scene

`diagnostics/closure/MemoryReload.cpp`, `tools/closure_memory.py`, `sdk_memory`:
two independent load/initialize/120000steps/unload cycles in one process, dt.0005.
The scene contains beams,cables,pressure sliders,elastic stick contact,free object;
first24s grasp/release followed by released mechanics. State recorder removed for
I/O only; contact observer retained,stride60000. This is not empty-scene inference.

| Cycle | RSS at60000/120000 KiB | Live heap growth last60000 bytes | Loaded FD | Unloaded FD |
|---|---|---:|---:|---:|
|1|74836/74836|64|7|5|
|2|75476/75476|-128|7|5|

Second-cycle PSS71573→71492KiB,Private_Dirty15220→15220KiB; unloadRSS70376KiB,
Private_Dirty10120KiB. Residual allocator memory is not called a live leak.
Initial classifier incorrectly compared loaded/open-stream FD count to unloaded
count and marked FAIL. Original result/log retained. `memory_audit.json` separately
checks phase-stable counts and exactly two known contact streams closing; live
criterion remains<1MiB and physics tolerances are not changed. This is a documented
classifier correction, not replacement of failed experimental data.

Actual matched-SDK600-point V109 FREE was independently repeated twice in this
campaign, all nine shared metrics/all600 samples satisfy1e-10+1e-6|golden|.
Final deflection.04121379160634628mm, slip.0008228072034270895mm,
velocity−.014380704053554549mm/s. `validation_golden/{1,2}/result.json`.
Matched-SDK two-finger12wrench and new three-finger integration are separate real
experiments; old45 gates are not re-labelled as new contact certification.

New kernel ASan/UBSan/LSan PASS (`sanitizers/run_unrestricted/result.json`), external
SOFA shared libraries not instrumented. Initial ASan shadow/virtual-memory-cap
failure and sandbox LSan/ptrace failure retained. ASan-compatible run bounds physical
RSS2GiB/time60s instead of virtual address space. Production trials retain4GiB/480s
child bounds and kill/reap. No unlimited process allocation or system-wide changes.
