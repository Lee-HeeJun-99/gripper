# Matched-source SOFA diagnostics

Installed SOFA is NOT modified. `MappingGraph-v26.06.patch` records the exact
three-file changes applied to source commit
`7c18e95d5c5f2839079892c69e7d89a313c79603` in this campaign. It implements the
weak-parent lifetime fix from [SOFA PR6259](https://github.com/sofa-framework/sofa/pull/6259).
SOFA source/changes retain the upstream LGPL license; the original official patch
is separately preserved in reports/grasp_evidence/official_PR6259.patch.
Do not apply only headers to a binary SDK: `parents` changes type/API/layout.

Source archive is in `.runtime/sofa-source.tar.gz` (hash in GRASP manifest).
Extract it to a **new** project-local directory. Apply this patch with `patch -p1`
from that new source root. Existing `.runtime/sofa-source` is already patched;
the reverse dry-run succeeded on all three files. Do not patch it twice.

Configuration skeleton for a **new** build directory (absolute paths recommended):

```bash
cmake -S .runtime/sofa-source -B build/grasp_sdk_rebuild_01 \
  -DCMAKE_BUILD_TYPE=Release -DSOFA_BUILD_TESTS=OFF \
  -DLIBRARY_SOFA_GUI=OFF -DLIBRARY_SOFA_GUI_COMMON=OFF \
  -DAPPLICATION_RUNSOFA=OFF -DAPPLICATION_SCENECHECKING=OFF \
  -DMODULE_SOFA_COMPONENT_COLLISION=OFF -DMODULE_SOFA_COMPONENT_CONTROLLER=OFF \
  -DMODULE_SOFA_COMPONENT_HAPTICS=OFF -DPLUGIN_SOFAPYTHON3=OFF \
  -DSOFA_EXTERNAL_DIRECTORIES="$PWD/diagnostics/grasp" \
  -DREGRIP_MATCHED_DIAGNOSTICS=ON -DREGRIP_MATCHED_STRUCTURAL=ON \
  -DREGRIP_MATCHED_GRASP=ON -DREGRIP_BEAM_PROBE=OFF
cmake --build build/grasp_sdk_rebuild_01 --target \
  memory_lifetime graph_probe ReGripPatchedDiagnostics ReGripStabilization \
  ReGripCompensated Sofa.Component.SolidMechanics.FEM.Elastic \
  Sofa.Component.MechanicalLoad Sofa.Component.Mapping.NonLinear \
  Sofa.Component.Playback Sofa.Component.Constraint.Projective -j4
ldd build/grasp_sdk_rebuild_01/bin/graph_probe
```

All SOFA_FETCH/unused plugin options were OFF; exact resolved flags are in
`reports/grasp_evidence/patched_CMakeCache.txt`. Inspect them before any new
configuration; do not enable network fetch or GUI unnecessarily. The skeleton is
a reconstruction command, not a claim that this exact new directory was built.
Actual executed commands/logs/build cache and binaries are in the campaign.

The matched native driver takes `SDK_ROOT SCENE STEPS DO_GRAPH_PROBE [PLUGINS...]`.
Load only project plugins rebuilt in that same SDK. `ldd` must not resolve installed
SOFA libraries. Minimal memory result does not certify all collision/Python/GUI
scenes. Default distributed-SDK experiments remain bounded child processes.

BeamEnergyProbe is independent: candidate `.5*d*Klocal*d` is compared with actual
addForce by finite differences. Successful diagnostic execution does not validate
that candidate as an exact corotational potential (see GRASP_05_ENERGY.md).
