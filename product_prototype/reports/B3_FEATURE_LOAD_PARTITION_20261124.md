# Reused actual B3 feature loads1254–1255

Read-only audit of historical Native485(50g) and1059(100g),no full B3 rerun.
Source b5164ad. Actual scenes use analytical Rigid3 SphereR30mm object;
Skin Point/Line features reach it. Stored Detector and Response rows are
different evidence layers,not one-to-one area. Existing historical response
observer getConstraintInfo metadata side effects remain disclosed;new
read-only observer purity does NOT retroactively qualify those old trials.

1254 strict recorded accepted time1.6–2.0s yields160frames (not rounded to
161;no interpolation or old verdict change). 50g Point–Sphere meanFz
+0.4904973N,Line–Sphere0N. 100g PointFz−0.036219N,LineFz−0.037715N.
No duplicate skin response row IDs. Skin Line rows existing in Detector
are not proof they actually carry load:50g shows exactly this distinction.

1255 phase-specific force decomposition,actual accepted window means:

|mass/window|Point Fz N|Line Fz N|total Fz N|
|---|---:|---:|---:|
|50g1.0–1.2s|.490396|0|.490396|
|50g1.2–1.5s|.490520|0|.490520|
|50g1.6–2.0s|.490497|0|.490497|
|100g1.0–1.2s|.234908|.471890|.706798|
|100g1.2–1.5s|.092839|.106676|.199515|
|100g1.6–2.0s|−.036219|−.037715|−.073934|

The100g early deficit relative .981N exists before the final failed hold;
large Line load and loss of Point support distinguish it from50g. Contact
shape and force direction are therefore relevant,not merely Cable command
magnitude. However point/line activation does NOT prove the plane coupon's
near-parallel Gram issue is the unique100g cause. No native detector normal
was recorded in these old journals:leaveNULL,not reconstruct fictitious
actual normals from response forces. Need temporal scene-specific feature
and normal measurements at withdrawal before product changes.

No new Holding or Wrapping verdict. Full time/mesh/element/joint failures
still block product qualification. Raw input scene/journal/summary hashes
saved in new summaries;old Raw untouched.

Reproduce(unique output):
`python product_prototype/sofa/b3_feature_load_audit.py --tag UNIQUE --early-phases`
`python product_prototype/sofa/test_b3_feature_audit.py`
