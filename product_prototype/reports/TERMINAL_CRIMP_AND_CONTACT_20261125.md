# Finite terminal anchor and actual unbraced contact prefix

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
