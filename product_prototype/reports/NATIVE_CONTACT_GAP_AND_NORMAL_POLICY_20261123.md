# Read-only Native gap/normal probe1211–1218

Did not stop at planned READY task. Implemented a new read-only BaseObject,
NOT ForceField/contact/ODE solver. Reads actual public Native constraint
problem dFree,W,f and rigid q/v/free state/J at build/solve/accepted phases.
InstalledSDK-only build1211 configure0.168s/compile3.011s;frozen source,
CMakeCache,binaryhash guarded. Reusable cad/build_contact_gap1211/
libReGripContactGapProbe.so. No SDK files modified. Deprecated BaseObject
warning preserved,not a failed build or silently patched engine.

1212 actual10steps/2ms0.169s q/v/contactimpulse prefix differences EXACT0.
At previous time0.0002,vertical normal and dFree agree with free face penetration
−0.857µm;correction brings the surfaces exactly together. At0.0004,all seven
mu.3 normal parent-J rows become ±X (zeroZ),and dFree≈0 despite free vertical
penetration−7.713µm. At0.0006 normals flip−Z;contact disappears later.1215
preserves actual row vectors/gaps. Previous-state detector points alone were
NOT proof of wrong free gap;new data narrows the degeneracy to zero separation
normal construction in this specific scene. Contact pair/feature provenance
still needed;do not generalize to every SOFA collision model.

New single-policy controls1213/1214 enable installed useSurfaceNormals,keeping
all geometry,force,dt,distances,solver andfixture unchanged. No tunneling,
BUT mu0 now stays laterally fixed;actual contactFx≈−0.01N cancels applied0.01N.
Thus not a validated frictionless sliding control or jamming repair.
Next1216/1217 replace ONLY detector policy by installed LocalMinDistance
defaults. Both produce nonfinite states then hit60s child limit.1218 flags
FAIL_NONFINITE_AND_TIMEOUT,keeps original partial Raw unchanged. No retry
or tolerance/dt/alarm/friction tuning after these failures.

No new Holding/Lift,wholeB3 convergence,mesh,material,energy or jamming PASS.
NEXT bounded detector-feature/response-row provenance at coincidence to
distinguish line/line vs triangle/point normals before selecting any policy.
No full grasp run or unsupported custom solver. Actual point-feature sources,
pressure force/friction work remain unqualified. READY task is in research queue.

Read-only restart:python -m json.tool product_prototype/results/contact_gap_assess1215/summary.json
Fresh actual probe:python product_prototype/sofa/contact_gap_probe.py --tag NEW_GAP
(reuses guarded1211 binary;never overwrite old result directories).
