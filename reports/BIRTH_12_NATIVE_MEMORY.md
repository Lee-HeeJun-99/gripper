# Birth validation 12 NATIVE MEMORY

Status: NOT RUN new Native campaign; EXPERIMENTAL bounded process memory

New campaign: `results/birth_20261115/canonical_v8`; frozen build `build/birth_20261115/v8_clean`. All quantities are research simulation/mathematics, NOT measured PET or hardware data. Earlier v7 results remain separate.

Environment: Ubuntu22.04.5, Linux6.8.0-138-generic, GCC11.4, CMake3.22.1, Python3.10.20. Patched matched SOFA26.06 SDK aliases resolve to the same build, see environment/summary.json.

Birth plugin SHA256 `27b21bb08d0db153c21465b3e3d92e19c62c09b73dc0385fea975f6a895cd0d2`; generated component SHA256 `c23dddd96b5a722427068f7a9a1dfde737de015e38cc3ae5db438053d3fa259b`. Beam SHA256 `52263d3d0a2e8e49a166ec17077c9c58d2d80f46dd51f304b6547681df146b6f`; SDK driver SHA256 `274a9de055d3c3dec07c03ca52866cf66332765500a697715df251ce4a4f875e`.

Existing Native contact is preserved as a different constraint law; no new Native force-equivalence claim. Actual new children have bounded4GiB/default480s; profile-justified single900s exceptions are recorded, not global defaults. Resource samples use same-parent verified child PIDs and include RSS/PSS/Private_Dirty/FD when available. Completed144000-step quarterdt is reported only if its raw metrics exist. No240000-step sustained-contact or hours-long leak-free claim; LSan is BLOCKED by ptrace, independent mathematical ASan/UBSan PASS is not engine-wide sanitizer coverage.

Actual canonical quarter-dt memory observation:

```json
{
  "status": "EXPERIMENTAL",
  "sample_count": 378,
  "monitor_error": null,
  "rss_range_kib": [
    77832,
    78740
  ],
  "pss_range_kib": [
    31334,
    75077
  ],
  "fd_counts": [
    10
  ],
  "tail_rss_bytes_per_step": -0.5422663211156364,
  "tail_live_heap_bytes_per_step": 3.7145689250894725,
  "engine_steps": 144000,
  "unload_heap": [
    840448,
    840448
  ],
  "scope": "tail may include release; not sustained-contact/hours or complete allocation traceback"
}
```
PSS depends on concurrent processes sharing engine pages; its range alone is not live-heap growth. A finite tail slope spanning contact/release is not a sustained-contact plateau certificate.
