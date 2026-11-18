# Typed material-edge continuation (experimental)

ThreeFilmFaceEdgeODE splits an identified smooth-face boundary and continues
with an explicitly owned material edge. The geometric constraint is C1 at
this transition: velocity is preserved, not clamped; no impact impulse is
introduced. Topological edge aliases are excluded only from independent
birth classification, never from all-triangle physical clearance.

ThreeFilmEdgeODE restores REGRIP_EDGE_V2, including physical q/v, quaternion,
public masses/inertia, affine root mapping, ordered material-edge support,
birth time, exact geometric parameter/normal, and accumulated physical time.
Private legacy sampled-work history is not restored; its origin is separate.

Actual1059 matches independent1057/decoded1058 exactly through five100us
steps. Actual1060 restores snapshot137 and reproduces four steps, all36
stage rows and four serialized snapshots exactly. Gates remain1e-12 API,
1e-10mm gap,1e-17Ns momentum and1e-10mm/s normal velocity.

Actual1061 fails after checkpoint170 (~27ms): a stage reaction becomes
negative. This model deliberately rejects release rather than applying
tensile contact. It is not a general release/CCD/friction/grasp solver.
No time/mesh/full energy certificate follows from exact resume.

Reproduce the small qualified continuous comparison with a NEW tag:

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/film_three_film_edge_resume.py --tag UNIQUE --parent 20261118_three_film_primitive_actual1059 --checkpoint-step 137 --steps 4 --compare
```
