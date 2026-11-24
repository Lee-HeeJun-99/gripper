# Opposite-side route1390–1395 — exploratory no-object opening

StartingHEADa18771f. One new causal change:guide cable point/pullpointnormal
offset+3→−3mm,keeping actualoutboardcoordinates,12Rigidguide frames/masses,
36Railbackfoot anchors,NativeFEM/C2/root/gravity/solver. This replaces thetwo
closingroutes for a matched diagnostic,NOT a simultaneous4cable antagonistic
assembly. OriginalB3/300partCAD unchanged. No object/support/other2fingers in
Nativecoupon;originalcollisionpipeline and retainedSkin/Rail/guidecollision
models stay present. Samegroup selfcollisionpolicy unchanged,NOT certified.

Finiteproxy assumptions:wireR.25mm,guide enclosingR=hypot(1.5,1)mm,solid
supportrodOD.5mm fromRailfootcentroidtoeyelet. Sampled distance plusLipschitz
halfspacing gives initial Skin lowerbounds1390:wire17.1152mm,guide15.8096mm,
support.199427mm. OwnRail joint/bond overlap,eyeletbore/wirebend,assembly and
dynamic interference NOTQUALIFIED. Rodstrength/guideCOM/inertia notmeasured;
oldRigidmass/COM/inertia intentionallyheld as controlled idealbody assumption,
NOT claimed massproperties of a manufacturedbackside support.

1391front/1392back .05s/20outputs complete in.471/.418s. Costforecastfor.6s
uses actualpilot×12×5<120s;child4GiB/120s.1393front/1394back.6s/240outputs
complete3.320/3.219s,mincorevolume ratios.983561/.989130,finite,noSOFAERROR.
Actual1.5N/cable NativeC2 input andlambda=Tdt journalidentityerror0Ns1395.
Geometricshortening reconstructed from actualRigid3 acceptedframes,localwire
coordinatesandfixedpullpoint;not command/internalvalue substituted forlength.
Backendpoint2.00252/2.13589mm;maxinternal-geometricdifference19.3541µm.
Front4.53878/4.84465mm,difference46.7365µm. No newCable/timeconvergencePASS.

1395restunit-force momentalgebra eachcable aboutSkinsection0/30/50mm:
front+3Nmm/N,back−3Nmm/N. Algebra reference,NOT Native measuredmoment.
Native widthmean topSkin endpoint tangent50.6667°rest→83.7657°front vs
34.5011°back. Back outwardTipX+15.4163mm;front−17.9414mm. Actualopening
direction observed inexisting circularrest singlefinger,not prestatedpose.
No actualcontact/100gHolding/Lift/jamming/hardwarequalification claimed.

Nextactualcycle:apply SAME opposedroute to rejected1388nonuniformmanufactured
restshape in NO-OBJECT coupon. Rebuild Native stress-free FEM/Guide-foot/wire
references consistently. ComputevirtualR30insertiongap fromacceptedstate:
noobjectexistsinNative,so gaptestONLY answersgeometricclearance for future
insertion,not contactorHolding. Do notinitializepenetratingactualsphere or
reuse old50gresult. Simultaneousclosing+openingactuators requireseparatefinite
guide/anchor/support/mass checks beforegraspintegration.

Reproduce(newuniquetags only),Pythonrobot_ws:
```
product_prototype/sofa/opposed_tendon_coupon.py --tag NEW_GEOMETRY
product_prototype/sofa/opposed_tendon_coupon.py --native --opposed --tag NEW_PILOT
product_prototype/sofa/opposed_tendon_coupon.py --native --opposed --duration .6 --pilot opposed_pilot1392 --tag NEW_MID
product_prototype/sofa/opposed_tendon_assess.py --tag NEW_ASSESS
```
All commands/source/binary/scene hashes/limits inpreflight,Raw preserved;
actualforcework/rootreaction/wholeenergy NOTMEASURED. SDKunchanged,nopush.
