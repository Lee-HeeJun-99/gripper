# Thickness-aware contact continuation — 2026-11-19

## Result and limits

Started clean on development/regrip-autonomous-research at1fcc0f3. Functional
implementation checkpoint ad3acc5. No SDK changes,push,old Raw overwrite or
physics-gate relaxation. Campaign1778–1795 includes failed builds/failed
unload as well as successful tests. Source hashes,compiled snapshots,binary
hashes,commands and bounded process results live in each unique Raw folder.

This is NOT completed wrapping/lifting or dynamic thickness-contact integration.
Actual SOFA qualification below is PASSIVE geometry query purity on the existing
precise free coupon. Static contact is a separately solved fixed-sphere model.
The old energy/time/contact failures and old3-finger checkpoint1644 are preserved.

## New physical geometry

For triangle k belonging to part p:

`g_k = distance(triangle_k,c) - (R + b + t_p/2)`.

R=30mm,b=.01mm,Skin t=.05mm,Rails t=.1mm. Each triangle owns its original
topology index and a constant half-thickness. This is a conservative Minkowski
ball envelope,not an exact thin-shell surface or measured finite-strain thickness
law. By the reverse triangle inequality,it contains a facet normal extrusion
of half-thickness t_p/2. The edge/corner envelope is deliberately conservative.
No new force correction,epsilon denominator or modified Newton tolerance.
Constant radius offsets preserve existing closest-point gradient and Hessian;
the static Lagrangian tangent remains K−sum(lambda*Hgap).

The legacy near-tangent fixture is infeasible for this envelope. New trials use
an explicit world-Z sphere-centre offset+.2mm instead of+.0001mm. This is a NEW
physical fixture,NOT a numerical repair of the old model. Core volume,materials,
root map,tension and solver are matched between new original/profile routes.
Neither matched guide hardware mass nor actuation work is claimed.
1778/1780 inherited initial_geometry prose was stale;immutable original summaries
are retained with append-only SCOPE_CORRECTION.json. Numeric mount metadata and
generated C++ already record+.2mm. Later runners emit corrected descriptions.

## Independent checks

1781 smooth vertex/edge/face branch tests:gradient FD1.43975e-11,Hessian
FD1.92928e-11,rigid-motion gap error0;degenerate triangle rejected. Gates1e-8
for derivative errors and1e-12 objectivity retained. This does NOT certify a
classical Hessian at nonsmooth feature changes.

1783 default/disabled-envelope regression reproduces1755 states,owned rows,
wrenches and Newton journals BYTE EXACT (1790). Legacy behavior is unchanged.
1794/1795 fresh deformed100uN states with actual owned force multipliers pass
Lagrangian directional-Hessian FD:2.83329e-10/2.81822e-10 relative,with unchanged
1e-5 test gate. Active branches are explicitly checked for feature transitions.
1792/1793 compile failures (mixed Eigen auto expression types) remain archived;
1794/1795 fix only the diagnostic vector declaration,not physical calculations.

## Actual SOFA observer

1782 FilmEnvelopeObservedODE inherits the qualified precise tendon solver and
identical Gauss4 early/late plan. A passive accepted-step observer reads the
computed displacement state x=rest+u and audits all320 triangles. It NEVER
applies sphere force or moves an object. Same DLL with observer OFF/ON:

- 40steps,dt25us,1ms;12,800 geometric rows.
- actual.csv,Gauss4 stage CSV,Field CSV and displacement CSV BYTE EXACT ON/OFF.
- Those four outputs also BYTE EXACT to1743's qualified free coupon.
- Minimum buffered envelope gap+.031575241701816mm.
- OFF72.366s,ON67.863s under concurrent trials;NOT a speedup claim.
- SOFA v26.06.00 only,ldd guard rejects mixed SDK libraries;4GiB/480s child caps.

Build:build/thickness_audit_20261119_thickness_sofa1782/.
DLL SHA256 eece26cb93f6687ca0812e435bb31515d7789d25dbc0daa0779e15b1571326b8.
Initial1779 compile failure (unqualified Assembly/Point aliases) is preserved.
Maximum RSS was NOT separately measured in this new observer trial.

## Static structure comparison at100uN per rail

| Metric | Original route1780 | Profile4.5/outboard10,1784 |
|---|---:|---:|
| Completed load stages |64/64|64/64|
| Force residual N |9.96912e-13|7.85784e-13|
| Minimum buffered envelope gap mm |+2.84217e-14|−3.55271e-15|
| Width-mean Skin tip z mm |−5.77943|−4.76206|
| Width-mean Skin mid z mm |+1.97547|−.0637728|
| Tendon stroke mm |4.18066|7.25593|
| Active force rows |1|1|
| Minimum Skin envelope gap to actual R30 mm,all64states |+.00999999996|+.00999999995|
| Minimum wire centreline gap mm,all64states |−.0838626 FAIL|+1.118785|
| Static64-stage unload |1785 FAIL first increment|1789 PASS toT0|

New profile suppresses the midspan upward arch,but requires greater stroke and
has only one contact row. No continuous wrapping/contact area/pressure/holding
load is measured. No structural superiority or final design selection.
Wire clearance is for zero-radius centrelines at sampled accepted states only;
finite wire/guide hardware,finger–finger and self-collision remain unqualified.

1785 fresh seed passes original force/gap checks,but at98.4375uN its force
residual fluctuates near1.5–2.2e-12N and exceeds unchanged1e-12 gate through
Newton30. FAIL retained;no OS exhaustion or physical instability inferred.
1789 unload endsT0,zero force rows,gap+.031575mm,residual7.01702e-17N.
This is static zero-load equilibrium,NOT actual dynamic release/recovery.

## Evidence and next development

1791 checks15,278 inherited v14 immutable artifacts with changed=[];live edited
source/reports are explicitly excluded. v14 is not claimed to match the new live
tree. New byte ledger:reports/FILM_CONTACT_EVIDENCE_20261119_thickness_v15.json.
1770/1774 thickness failures and1748 signed-energy residual FAIL remain unchanged.
Whole energy/root work remain BLOCKED/NULL. Friction,mesh/time convergence of
the new contact law,mechanical equalizer,free3-finger grasp and lift are NOT RUN.

Next implementation:carry per-triangle radii into a separate dynamic contact
owner,including whole-surface event roots,Jacobians,closure and work using the
same geometry. Do not change only the observer or blindly remove old guards.
Qualify single-film fixed-sphere contact before free-body/three-finger coupling.
Independently investigate baseline unload residual/rounding with archived Newton
traces;do not relax force tolerances or increase tension to hide it.

Exact reproduction commands (new unique tags;these reproduce completed tests,
not new studies):

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_precise_static_contact.py --tag UNIQUE --richardson --thickness-envelope --full-load --profile-amplitude 4.5 --outboard 10 --profile-proof 20261119_precise_profile_wide10_math1772
$PY tools/film_thickness_sofa.py --tag UNIQUE_ACTUAL
$PY tools/film_continuation_evidence.py --name 20261119_thickness_v15 --verify
```

Raw root:results/autonomous_film_20261119_thickness_*. Summary/forces/geometry/
energy CSVs preserve actual units;static multipliers are N,not Ns.
1790/thickness_results.png explicitly separates independent static results from
actual SOFA passive geometry;no prescribed pose or scaled deformation.
All owned children through1795 exited;no automatic post-session execution.
