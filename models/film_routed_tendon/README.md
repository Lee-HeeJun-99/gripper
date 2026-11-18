# Experimental distributed tendon route

Separate `FilmRoutedTendon` and `FilmRoutedPlanODE`; original Assembly layout,
legacy ForceField, mappings and historical binaries are preserved. Generated
Field/API sources live only in immutable campaign source archives. The guarded
generator records original/generated hashes; the installed SDK is not modified.

Material coordinate s=x/100mm sets guide eccentricity
`e(s)=5-4*amplitude*s*(1-s)` mm, amplitude either0 or4.5mm. Original objective
guide AD, reference roots, shell/rail/attachment physics and projected public
mass are reused. Five guides per rail. Tendon force is the gradient of actual
piecewise cable length, not an invented skin load. Skin is still driven through
Rail→Attachment. Route parameters are frozen; runtime mutation is rejected.
The external tension potential uses gauge `T*(combined length-200mm)`; this
is NOT stored energy. The new rest route length is201.00833432mm at amplitude4.5.
Private sampled-work initialization uses that rest length; the owner admits
rest-start only. Arbitrary deformed checkpoint restoration is NOT supported.

Independent force/Hessian/objectivity tests and ACTUAL SOFA Force/dForce/matrix/
query-purity APIs passed in1240. Actual XML dynamics profiles1242/1243 match
standalone q/v/time and stage inputs EXACT; amplitude0 preserves old8step
trajectory EXACT (1246). This is NOT wrapping, grasp or full time certification.
The default original zero-tension cable terms are calculated then discarded, preserving
the original core implementation. Their degeneracy guard remains an additional
conservative restriction; this is not a general production large-wrap model.

`film_routed_build.py --core-only` is a SEPARATE performance experiment. Its
guarded generator extracts the original core method body verbatim into an
ephemeral derived Assembly and removes only the discarded zero-tension cable
loop. No original kernel/Assembly layout/SDK is modified. Generated sources
and hashes are archived. The extraneous old-cable degeneracy rejection is
absent in this variant; no large-wrap domain qualification is implied.
1258 math/actual API and1260 profile passed;1264 shows ALL50ms physical CSV
bytes identical to the default variant. However actual runtime increased
84.111→89.054s in that comparison,while reference decreased94.351→92.184s.
Thus this is NOT ADOPTED as a speed improvement;default remains unchanged.

Initial fixed R30 sphere overlay: original5mm-offset wire centerline intersects
the sphere by2.607968mm, whereas this quadratic route has0.260208mm centerline
clearance (1238). Finite cable radius, guide bodies/mass, friction, self-collision,
moving geometry clearance and manufacturability are NOT qualified. The new
core volume is unchanged; total hardware volume/mass and work are not matched.
Do not use old triangle contact PASS as cable/guide clearance certification.

Reproduce with NEW tags only:

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_routed_build.py --tag UNIQUE_BUILD
$PY tools/film_routed_run.py --tag UNIQUE_PROFILE --amplitude 4.5
```

Runner currently explicitly binds qualified immutable build1240; inspect its
source/binary/SDK guards before using a different provider. All children use
4GiB and480s (compilers120/180s). Full run requires a measured same-route profile.
