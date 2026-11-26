# Current product definition — reference and candidates are separate

Adopted reference: RevAA,304parts, supported direct winch,3Fingers,
one baseline Tendon per Finger. Exact authoritative dimensions, datum and
assembly instructions remain in Stage1 revAA_mbd1; no copy overrides them.
`CURRENT_BASELINE.json` records all actual per-part hashes and geometry in SI.
Physical mass/material allowance is unassigned where no justified specification
exists; unit-density geometric integrals are not actual mass properties.

AB sliding PET is unadopted. AC shortens three PET ends and retains the AB
front geometry; deformed interference rejects acceptance. AD retains AC PET
and modifies three terminal front entry profiles. Actual assemblies and parts
are in `cad/exports/revAC_pet_travel1` and `cad/exports/revAD_funnel1`;
the AD304row candidate BOM is `bom/revAD_packet1`. Unchanged parts reference
their exact prior STEP files. None of these is the final integrated revision.

The HPMC object is explicitly a packaging gauge, not an installed clutch.
An Oldham independent kinematic reference is not a selected complete coupling.
The torque arm is a separate bench fixture, not a new gripper component.
The stocked0.45/0.54mm Tendon screen does not change the current0.48..0.52mm
incoming diameter requirement or approve a new finished terminal.

No motor current limit, nominal holding torque, accidental coupling slip or
stroke stop is treated as a certified maximum Tendon load. No powered
operation or100g performance is approved by this package.
