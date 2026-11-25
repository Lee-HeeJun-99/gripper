# Finite terminal anchor and actual unbraced contact prefix

##1922/1926valid prefix;1925full actual Holding in progress

1922normal240steps/.6s108.17103s. All3Skin contact, Guide–Guide/Root rows0,
savedFEM minimum0.988971. Actual maximum reconstructed brake torque
0.00139516Nm below declared0.015Nm design-reference budget. Finalobject
speed14.92576mm/s is during prefix, NOT Holding.1926before0.5s actual
objectq/v/impulse and all3Skinq/v agree EXACT0 with unbraked1904. Thus
observed change is after declared engagement, not altered initial simulation.
Configured viscous-loss reconstruction24.8894uJ at six ports is not actual
hardware loss or whole coupled energy. Entire motion/physical brake remains
unqualified.1925full2s actual run launched with unchanged420s/4GiB hardlimit;
forecast337.14s from actual unbraked full259.34s with1.3margin, no positive
prefix overhead (new108.17s versus old146.61s). No success before full data.

1924preservation audit verifies3566manifestrecords, original102queue entries,
all prior tracked Raw/SDK/compiled binaries unchanged; seven helper testsPASS.
It explicitly observed1922RUNNING at audit time; not a final no-running claim.

```sh
python product_prototype/sofa/brake_prefix_compare.py --case braked_contact1922 --tag braked_purity1926
python product_prototype/sofa/braked_crimp_native.py --tag braked_hold1925 --full --prefix braked_contact1922
```

##1920–1922: independently scheduled actuator loss

New NativeBrakeSchedule writes ONLY stock implicit FF dampingCoefficient at
AnimateBegin, using declared end-clock quintic onset0.5s/full0.6s. No q/v,
free-state, row, contact, force or ODE solver is implemented or modified.
Coefficient nonnegative: ideal f=-c(t)v dissipates c(t)|v|²; this is not a
real motor/friction/switching measurement or electrical energy certification.
1920actual50step coupon checks applied schedule and Native operator/work
against independentM/C/K. Normal0.13601s, PASS component only. Source/
CMake/build recipe and actual binary SHA frozen in result/preflight.

1921actual registered single-Finger fullclosing240steps/0.6s4.07732s normal:
before-brake Skin q/v difference versus1892 EXACT0, no contacts, minFEM
0.98892457, inputpeak1.41443636N/no cap, lateerror<=6.568pm. This preserves
closing unlike always-on1917/1918. No100g success inferred. Append-only
metadata clarification notes inherited preflight always-active wording;
actual frozen Scene, producer scheduled=True and applied-data journals
unambiguously show switched input. No original artifact edited.

1922new actual3Finger/free100g0.6s contact prefix launched from1904. Only
local nonnegative rotor loss schedule differs; same1.5Ncap, all geometry/
mass/FEM/contact settings/support protocol retained. Check actual brake
torque stays within declared0.015Nm reference budget and all original
prefix gates before fullHolding. Coefficient not scanned or fitted.

```sh
python product_prototype/sofa/winch_brake_schedule_contract.py --tag brake_schedule1920
python product_prototype/sofa/winch_brake_finger.py --tag brake_switched_finger1921 --scheduled
python product_prototype/sofa/braked_crimp_native.py --tag braked_contact1922
```

## Actual full1904: internal support removed, speed gate FAIL

Normal800steps/2s259.34044s. Original1908Holding: Slip0.209806mm PASS,
maxspeed23.208324mm/s FAIL, Supportgap42.064484mm PASS, Supportforce0.
Guide–Guide and Root nonzero rows0 throughout; no object Guide/Rail/Winch
response, savedFEM minimum0.988971.1911independent actual-pose clearance:
75parts/800poses/1,500,000interFinger pairframes,1260narrow tests, uncleared0;
minimum hardware–object triangle gap0.609613mm. Saved outputs only, notCCD.
1910/1914object linear residual8.674e-19Ns/angular4.235e-21Nms, actual row
partition sound.1914aligns original inclusive1.6s endpoint to161samples;
1910used160half-open samples and is preserved. Correct inclusive mean SkinZ
0.983699663N versus weight0.981N. Original and combined1915verdicts FAIL.
Solver iteration limit23/161Holding samples: no numerical convergence PASS.
First1913aggregate parser expected maximum_support_resultant_N; existing
Holding producer uses maximum_support_reaction_N. Corrected parser before
writing1913, no Raw regeneration;1915uses corrected-window1914balance.

