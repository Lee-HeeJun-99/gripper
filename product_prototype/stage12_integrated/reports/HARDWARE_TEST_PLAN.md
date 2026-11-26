# Hardware preparation — no operation authorized

Actual fixture CAD: `hardware_test/fixtures/torque_arm2`, four finite parts
plus assembly STEP. Actual stock M2 socket plug geometry is retained in V2.
The revised cross-pin uses the Z direction after rotating the bench shaft90deg
about Y. Off-bench subassembly and reverse off-bench service are required;
this is not a claim of installed access through the complete gripper.

Read the actual finite checks in torque_fixture3 and torque_arm2_access3.
V1 pin insertion failure remains in torque_arm1_access1. The earlier V2
extraction envelope with an incorrect bottom thread rotation direction remains
preserved; access3 uses opposite signed rotations for opposed RH axes.
These are sampled geometric paths, not helical thread/contact strength proof.

`hardware_test/protocols/TORQUE_AND_JAM.md` defines guarded calibration/jam
preparation and stop conditions. Blank physical recording form and strict
analysis are in `hardware_test/inspection/torque_records1`; no actual physical
records have been collected. Synthetic parser controls are not hardware data.

Before any test: obtain equipment and user authorization; validate fixture
strength and fastening, sensor calibration/uncertainty, counterhold, guarding,
hard travel stops, safe energy and independent overload shutdown. Nominal arm
stress and a sensor measurement range do not constitute proof-load approval.

Still unfinished: validated mounting/guard/sensor interfaces and strength,
finished-terminal pullout fixtures, full Tendon/Finger/root proof fixtures,
actual material certificates and bounded maximum dynamic jam specification.
Do not describe this partial hardware preparation as the full requested test
package or as a reason to bypass remaining digital verification.
