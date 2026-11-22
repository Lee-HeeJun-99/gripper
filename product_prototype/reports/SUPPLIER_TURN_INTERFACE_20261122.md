# Changed turn branch — interface and material qualification sheet

DESIGN REVIEW ONLY. Current geometry: results/product_supplier_mount875/
full_assembly_recipe.json. One branch,not six. Functional sourcee11fc36.

Interface | Actual CAD input | Required qualification
---|---|---
Palm attachment | two feet atworld(44,30,15),(52,30,15)mm;OD7mm;boresD3.4mm | actual fastener grade,head/tool fit,thread/preload,pullout and Palm strength NOT MEASURED
Three turn forks | integral connected bridge,thrust span2mm,landsOD2.5/boreD1.2mm | actual machining/print capability,axialplay,wear and friction NOT MEASURED
Turn wheels | rootD11.25,pitchD11.7,OD13.75,width1.8,boreD1.2mm | candidate .45mm6x19 supplier bend guidance only;actual wheel material,bearing and fatigue NOT MEASURED
Turn axles | shaftD1mm,finite headed-pin/nut envelopes | actual threads,grade,retention and shear/bending strength NOT MEASURED
Third support | cross-member raised12mm toz68.75mm | nominal static/service clear only;assembly stiffness,moving clearance and handling NOT MEASURED
First Root seat | retained V43 research seat/bondline and shifted first guide | translated Skin attachment,adhesive,actual joint force/peel and fatigue NOT MEASURED

881 integrates actual saved watertight solids using explicit signed tetrahedra
and checks against trimesh moments.10parts,max relative inertia discrepancy
7.88824e-11 (software geometric calculation,not a physical convergence Gate).
Fields are COM_world_mm, mass_per_density_m3, inertia_COM_per_density_m5 and
inertia_COM_per_mass_m2. For a KNOWN uniform densityrho[kg/m3], mass=rho×volume
coefficient;inertia=rho×inertia coefficient. No rho has been selected or applied.
Actual material,density,mass and inertia remainNULL. Root/assembly joint masses
and heterogeneous construction cannot be inferred from a homogeneous CAD solid.

Before any new Native adoption: confirm real material/process and retained
geometry,measure mass/COM (weighing and suspension/balance),measure principal
inertia using calibrated pendulum or validate a traceable physical CAD mass
model;verify joint retention/force-deflection;then transform geometry and force
Jacobians to the verified COM frame. No old B3 checkpoint reuse.

Existing ROOT_AXLE_LOAD_MEASUREMENT_PROTOCOL.md remains the physical procedure;
this sheet does not replace measurements or authorize purchases. Actual motor
continuous duty,cable friction/force/stroke and supplier availability remain
unqualified;no speculative motor/material selection is made from CAD-only data.
