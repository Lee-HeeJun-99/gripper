# Film mechanics/contact implementation — actual results,unfinished

## Implemented and independently checked

Independent `models/film_shell`,not changed Beam or Golden. Flat-reference
Green-strain membrane + material-curvature/twist energy,full xyz width DOFs,
AD2 forces/tangent,SOFA plugin,journal and fixed-plane clipped surface contact.
Research assumptions:E250,ν0 or.3,t specified perexperiment,mm/s/modelF.
No measured material,density,pressure,actuator or destructive test data.

Kernel current:force FD2.77938e-11,Hessian FD5.9425e-9,
objectivity8.32667e-17,net internal force5.55e-17,moment2.22e-16 PASS.
Analytical equibiaxial membrane and quadratic plate/twist energy PASS.
Cantilever L100,W10,t.2,ν0,F1e-7:consistent one-sided slope constraint has
11/21/41mesh analytical tip errors.3001/.1002/.0283%. Width3/5nodes agree.
Two fixed rows instead have22.7/11.9/6.10%errors because clamp length changes.
Do not mix these boundary conditions or approve the latter as mesh convergence.

Actual SDK API tests cover no-contact,plane,root fixture and displacement DOF
modes:F/dF/matrix/pure state queries. FD sweep2e-5/1e-5/5e-6 passes unchanged
absolute1e-8criterion. Earlier1e-6 had cancellation3.29e-8 and2e-4 had
truncation2.22e-7;both failures are preserved,not a loosened tolerance.
Plane clipping unit has known area.5,F.5,U.125 and force/Hessian FD PASS.

## Actual SOFA deformation/contact and comparisons

Existing Matching SDK only. `ldd` resolves closure_sdk symlink and patched SDK
libraries from the same installation;no installed SOFA engine mixed.
First actual cantilever mechanics04tip matches independent same-mesh linear
two-row-clamp solution≈.0154600mm. Tip-only time comparison passes,NOT global
energy or static equilibrium certification. Saved actual xyz states are inCSV.

Equal-core-volume homogeneous rectangular coupons are an isolation comparison,
NOT baseline3finger vs proposed skin/rails. L100,E250,ν0,F1e-6,planez.1,
kn1e-5,volume146.4466mm³/coupon. W10,t.1464466 versusW24,t.0610194.
Early Euler cohort narrow06/wide06had Aref29.45799/51.05005mm²,
nominal mean traction ratio.747824 and area ratio1.732978. Both final free-force
residuals below1e-3 at those final samples. NOT a converged grasp advantage.
Actual deformation PNG/OBJ:designs/visualizations/film_actual_v1.
PNG z is exaggerated50× and orange triangles CONTAIN an active fraction;
their full colored areas are NOT the clipped contact area.

### Runner classification bug and preserved correction

Up through wide_bdf08,the requested Static/BDF option did NOT replace the
literal Euler node in generated XML. Thus these cases were actually Euler.
Their old summary solver/time labels are INVALID;read generated XML/raw.
No old result was overwritten. Runner now asserts actual XML solver selection
and writes actual_solver.json. Static09is genuinely Static;BDF09genuinelyBDF.
The earlier manually debug-rebuilt API executable in mechanics02was NOT an
immutable compiled identity;its original source snapshot/logFAIL are preserved.
Use compiled.json of fresh later campaigns,not that debug executable.

## Actual failures and alternative hypotheses

Euler weak-load contact05free-force residual.0010–.0034 FAIL1e-3,despite
tip-only agreement. Larger-load wide_dynamic07has huge residuals despite
small tip changes. Proper BDF09and BDF ramp produce nonfinite positions FAIL;
not claimed to be successful nonlinear Solver comparisons.

