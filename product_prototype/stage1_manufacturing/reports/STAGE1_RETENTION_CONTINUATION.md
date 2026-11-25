# Stage1 incremental retention development —2026-11-25

Start98d1dd6 clean; revA-H immutable. Only NEW drive parts are created and
remaining STEP geometry is referenced by path/SHA, not regenerated.

revI_drive211parts,0bulk overlaps. revI_fit adds locating outer-race0.02mm
nominal endplay and explicit journal clearance;211parts,0overlaps. Actual
independent stop shifts show left and right bearings blocked in BOTH axial
directions by caps/integral shoulders. Shaft8mm central shoulder, two OD8
inner washers and M5x0.5 thin nuts close the inner-race path. Left locating,
right deliberately floating outer race. No contact buffer or virtual bearing.
Two actual split coupling jaws/fourM3x10 replace missing set-screw placeholders.
Captured transverse1.5mm custom pin and twoM2x4 plugs carry shaft/drum torque
and locate drum axially. Reference1.5N/.012375Nm is NOT a certified capacity.

Actual cap service13axial samples each,0obstacles after declared coupling/
cap-screw cut-set. New real1.5mm thin8AF custom spanner CAD clears every other
actual part at both nuts. Assembly order prevents trying to pass16mm bearing
through13mm housing shoulder: empty supports first, then bearings from outside.
No powered assembly, physical preload or strength trial.

Manufacturer checks found an important correction: prior proposed shaft
4.984..4.992 was wrongly labelled5g6. It is NOT a standard g6 range. New
contract explicitly selects f6 [-18,-10]µm, nominal4.986mm. Historical result
is preserved and its old label is not reused as supplier verification.
Mean P6 bearing limits alone do not prove full envelope clearance; supplier
variation, gauge and coaxial inspection remain explicit drawing requirements.

Sources checked2026-11-25 (specification, not purchase/stock/strength approval):
- SKF625-Z generated manufacturer sheet,5x16x5, da7.4..8.3,Da≤13.6,fillet≤0.3,
  dimensionalP6: https://assets.alliedelec.com/v1644492269/Datasheets/c5ad7fad1c9a5f6a3c382f0ca640fe6a.pdf
- SKF P6 tolerance table, mean bore/OD and conservative width bounds:
  https://cdn.skfmediahub.skf.com/api/public/0901d1968094ddb3/pdf_preview_medium/0901d1968094ddb3_pdf_preview_medium.pdf
- Manufacturer fit table f6 3..6mm and H6 10..18mm:
  https://product.minebeamitsumi.com/en/technology/bearing/ballbearings_cat-3_004-10.html
- Bossard BN1207 fine M5x0.5 AF8/t2.7, not a claim every DIN439M5 nut matches:
  https://www.bossard.com/ch-en/eshop/hex-nuts/hex-jam-nuts-0-5d-metric-fine-thread/p/1207/
- Nut locking compound candidate TDS, cure depends on substrate/temperature:
  https://datasheets.tdx.henkel.com/LOCTITE-243-en_GL.pdf

Next actual design work is retained factory-terminated0.5mm Tendon ends,
swivel receiver, taper/flush-terminal geometry and full moving-path checks.
No Stage1 release or hardware PASS inferred from the drive component contract.
