# Reproducible execution environments

Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`3.10.20.
CAD reads/exports: `PYTHONPATH=/tmp/regrip_stage1_ocp`, cadquery-ocp7.9.3.1.1,
VTK9.6.2. Reuse installed package, never modify SOFA SDK.

3D static FEM/contact: `PYTHONPATH=/tmp/regrip_stage2_fem`, pinned distributions
in `models/analytical/FEM_REQUIREMENTS_LOCK.txt`. Gmsh4.15.2 bundles OCC7.8.1;
do not import OCP7.9.3 in the SAME process. libgmsh SHA256
9db3090d3b720c57b76bcbfa01d13854823ae2698c91343c20bdd4c2b81f6317.
OSQP1.1.3 actual binary hash is in sliding_contact4 summary.
Current separate environment fingerprints are in models/analytical/environment_
cad1, analytical1, fem2 and contact1. They are recreation fingerprints, NOT
retroactive evidence of an unrecorded historical process. One initial combined
Gmsh/OSQP provenance capture was explicitly stopped after74s with no output;
cause UNKNOWN. No scientific trial was stopped or reclassified by that event.
Keep library-owner processes isolated and set thread limits for metadata too.

Recovery if /tmp disappears (network installation may require approval):

```
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m pip install --target /tmp/regrip_stage2_fem -r product_prototype/stage2_load_transfer/models/analytical/FEM_REQUIREMENTS_LOCK.txt
```

Actual pip target installation omitted Gmsh's shared library. Recovery used a
same-version official wheel downloaded to the isolated directory, then extracted
`gmsh-4.15.2.data/data/lib/libgmsh.so.4.15` with `unzip -j` into that directory.
Verify the above hash before reuse; never overwrite SDK libraries.

Bounded child wrapper: `ulimit -v 4194304`, `ulimit -c 0`, `timeout 420`,
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`. Actual result commands are stored
in summaries; choose NEW tags. No existing result path may be overwritten.
Existing generated STEP trailing whitespace is exporter output, not edited or
stripped after hashing. Run whitespace checks on source/docs, not CAD serialization.
