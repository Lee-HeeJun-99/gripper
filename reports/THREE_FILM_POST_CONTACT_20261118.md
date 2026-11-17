# Three-film actual impact continuation and post-contact convergence

## Latest result through999

986/993/994 corrected clock runs COMPLETE,same DLL with11 child/root contexts
synchronized. Actual runtimes41.1046/60.0703/101.4051s.989/995/996 inventories.
998 causal pairs PASS:seven owner/row/displacement CSVs BYTE-EXACT before/after,
field mechanical observables exact;incorrect endpoint T and sampled-work
columns intentionally corrected. Maximum field/control mismatch becomes0N.
984 old input failure remains unchanged. Compiler dependency closure proof
for993/994 checks every included source/header and target CMake;only new
unlinked AllRowRelease.h differs,never a compiled-code exemption.

997 actual post-contact overall assessment STILL FAIL at0.1%.1→4:
film velocity0.00743931%,rails0.0230886%,stage work0.0136215% PASS;
legacy sampled work0.7214203% FAIL(abs2.370409e-11Nmm);
normal constraint-work residual83.0143% FAIL(abs4.418469e-24Nmm).
Both absolute and relative errors retained;no tiny-energy exemption.
Signed integrator residual decreases -2.30669e-13→-9.03525e-16Nmm but is NOT
heat or full energy closure. The separate listed motion/force/stored/stage-work
subset passes;this is NOT overall time,whole event or grasp certification.

999 independently tests release from ACTUAL deformed1.6ms state after an
explicit external-force change to+.001N. All free normal accelerations remain
about-63.0993mm/s2 and needed reactions+4.93538e-7N. ALL-row release correctly
rejects. FAIL hypothesis:weak pull-away does not release this transient state.
No velocity/reaction was zeroed and no larger force was introduced to fake
ungrasp.992 flat-reference release PASS does NOT cover this deformed state.

Not project completion. Sources are archived per campaign;baseline5d53e6 plus
recorded working changes. All material/actuator inputs are research assumptions.

## Actual contact continuation

ThreeFilmEventContinuationODE reuses the prior actual persistent owner only
AFTER the new common event/remainder. No old fixed-object guard was removed.
966 actual SOFA completes8x200us to1.6ms with ONE free sphere,three film/rail
fields and fixed mapped roots. Existing C2 Tmax=.0001N per rail,ramp.01s.
Initial body vz=-1mm/s,z offset+.0001mm;gravity0,Fz=-.001N. This is NOT tendon
closing from rest or lift. Equal prescribed tension is NOT a mechanical
tendon equalizer. No friction,self-contact or pressure certification.

Reference/actual maximum q difference5.42e-20mm,v5.55e-16mm/s,41.2195s runtime.
974 actual post-event work interval200us..1.6ms only:full-AD/actual field
stored/film kinetic error2.07e-24Nmm,signed residual-2.30669e-13Nmm.
Tendon work3.28781943e-9Nmm,external work1.41004101e-6Nmm,damping
2.84040986e-7Nmm. First200us integration work is NULL/missing,not zero.
Impact loss9.38172884e-10Nmm is separately recorded,not viscous/friction heat.
No full physical energy PASS follows from the small signed residual.

## Independent post-contact isolation

967/968/969 use the SAME saved actual200us q/v and exact public masses;refine
ONLY the following1.4ms in8/16/32 steps. Runtimes22.12/37.23/70.99s.
970–972 full-AD separate skin/rail/attachment/kinetic inventories.
973 all-pair0.1% listed post-contact gate PASS,including base-to-quarter:
rail energy0.0135535%,attachment0.00059328%,film velocity0.00447149%.
This is independent nonlinear FEM,NOT actual SOFA/full impact time convergence.
Earlier single-film553 and every old coarse-grid failure remain unchanged.

## Actual post-contact dt / discovered API-control defect

ThreeFilmVariableContinuationODE keeps the first200us event/remainder EXACTLY
fixed,then public next-step clock selects200/100/50us. It does not use a
multistep history across impact and does not project positions/velocities.
978/979/980 actual same-DLL runs complete with8/15/29 frames to1.6ms,actual
q/v match independently reintegrated post references within2.84e-15mm/s.
Actual times43.92/61.27/99.84s,all below480s/4GiB guard.

981–983 full-AD inventories;984 overall actual assessment FAIL:
1→4 rail0.0230886%,film velocity0.00743931%,stage tendon work0.0136215%;
legacy sampled tendon work0.721923% FAIL;normal-work residual relative
comparison also FAIL(abs and relative retained,not ignored as small).
Most importantly,field C2 input mismatch4.5176518125e-8N at the FIRST changed
dt frame. Root dt changes before child contexts are updated for AnimateBegin:
factor2 t=.0003 field usesT(.0004),factor4 t=.00025 usesT(.0004).
The custom owner uses correct stage times;this does NOT validate mismatched
ForceField API input.984 is preserved,not relabelled.

New synchronizeChildren clock mode uses PUBLIC BaseNode/Context setDt on the
whole scene tree AFTER AnimateEnd,BEFORE next AnimateBegin. Old root-only
mode remains defaultfalse and reproducible. Every next context dt is journalled.
986 factor1 control COMPLETE;993/994 corrected factor2/4 are distinct campaigns.
987/988 NOT RUN:dependency guard rejected noncanonical ../ paths,NOT OS or
physics failure. Canonical compiler-emitted dependency closure now permits
ONLY proven UNLINKED added files;included code/CMake/binary hashes still guard.
It does not exempt changed compiled code. Current proof excludes only added
AllRowRelease.h,which is not included in the tested actual DLL.

## Independent extensions (not actual release certification)

985 unique smooth ONE-contact event-time IFT with initial body-z perturbation:
analytic .100009827814s/mm,FD .100009795278s/mm,relative3.25329e-7 against1e-6.
No derivative assigned to simultaneous minimum or feature transition.
992 all-row zero-impulse release reference PASS:all initially tensile
bilateral reactions are rejected as sustained contact;free normal acceleration
min2.828762mm/s2;analytic free-body midpoint,flat-plane whole-surface gap bound
and compressive negative control. This changes external Fz to+.001N in an
undeformed stationary fixture. It is NOT actual deformed/tendon release,
partial active-set switching,re-impact or ungrasp success.

## Reproduction / next integration

```bash
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_three_film_event_sofa.py --tag NEW_UNIQUE_CONTINUATION --sustained
$PY tools/film_three_film_post_sofa.py --tag NEW_UNIQUE_POST_DT \
 --reference 20261118_three_film_post7_975 --refinement 1 --sync-child-clocks
$PY tools/film_three_film_unit.py --tag NEW_UNIQUE_RELEASE --test test_three_film_release.cpp
```

Next:qualify corrected child-clock input,retain residual/legacy FAILs,then
generalize deformed release with whole-path clearance BEFORE using new branch
in actual SOFA. Full event-time refinement,globally earliest nonlinear family,
contact thickness,mesh,friction,self-collision,first-interval work,wrap/lift/
holding/12wrench/multimaterial/Grasp Optuna remain unqualified.
No automatic continuation or OS resource exhaustion is asserted.