1912actual held-drive diagnosis: all6inputs at1.5N cap in161/161outputs,
stroke error1.799955–2.013069mm and output port speeds15.578–30.685mm/s.
Thus commanded displacement is NOT achieved or stationary. This is actual
coupling evidence, NOT proof of unique cause; do not just increase tension.

1916distinct actuator passive-loss path: stock Rigid3d mapped implicit
UniformVelocityDampingForceField on supported rotor. Research coefficient
0.0048884Nms/rad derives0.015Nm torque budget at observed peakbackdrive,
NOT actual motor data or global FEM damping fitting. Actual50step Native
normal0.13598s; discreteM/C/K velocity error<=1.887e-14, reference work
identity residual<=1.878e-20J, nonnegative loss. Component PASS only.
1917actual registered single-Finger constant-loss closing normal4.34655s,
minFEM0.989143/no contacts. Original postprocessor numpy.int64 serialization
fails; independent1918reads same Raw without rerun:147cap samples/tendon,
late stroke error177.93um violates unchanged1um gate. Always-on brake
candidate REJECTED before fullgrasp. Original1917failure retained explicitly.

Next distinct hypothesis is an independently controlled passive brake after
closing, not another damping-coefficient sweep: c(t)>=0 cannot inject
mechanical work in the ideal viscous model. It needs actual Native public
Data scheduling, prefix purity and single-Finger closing validation before
any3Finger trial. Switching bandwidth/actual motor loss remains unmeasured.

```sh
python product_prototype/sofa/holding_assess.py --case crimp_hold1904 --tag crimp_holding1908
python product_prototype/sofa/winch_object_balance.py --case crimp_hold1904 --tag crimp_balance_window1914
python product_prototype/sofa/actual_hardware_clearance.py --case crimp_hold1904 --tag crimp_clearance1911
python product_prototype/sofa/winch_hold_boundary_diagnostic.py --case crimp_hold1904 --tag crimp_boundary1912
python product_prototype/sofa/winch_brake_coupon.py --tag winch_brake1916
python product_prototype/sofa/winch_brake_finger.py --tag brake_finger1917
python product_prototype/sofa/winch_brake_finger_assess.py --tag brake_finger_assess1918
```

Start HEAD397a997; see git log for feature commit. This is NOT Holding PASS.

1894 completed the new parallel-winch 3Finger/free100gR30 prefix:240steps,
0.6s,112.374875s normal/noERROR. All3Skin contact, minimum saved FEMratios
0.989924/0.989048/0.988967, object impulse partition residual4.337e-19Ns.
But36nonzero terminal Guide–Guide rows: FAIL unbraced. New Root contacts0.
Final speed25.7375mm/s is during closing, NOT1.6–2s Holding. Mean closing
Skin0.746072N/Support0.238669N is not unsupported late load capacity.

1896new mechanism: cable ends at guide5 with no outgoing span; replace its
pass-through eyelet with a blind termination, not another chamfer/size scan.
Finite2x1x0.7mm fitting, boreR0.25mm/L1mm, wireØ0.5mm unchanged, connected
bridge overlaps actual Support. Endpoint coordinates and all Triangle/Line/
Point collision features retained. New-exclusive minus old-exclusive material
updates body5mass/COM/full tensor without double-counting Support. Assumed
density1000kg/m3 remains uncalibrated. Actual crimp retention, bond strength,
friction, fatigue, finite-wire sliding NOT MEASURED.

