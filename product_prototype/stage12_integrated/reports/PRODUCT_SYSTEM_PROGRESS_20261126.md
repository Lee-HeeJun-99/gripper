# Product-system continuation — 2026-11-26

Official baseline: **RevAA**, unchanged. Latest actual candidate:
**revAJ_idler1, 250 parts**, NOT ADOPTED. Integrated digital release remains
**NOT QUALIFIED**. No Stage3/grasp run, hardware, purchase or push occurred.

## Actual product changes

| Candidate | Actual implementation and result |
| --- | --- |
| AE1/2 | Direct motor friction-drum assembly;63/51 actual nominal interference pairs. FAILs retained. |
| AF6 | Relocated motor, plate, real fasteners and finite wire;238-part full STEP. Nominal collision and independent BRep/STL/integrals PASS. Input-supported bearing gives parallel torque path: protection topology FAIL. |
| AG6 | Actual fixed hollow spindle/bridge, inner-ring clip, front input collet and one friction face.253 parts. No nominal interference;48 drive/slip poses, closed STL and geometric integrals pass. |
| AH2 | Shared22mm motor/spindle register,5mm replacement motor plate, longer real motor screws,3mm ground spacers and finite base-head relief. Nominal geometry, entire clamp stack and prescribed motion pass. |
| AI1 | Same drive/Finger locations, full290mm Palm annulus replaced by original230mm body plus3 rounded local tabs.253 parts. Strict Palm subset and all six mount footprints proven. |
| AJ1 | Larger M3 Idler runout,2.38mm neck with0.1mm fillets, integral metal shoulder.3 loose shoulder washers removed:250 parts. Actual journal/shims retain0.03mm nominal running gap. New actual BRep/STL, metal-stack and prescribed wire checks pass. |

All assemblies and changed STEP/STL actually exist. Final complete candidate
inventory: `bom/revAJ_identity1/CANDIDATE_BOM.csv`. Changed geometry does not
inherit old machining definitions or old M2 Idler procurement specifications.
Final actual geometry: `cad/exports/revAJ_idler1/ASSEMBLY.step`.

## Product contribution, not test-count promotion

The separate rigid two-shaft coupling is absent from these candidates. The
ground-supported output bearing removes the particular input/output bearing
seizure bypass in the declared graph. This does NOT certify a torque maximum.
Actual rear compression spacers close the previously unmodelled5mm mount gap;
their full annular seating was verified, not inferred from a collision-free pose.

The common pilot replaces bolt-float centering: declared interface play bound
0.070mm; minimum proposed shaft/tube radial clearance0.145mm; remaining
0.075mm is **unallocated** runout/deformation budget, not a measured margin.
Pilot tip/boss axial gap is at least0.150mm under the declared design intervals.
Manufacturer pilot-to-shaft runout, actual machining and loaded deflection are
not qualified. Shaft engagement is4.2..6.2mm, nominal5.2mm. Earlier6.2mm
"nominal" labels refer to the maximum-length CAD envelope and are superseded
by `validation/alignment/AH_pilot_bounds2`.

Palm volume317077.009→201555.597mm³: **36.433% reduction**. At illustrative
2700kg/m³ this saves0.311908kg; actual material/mass is NOT measured. The
entire three motor-foot contact footprints, not only bolt annuli, retain their
previous supported area (about515.383mm²/foot). Local/global strength is separate.

AJ's same-moment nominal neck stress ratio is0.276226 relative to the1.55mm
reference neck. This is a geometric section-modulus comparison, not a stress
concentration, thread-root, fatigue or material-strength PASS.

## Actual physics and failures

- Actual AD distal PET fragment first meets the finite stop at1.8mm advance;
  at2.0mm its intersection is0.36mm³. This is not a whole deformed Finger test.
- Actual root projected areas: PET405.06mm², Rail51mm² each. Independent
  friction-network LP and seven-cut bounds agree. Under the **prior conditional**
 39.1408N balanced layer-force case, required `mu*N` is19.5704N despite zero
  net axial force. Actual friction, preload and current Finger forces are unknown.
- Actual RevAI tab STEP, finite1N washer load, assumed70GPa/nu0.33, P2 FEM:
  meshes3/2/1.5mm pass equilibrium, residual, energy, volume and element checks.
  Finest compliance2.203312e-7m/N; force residual norm<1.6e-12N.
  Response refinement0.128372% passes1%, **unsmoothed stress8.833449% FAILS**.
  Peaks are within0.037mm of the artificial clamped cut. No data are trimmed;
  actual whole-Palm mounting/contact is the next physical question, not a blind
  finer-mesh sweep. No full-Palm or material strength is certified.

After that failure, actual development moved to the M3 integral-shoulder Idler,
not another generic rod/dt/mesh search. Its metal bypass and nominal running
gap are verified geometrically; loaded free-spin and actual thread fit are not.

## Protection still unresolved

Custom clutch spring/friction/preload are unqualified; the CAD is an unloaded
installation candidate, not a calibrated clutch. The one-face AH/AJ torque law
must not reuse AF's two-face normal-force calculation. Actual motor axial load,
minimum-engagement collet closure and output-bearing load/tilt need verification.

A distinct complete catalog candidate was checked in the
[WM Berg metric catalog, MG37](https://www.wmberg.com/documentation/metric-catalog/section-g_metric.aspx?ext=.pdf):
JH-1M publishes0.064±0.007Nm,3mm bore,16mm OD and26.7mm length. It is NOT
installed: the5mm motor interface does not match. Parsed mounting-thread text
was ambiguous; screenshot cache failed and direct PDF download returned403.
No special bore, price, stock, internal CAD or thermal/fault rating is invented.
The interval gives a6.359N catalog static reference at11.165mm radius; the
conditional jam model gives about11.75N even at zero initial speed. Actual
temperature, inertia, wire EA and transient maximum remain unqualified.

## Evidence and execution

Latest candidate readiness: `validation/integrated/AJ_readiness2` uses the
unchanged existing Stage2 gate with the actual AJ identity, not RevAA hashes.
Stage2's22 system criteria and a same-revision full Stage1 release are missing.
Hardware/manufacturing/power statuses are separate, not fabricated digital PASSs.
Earlier readiness1 had an overbroad hardware warning in its error list;
readiness2 separates hardware status without changing frozen digital criteria.

All previous RevA–AD, AA release, old failures and Raw remain unchanged.
Intermediate new CAD is preserved locally with source/summary/hash manifests;
final referenced AH/AI/AJ STEP/STL is saved. No raw CSV is added.

CAD: robot_ws Python, OCP7.9.3.1.1 in `/tmp/regrip_stage1_ocp`.
FEM: separate `/tmp/regrip_stage2_fem`, Gmsh4.15.2, scikit-fem12.0.2,
NumPy2.2.6/SciPy1.15.3. Each child≤4GiB/420s; one BLAS thread.
Initial FEM JSON-int failure and two wrong-environment imports are preserved;
they are not physics FAIL/PASS. Corrected FEM stores full P2 state/load vectors.

No external automatic calls were added. Previous6 calls are exhausted;
service3 was rechecked inactive/dead/MainPID0. Manager, Supervisor, STOP and
budget controls were not modified. READY work remains; this is not completion.
