# Separate three-finger research design

FrameLayerNetwork applies the UNCHANGED small-planar LayerNetwork law in a fixed
reference frame: x_local=R0^T x_world, q_local=q0^-1 q_world. Wrenches transform
by diag(R0,R0), and spatial tangents by B*J*B^T. This reference is fixed for each
trial. It is NOT a new finite-deformation layer law or a pose correction.
The generated build-local FrameLayerBase is the original class with only its
name/final qualifier changed; original sources are not edited.

History/pressure slider updates use local coordinates exactly once at AnimateEnd.
Domain remains |relative planar angle|<.005, local nonplanar components<1e-8.
Record own layer*.csv dissipation: original IntegratedRecorder's LayerNetwork
dynamic_cast does not identify this distinct component. Component energy remains
partial; original BeamFEM's nonconservative work defect is NOT repaired here.

Research geometry: three100mm fingers tangent to the object at reference angles
0,+120,-120 degrees aboutY. All cables offset-.2mm bend inward in local frames.
Same per-finger section/E/mass/tension as two-finger benchmark, but total finger
material/mass/cable count is50% larger. Roots are about95.15mm from objectCOM;
this is NOT the proposed50mm gripper body or a fabricated design.

Finger Y/rotX/rotZ guides are explicit physical assumptions; object has6 free
DOFs, no fixed constraint, pose projection or invented torsional support. New
contact wrenches arise only from the third actual beam/finger and Coulomb law.
Reference-frame covariance/energy/Jacobian/history/dissipation unit tests run
before actual SOFA design trials. Pilot Tz is not a full12-direction certificate.
