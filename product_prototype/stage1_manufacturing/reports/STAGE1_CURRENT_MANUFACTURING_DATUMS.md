# Manufacturing definition and acceptance — Rev Y candidate

Authority order: controlled interface limits below and per-part BOM notes;
actual native STEP; case-linked face catalogue; dimensioned three-view SVG. The STEP
does not model thread helices. A major thread cylinder is NOT a drilling
instruction. Model coordinates are mm. F0 coordinates are retained as setup
coordinates; inverse-rotate F1/F2 by120/240° around globalZ before machining
identical parts. Swivel parts are pitched in assembly: align to their actual
split plane/axle axis from face table, NOT the global bounding-box axes.

Unspecified machined linear±0.10, drilled clearance diameter±0.05, hole
position±0.05 per coordinate are DESIGN REQUIREMENTS, not measured process
capability. Precision fits below override general tolerance. Burrs/edge breaks
must not intrude into contact/small-wall envelopes. Actual process capability
and gauges must be accepted by selected shop before fabrication authorization.

| Interface | Required manufactured limits / datum |
|---|---|
| Main shaft journals | 5f6:4.982..4.990 maximum-material envelope; common axisA X80/Z20; coax0.005DIAMETER, Ra<=0.8µm |
| Main shaft shoulders | OD8, facesY-3.5/9; datumB left shoulder; perpendicularity0.010 toA; fillets<=0.20 |
| Main shaft threads | M5x0.5-6g FULLY FORMED Y-12.1..-9 and14.5..18.2; root4.30 runoutsY-9..-8.5/14..14.5;0.30 entry leads at-12.4..-12.1/18.2..18.5; gauge actual nuts |
| Shaft plain passage |4.400/-0.010 atY-18..-12.4; AF4 counterholdY-18..-12.5. ONLY bearing seatsY-8.5..-3.5/9..14 are5f6. Incoming nut additional plainGO4.42/NO_GO4.70 andM5x0.5-6H are DESIGN acceptance, not measured supplier crest limits |
| Stepped coupling |NEW billet jaws input5.050+0.020/-0 atY-32..-18.5; output4.450+0.020/-0 atY-18.5..-12.5; step transition<=0.20axial in shaft gap; split0.30. Actual output grip5.5; no glued liner or certified torque capacity |
| Main crosspin |1.490..1.500x26; crossbores1.500..1.510, axisX/Y2.5/Z20; deburr without reducing retention |
| Bearing housings |16.030±0.005 MIN-bore-envelope, NOT16H6; pair coax0.010DIAMETER to commonA; line-bore mounted fixture |
| Bearing stops | ID13, corner<=0.20; L cavity5.010..5.030, R5.580..5.620, deliberate endplay, no outer-race preload |
| Incoming SKF625-Z | requireP6; inner GO4.991, outer max-ring16.006; select/reject lots, NOT assumed guaranteed envelope from mean diameter |
| Groove geometry | majorR11.28, profileR0.300+0.010/-0, actual root21.960+0/-0.020; nominal cable centre11.25 is prescribed assembly path, not measured seating law |
| Cable | finished7x7 stainless0.48..0.52;190.809325±0.25 free outlet length at0.1N reference; factory NI000032 both ends; pullout/fatigue NOT MEASURED |
| NI pocket |4.20±0.02 x6.2; ACTUAL end blendsR0.350±0.005; manufacturer envelope stepped head3.8x3/stem2.8x3 to fixed outlet; no hand-swaging of loose fittings |
| Drum cap |3M2x0.4-6H,6H gauge; prescribed3mm body engagement; M2 plugs ISO4026M2x4,0.9AF tool |
| Swivel pivots |smooth axle1.995..2.000, fork eyes2.200±0.010; receiver3.040±0.010 on stationary sleeve3.000/-0.005 ID2.020+0.010/-0; pair fork common-axis0.010DIAMETER; sleeve matched to actual fork gap, not rotating-body width |
| Idler axle |custom journal2.994..3.000 Y-2.5..3; head+Y; M2x0.4-6g fully formedY-7.6..-3, root1.55runoutY-3..-2.5 under metal shoulder washer; no M3 thread on this new axle |
| Rotating-stack preload bypass |stationary sleeve/shaft shoulder and real washers carry clamp force; match thrust shims to actual spans for running gap0.025..0.035 and groove midplane±0.005; nominalgap0.030 is not measured free-spin |
| Swivel nuts |4.10±0.02AF pocket,0.600±0.010deep; body halves3.000±0.010; incoming nutAF3.82..4.00/t1.35..1.60; MATCHED trim stockM2x8 to actual closed grip+actual nut+0.55, inspect final exposed tip0.50..0.65 and6g, label matching location |
| Terminal relief |front inner X49..51/Y±7.3/Z-95..-83;1mm deep; retain actual DIN7991 cones toX48.7 and distal clamp belowZ-95; lateral bore web0.5 |
| Skin/Rails |PET0.300±0.020;301spring strip0.200±0.010 x3.000±0.050; actual tapered width and index cut from STEP; no bond stiffness assumed |
| Motor pilot/mount |22.5±0.05, plate3.0±0.1,4holes3.6±0.05;31±0.2square vendor pitch; shaft24±1/5.000-0.012; selectedA0648 pilot2±0.5 |

Axle diameter2.994..3.000 is a custom design acceptance interval; no unverified
claim of its complete ISO tolerance-table provenance is made. Reject any
standard axle not matching the actual required envelope and smooth span.
All brass/steel/aluminium/PET/301 material identities in BOM are procurement
requirements. Require certificates, but no fatigue, allowable strain, clamp
friction, thread strength, pin shear or torque capacity is certified here.
Small0.45mm receiver pocket rim and1mm Root-dock edge ligament require
micro-machining/deburring inspection and Stage2 load proof before use.
Captive hex-pocket internal cornerR<=0.15 is allowed: minimum4.08AF pocket
vs maximum4.00AF nut gives0.046188mm radial corner allowance; R0.15 at120°
intrudes0.023205mm, leaving0.022983mm. This corner allowance is NOT permission
to round the actual bearing/thread datums. Matched screw length design
interval6.61..7.09 is covered by stock8mm; actual readings stay blank until
hardware exists. Convex external envelope test includes bolt axial[-0.03,+0.10],
nut[-0.02,+0.10], lateral±0.05, all31poses. Not a blanket all-tolerance CCD claim.

Supplier basis preserved: SKF625-Z drawing/P6table3 and Minebea shaft-fit
table; CarlStahl NI000032 drawing and6x7-WSC42d recommendation; DIN7991
M3 head6x1.7/2AF (not ISO10642); Bossard ISO4026M2x4/0.9AF; STEPPERONLINE
17HS15-1504S1 drawingA0648/2025-07-30. Source URLs and downloaded SHA records
in continuation evidence. No stock, price, purchase or physical measurement
is implied.