Explicit world-z root slope fixture(K100F per unit width),one fixed root row,
removes moving clamp length. Actual Static fixture11/21/41Aref≈53.158/52.660/
52.457;energy≈3.085/3.110/3.121e-9. Adjacent geometric/energy differences
decrease but base→finest energy remains over1%;equilibrium also fails in some
coarse conditions. Solver absolute stopping1e-12was tested against1e-10,
which is STILL stricter than physical residualGate1e-3atthese loads.
No physicalGate changed. fixture_tol21stillFAIL. Continuation via real
LinearForceField0→Fover10s achieves final residual6.34935e-6 in
fixture21_ramp PASS(local static endpoint only). Ramp-phase observer residual
uses final reference load and must NOT be interpreted before full load settles.

Hypothesis2:coordinate/strain cancellation. New displacement DOF + stable
Green strain is algebraically equivalent;FD,objectivity,tiny strain1e-12
analytic energy PASS. Actual euler_displacement reduces residuals but still
FAIL(.00356,.984,10.59). bdf_displacement still nonfinite FAIL. Thus
cancellation alone is insufficient;do not claim this experiment fixed dynamics.

Hypothesis3:nonlinear integration/assembly versus constitutive energy.
Independent full-Newton backward-Euler reference uses the SAME energy,fixture,
plane,mass,damping,start-time load schedule but no SOFA. In
autonomous_film_reference_20261116_a01,100step fails Newton30atfirst load;
200/400finish with final dynamic residual1.85e-13/5.72e-13,
tip.103759540/.103759534,U3.109988e-9/3.109983e-9. This supports
separating nonlinear Solver/global assembly investigation from constitutive
failure,but is NOT an actual SOFA dynamics PASS. Base dt convergence stillFAIL.

## Temporal friction work — independent new reference,not engine fix

`tools/sphere_temporal_reference.py` derives a continuous exact positive-slip
great-circle sphere chord (normal changes),c=a(R−r),r=√(b²+u²),
plastic arc derivative(b+a*u/k)/r. Verified70digit quadrature and W=U+D.
Birth time.00500306748674s;D1.10709903936596e-9,W1.50944853571630e-9,
U4.02349496350343e-10. All aligned20/40/80phase comparisons exact for this
analytical branch. It excludes arbitrary off-plane history/re-stick/general
endpoint tangent,and is NOT installed as a new SOFA constitutive law.
Original SphereEvent512time0.146423%FAIL and Curved.8519%FAIL remain.

## Gates and next actual work

PASS limited:kernel/API/analytical patch;fixed-plane actual contact exists;
some same-load endpoint equilibria. FAIL:fullfilm dynamic equilibrium,
coarse→fine energy/contact convergence,base dt/reference robustness.
BLOCKED:laminate friction/pressure calibration,tendon-driven fullfilm,
baseline3finger free-object comparison,global energy,grasp Optuna.
Additional actual probe:the first assembled free block equals M+dtC+dt²H
with relative5.57780e-17(maxabsolute4.44089e-16). Rawmatrix is under
matrix_probe/1/journal.csv.matrix.csv;film_matrix_assess explicitly removes
15scalar root DOFs. The initial in-component diagnostic wrongly skipped only
5scalar rows and showed a false29%defect;postprocessing uses15,retains raw
and does not change any physics. Not evidence about all nonlinear stages.
Next:compare actual nonlinear RHS/state/correction to the independent200step
reference FIRST,not another identical BDF rerun or alleged missing-stiffness fix.
Then qualified adaptive/time step Newton integration,physical layer/rail
coupling and virtual-work-consistent native surface mapping.

Reproduce fresh paths only:

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/film_shell_run.py --tag UNIQUE --steps 30 --solver static --plane .1 --width 24 --thickness .06101941552425123 --load .000001 --nodes 21 --single --fixture 100 --ramp 10 --displacement
$PY tools/film_implicit_reference.py --tag UNIQUE
$PY tools/sphere_temporal_reference.py --tag UNIQUE
$PY tools/film_equal_material.py --tag UNIQUE
$PY -m unittest discover -s tests -p test_film_design.py -v
```

All children bounded4GiB/480s,longest independent reference≈34s perchild.
No host resource exhaustion,hardware execution or background restart asserted.
