# HISTORY 12 — bounded memory/performance

**EXPERIMENTAL bounded observations**, not a whole-engine no-leak certificate.
All new physical trials use the existing matched MappingGraph-patched SDK and
locally rebuilt new plugin; installed SDK is not overwritten or mixed.

`history_evidence/memory.json` extracts actual RSS,mallinfo2 arena-live,mmap and
unload observations from each trial log. It explicitly states executed step
counts. The halfdt run reaches72000steps; this does not mean72000steps of
continuous contact. End-event buffers and allocator cache are distinct from
live-object ownership; arena-live+mmap is only a proxy, not a full allocation
trace. PSS,FD and new120000/240000 sustained-contact soak are NOT RUN unless
the corresponding final actual trial record explicitly contains that count.

New prescribed own-kernel ASan/UBSan passes; LSan is BLOCKED by ptrace
restrictions. SOFA itself was not sanitizer-rebuilt. ASan uses hard2GiB RSS/60s,
not a4GiB virtual-address cap that would invalidate shadow allocation.
Default child limits and the two measured900s exceptions are documented in
HISTORY04. Profiles are not equilibrium or long-term memory passes.
