# Manufacturing definition and acceptance — Rev U candidate

Authority order: controlled interface limits below and per-part BOM notes;
actual native STEP; actual634face catalogue; review three-view SVG. The STEP
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
| Main shaft threads | M5x0.5-6g atY-12.2..-8.5 and14..18.5; relief/chamfer under washers; gauge actual nuts |
| Main crosspin |1.490..1.500x26; crossbores1.500..1.510, axisX/Y2.5/Z20; deburr without reducing retention |
| Bearing housings |16.030±0.005 MIN-bore-envelope, NOT16H6; pair coax0.010DIAMETER to commonA; line-bore mounted fixture |
| Bearing stops | ID13, corner<=0.20; L cavity5.010..5.030, R5.580..5.620, deliberate endplay, no outer-race preload |
| Incoming SKF625-Z | requireP6; inner GO4.991, outer max-ring16.006; select/reject lots, NOT assumed guaranteed envelope from mean diameter |
| Groove geometry | majorR11.28, profileR0.300+0.010/-0, actual root21.960+0/-0.020; nominal cable centre11.25 is prescribed assembly path, not measured seating law |
| Cable | finished7x7 stainless0.48..0.52;190.809325±0.25 free outlet length at0.1N reference; factory NI000032 both ends; pullout/fatigue NOT MEASURED |
| NI pocket |4.20±0.02 x6.2; max end3.8x6; internal cornerR<=0.15; no hand-swaging of loose fittings |
| Drum cap |3M2x0.4-6H,6H gauge; prescribed3mm body engagement; M2 plugs ISO4026M2x4,0.9AF tool |
| Swivel pivots |smooth axle diameter1.995..2.000, bore2.100±0.010; ream paired fork eyes on COMMON AXIS, coax0.010DIAMETER; split-body bore in clamped fixture |
| Idler axle |smooth journal3h6 (custom inspect2.994..3.000), bore3.040±0.010; bore/shoulder axis common; cut threadM3 only on specified end |
| Swivel nuts |4.10AF pocket, nominal0.6deep; M2x7 finished screw underhead7.000±0.050 from stockM2x8; trim/chamfer<=0.10, gauge6g |
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

Supplier basis preserved: SKF625-Z drawing/P6table3 and Minebea shaft-fit
table; CarlStahl NI000032 drawing and6x7-WSC42d recommendation; DIN7991
M3 head6x1.7/2AF (not ISO10642); Bossard ISO4026M2x4/0.9AF; STEPPERONLINE
17HS15-1504S1 drawingA0648/2025-07-30. Source URLs and downloaded SHA records
in continuation evidence. No stock, price, purchase or physical measurement
is implied.