Initial ownFEM new-material intersection0, connected positive solid and SPD
tensors. Old1894trajectory replay ONLY: minimum new-fitting pair gap205.0267um,
object gap2.86269mm. Necessary geometry, not new dynamics/continuous sweep.
Narrow margin above unchanged200um contact budget required actual Native.

1897actual one-step indexed-mass contract on3new tensors: normal0.12027s,
velocity error<=8.882e-16 versus1e-12 gate. Initial operator PASS only.

1898actual new3Finger240steps/0.6s,146.61413s, normal/noERROR:

- Actual Skin contact Fingers0/1/2; nonzero Guide–Guide rows0, Root rows0.
- Object Guide/Rail/Winch load0; minimum saved FEMratios
  0.990030/0.989044/0.988971.
- Actual input tensions<=1.5N; output peak1.517738N, not assumed equal.
- Object impulse partition residual4.337e-19Ns; final speed14.77195mm/s.
- Mean closing SkinZ0.744604N, SupportZ0.238667N; Support still present.

PASS **valid unbraced contact prefix only**. No1.6–2s output: no Holding,
numerical, physical or hardware PASS. Versus1894 finite termination material
and coherent COM/tensor changed, not collision filtering.

1899actual1.2s extension is next bounded trial. Full2s forecast635.33s with
1.3margin exceeds420s limit.1.2s forecast381.20s permits a Support-withdrawal
pilot; record actual outcome separately. All scenes/producers/source/binary/
commands/hashes and Raw retained. No q/v/SDK/dt/force/tolerance changes.

Actual commands (historical tags; NEW tags for any justified rerun):
```sh
python product_prototype/cad/terminal_crimp_candidate.py --tag terminal_crimp1896
python product_prototype/sofa/yoke_inertia_native_contract.py --case terminal_crimp1896 --tag crimp_tensor1897
python product_prototype/sofa/terminal_crimp_native.py --tag crimp_contact1898
python product_prototype/sofa/terminal_crimp_native.py --tag crimp_withdrawal1899 --duration 1.2 --prefix crimp_contact1898
```

## Actual1899 / independent1902 / resource1903 / full1904

1899normal/noERROR480steps/1.2s completed214.23001s. All3Skin contact,
Guide–Guide and Root contact rows0, same minimum saved FEMratio0.988971.
Finalspeed5.47397mm/s is outside original Holding window. No Holding verdict.

1902read-only actual object impulse analysis: linear momentum residual
8.674e-19Ns, angular4.235e-21Nms, row partition8.674e-19. Algebra regressions
4PASS. First analysis attempt1901created no output: parser assumed totalMass
and iterations; actual RigidMass uses vertexMass and solver_iterations.
Corrected actual-source parsing, no Raw edit or rerun.1.0–1.2s maximumspeed
12.51535mm/s, minimum Supportgap2.30523mm, Support/hardware force0, mean
SkinZ0.97461856N, Solverlimit samples0/80. Earlier0–0.5s95/200 and0.6–1s
11/160limit samples: convergence NOT globallyPASS. Small momentum residual
does not certify contact, energy or FEM dynamics.

1903resource model uses two actual durations with canonical Scenes identical
except output paths. Every short CSV is a byte-identical prefix of the longer
CSV. Fixed initial/closing cost78.99826s, incremental112.69313s/s, full2s
forecast304.38451s; same1.3margin gives395.69987s<420. Supersedes only the
single-run conservative resource estimate, not physics gates. No observer
removal/dt change/state restart/tolerance change. Actual full1904started with
hard4GiB/420s; preserve timeout if forecast wrong. Initial CLI rejected new
argument before output or child; parser registration corrected before launch.

```sh
python product_prototype/sofa/test_winch_object_balance.py
python product_prototype/sofa/winch_object_balance.py --case crimp_withdrawal1899 --tag crimp_balance1902
python product_prototype/sofa/crimp_runtime_contract.py --tag crimp_runtime1903
python product_prototype/sofa/terminal_crimp_native.py --tag crimp_hold1904 --full --prefix crimp_withdrawal1899 --runtime-contract crimp_runtime1903
```
