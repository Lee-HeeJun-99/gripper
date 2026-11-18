# Experimental exact separated-film scheduling

`freeGaussParallel` supports one or three workers, using the existing Gauss
integrator and immutable numerical film snapshots. Workers never touch SOFA
objects, clocks or journals. Results and observer callbacks are reduced in
finger order. Existing zero-load/zero-tension/no-spin/separation guards remain.

1630 same-binary independent comparison preserves endpoint, stages, forces,
momentum and evaluation counts.1631 same-binary actual SOFA six-run comparison
preserves all physical CSV and full checkpoint bytes, including actual1618
endpoint/stage-force/clearance CSV identity. Median wall ratio .699791;
inclusive kernel ratio .481650. This is not contact parallelism, a new physical
model, whole-time convergence, or grasp certification.

1632 fine-window refinement is a separate numerical experiment; do not infer
its result from exact scheduling or isolated800us time-gate PASS.
