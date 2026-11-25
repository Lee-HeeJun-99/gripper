"""Versioned actual-part BOM and dimensioned three-view review drawings.

No overwriting RevH BOM. Not a shop release merely because files exist.
Thread major envelopes MUST NOT be used as tap-drill machining diameters.
"""
import argparse,csv,hashlib,html,json,shutil
from pathlib import Path
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
FEATURES={
 'SHAFT':['DatumA common journal axis X80/Z20; datumB left shoulder Y-3.5','journals5f6 =4.982..4.990; central shoulder OD8/length12.5','left journal Y-18..-3.5; right Y9..18.5','M5x0.5-6g ends, nut engagement2.7; actual end thread zones per nut STEP','transverse pin hole1.500..1.510 atY2.5/Z20; fillets<=0.20','journal coaxiality0.010 design requirement; Ra<=0.8um; gauge inspection required'],
 'PEDESTAL':['16H6 bore16.000..16.011; final nominal16.006; datum axis X80/Z20','abutmentID13; corner<=0.20; shoulder face perpendicularity0.010','L endstop cavity5.010..5.030; R5.580..5.620','pair co-bore after bolting to Palm fixture; align within0.010 design requirement','M3x0.5-6H cap threads; holes in CAD are major envelopes, not tap-drill sizes'],
 'CAP_':['L2mm/R1mm ring plate, OD30 ID13; actual locating lips in STEP','L DIN7991M3x6 flush90deg CSK6x1.7; R ISO4762M3x4','retain selected endplay, no load/preload certification'],
 'DRUM':['datum common axis X80/Z20; bore8.10 +0.02/-0; groove rootR8','transverse pin1.500..1.510 atY2.5/Z20, twoM2x0.4-6H plugs','factory-nipple side cavity4.2D x6.2; max end3.8D x6, stem outletX86','cap3M2x0.4-6H at(X,Z)=(72,15),(72,22),(88,22)','Bezier lead cutR0.65; preserve frozen producer control polygon; NO powered release until bend review'],
 'COUPLING':['nominal5.05bore; split gap0.30;4ISO4762M3x10','upper3.4clearance/lowerM3x0.5-6H;2.5AF actual sockets','needed closure>=0.068mm, nominal gap margin0.232; preload/capacity Stage2'],
 'ROOT':['Rootfront X47..50; Rootback50.5..53.5; actual root stack0.50','clamp bolt axesY+-16/Z5, M3clearance3.4; metal-to-metal nut pair','no adhesive assumed: PET/rails mechanically clamped at both ends','docking top M2x0.4-6H atX53/Y+-8; register3.2D x1.05'],
 'SKIN':['PET0.300+-0.020; flat stress-free manufactured sheet','length100 +10 root; width24 atZ0 ->12 atZ-100','index bore1.60+-0.05, Y0/Z-97, normalX','die/knife cut, deburr edges; no thermal forming or jamming claimed'],
 'RAIL_':['301spring strip0.200+-0.010 x3.000+-0.050','root centreY+-10 ->tip centreY+-4; length110','unbonded slip laminate; root/tip clamps; no invented composite stiffness','fatigue/allowable bending/rolling direction must be tested Stage2'],
 'TERMINAL':['front3mm/back3.5mm; all clamp/relief surfaces authoritative STEP','DIN7991M3x10 atY+-9.5/Z-88; front6D90deg CSK1.7','index boss1.50 vsPET1.60; actual distal5mm capture/endstop','fork smooth2mm axle /2.20bore;1mm lower leading-corner relief','CNC rather than printed surrogate; clamp friction and PET bearing Stage2'],
 'SWIVEL':['split Y0 for factory finished terminal installation','body pocket4.20D x6.2; outlet0.80 atstem outletZ-76; axle2.10D','4ISO4762M2x8 atX39/47,Z-86.5/-74.5,1.5AF','2mm smooth axle11bearing span thenM2end; no fully threaded bearing','nominal side ligament0.8mm; actual allowable strength Stage2'],
 'IDLER':['axisX44/Z25/Y direction; POM grooveR4.5/outerflangeR5.5','bore3.040+-0.010 over smooth3h6 journal, length4','groove axial centreY0; spacersOD5/ID3.1x1','currentD/d18 is not a7x7 life recommendation PASS; redesign pending'],
 'JAMMING_DOCK':['top plate14x50x2, key3.0D x1 into3.2root pocket','twoM2x4 atX53/Y+-8; lowerbridge Y+-24/Z-18..-14','arms2x2 through Palm slots2.6x2.6','replaceable20x4x2 blank,2M2 flangeY+-8/Z-16; future chamber NOT supplied'],
 'CASSETTE_BLANK':['20x4x2; twoM2x0.4-6H through atY+-8/Z-16','normalX boltsM2x4 through dock2.2clearance;2mm thread engagement','future chamber space naturalZ-18..-82, width<=min(18,Skinwidth-2), normal0.8..4.8'],
 'PALM':['actualOD230 (not old prose270),5mm thick Z-12..-7','Finger datum radius50; sectors0/120/240deg','all retained unused holes visible in STEP; not silently deleted','wire sweep slots X25.7..41.3,Y+-0.75 per sector','laminate slot X49.7..55.7,Y+-13; dock-arm slots per STEP','8.4mm web between radial wire slot and laminate slot; inspect1.55mm anchor-hole web'],
 'MOTOR_PLATE':['SOYO SY42STH38-1684A /Pololu2267 manufacturer interface','31+-0.2 square hole pitch;3.6clearance;22.5pilot','motor5mm shaft4.988..5.000; actual shaft24+-1 length','4M3x6 through3mm plate ->3mm nominal engagement vs4.5available; do not bottom','unpowered mechanical interface; no driver/current/torque-speed certification']}
def metadata(n):
 s=n[3:] if n.startswith('F') else n
 if s=='TENDON_WIRE':return ('0.50+-0.02mm7x7 stainless finished cable','PURCHASE','Custom completed tendon with TWO NI000032 ends; CAD outer-envelope installation curve only, not preformed wire; length requirement in wire_CAD_metadata')
 if 'FACTORY_NIPPLE' in s:return ('manufacturer brass finished end','BUNDLED PURCHASE','NI000032 supplied only factory-swaged, part of completed tendon')
 if s=='MOTOR':return ('SOYO SY42STH38-1684A','PURCHASE','Pololu2267; manufacturer drawing; electrical performance not certified')
 if 'BEARING' in s:return ('SKF625-Z P6','PURCHASE','5x16x5; manufacturer lot/mean and single-plane limits inspection')
 if 'NUT' in s or 'BOLT' in s or 'PLUG' in s:return ('steel specified standard fastener','PURCHASE','6g/6H nominal thread interfaces; select actual listed length/pitch; locking per HenkelTDS')
 if s=='SKIN':return ('PET sheet0.30','MAKE','knife/die cut, drilled index; material certificate and coupon Stage2')
 if s.startswith('RAIL'):return ('301spring strip0.20','MAKE','laser/photochemical cut with deburred edges; root/tip mechanical clamping')
 if s=='IDLER':return ('POM','MAKE','turn/ream on common setup;3.040+-0.010 running bore')
 if any(k in s for k in ('SHAFT','PIN','AXLE','SPACER','WASHER','CAP_','SWIVEL')):return ('303stainless prototype stock','MAKE','turn/mill/ream; thickness, interface and design intent in actual STEP/drawing; allowables not certified')
 return ('6061-T6 aluminium','MAKE','CNC mill/turn; finished-interface drawings plus actual STEP; no blanket printed replacement')
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'cad/drawings'/a.tag;out.mkdir(parents=True,exist_ok=False);bom=ROOT/'bom'/a.tag;bom.mkdir(exist_ok=False)
 if idx.get('design_geometry',{}).get('wire_model')=='planar_tangent_nipple':
  FEATURES['PEDESTAL']=['datum common bearing axisX80/Z20; actual carrier/stop STEP unchanged except seat','CUSTOM seat16.030+-0.005 minimum-bore-envelope; NOT16H6','housing pair co-bore/inspect coaxiality0.010DIAMETER to common axisA','abutmentID13; edge fillet<=0.20; L cavity5.010..5.030/R5.580..5.620','L M3x0.5-6H cap threads6mm through/R3mm; CAD major envelopes NOT drill sizes']
  FEATURES['SHAFT']=['datumA common journal axisX80/Z20; shoulder facesY-3.5/9','journals5f6=4.982..4.990 MAX-MATERIAL ENVELOPE; journal coaxiality0.005DIAMETER','centralOD8/length12.5; shaft endsY-18/18.5; journals Ra<=0.8um','M5x0.5-6g zonesY-12.2..-8.5 and14..18.5; release chamfer/runout under washers','cross hole1.500..1.510 atY2.5/Z20; abutment fillets<=0.20']
  FEATURES['DRUM']=['axisX80/Z20; bore8.10 +0.02/-0; flangeOD34; rootD22+-0.02','U-groove profileR0.28 +0.03/-0; outward-open, no small3D transfer','tangent NI stem outletX80/Y0/Z8.75; maximum end3.8x6','body side pocket6.2x6.2/R1 from+Y, floorY-2.2; use2mm flat endmill','M2x0.4-6H cap axes(X,Z)=(69,26),(91,26),(80,33)','transverse1.500..1.510 hole Y2.5/Z20; pin1.49..1.50x26 fromX67..93','twoISO4026M2x4 plugs atX63..67/93..97;0.9AF sockets; plugs retain, pin carries torque']
  FEATURES['SWIVEL']=['splitY0 body for factory finished NI end; pocket4.2D x6.2, outlet0.8 atstemZ-76','actual0.6mm open head spotfaces and4.10AF nut recesses;4M2trimmed7mm screws','trim purchased ISO4762M2x8 to7 underhead, rechamfer/deburr/gauge6g','pocket internal edgeR<=0.15, clearance to max3.8end>=0.04 with4.2+-0.02 pocket','axle2.10 bore over smooth2mm pin; NUThex pocket anti-rotation, capacity Stage2']
  FEATURES['ROOT']=['actual RootfrontX47..50/Back50.5..53.5; nominal clamp stack0.50','PET0.30+-0.02 + rails0.20+-0.01 ->0.47..0.53, front plate floats+-0.03','M3clearance3.4 atY+-16/Z5; root foot M3x12/nuts before drive/dock','docking pad width20, M2atX53/Y+-8; actual1mm edge ligament','unbonded slip laminate mechanically captured at both ends; NO adhesive strength assumption']
  FEATURES['IDLER']=['axisX44/Z25/Y; POM rootD22+-0.02/flangesD25','U profileR0.28 +0.03/-0; bore3.040+-0.010 over smooth3h6 journal','axial centreY0; actual sleeve spacers1mm; radial play/creep strength Stage2','minimum root21.98>=42xmax wire0.52=21.84; recommendation, NOT fatigue test']
  FEATURES['MOTOR_PLATE'] += ['actual entire motor/mount/MF bolts Y-1; motor holesY-36.5 on NEW Palm blank','shaft24+-1 yields actual axial gap1..3 to output shaft; nominal2','pilot projection not dimensioned by source: incoming require<=3mm and clearance check, NOT claimed catalogue data']
  FEATURES['PALM']=['actualOD230/t5/Z-12..-7; root radius50, sectors0/120/240','NEW blank, not shifted-hole rework; current MF holesX63/97,Y-36.5 per sector','radial wire slotsX21.5..41.3/Y+-0.75; root slotX49.7..55.7/Y+-13','all other exact hole coordinates/axes/diameters in FACE_FEATURES.csv and STEP','arms use2.6x2.6 through-slots; incoming co-boring fixture and gauges mandatory']
  FEATURES.update({'IDLER_BRACKET':['2mm axle-support plate, base4mm; actual open wire relief, source STEP','axle bore3.4M3 clearance; smooth axle clamps through bracket, NOT a precision dowel fit','base3.4 through X34.5/Y-4; actualM3x12/5.5AF nut; mount BEFORE tendon'],
   'IDLER_AXLE':['custom smooth3h6 spanY-5..3, length8; M3x0.5-6g endY3..7','head5.5x3 atY-8..-5,2.5AF socket; no fully threaded bearing journal'],
   'SWIVEL_AXLE':['smooth2mm length11/Y-5.5..5.5 thenM2end to8.5','head3.8x2,Y-7.5..-5.5,1.5AF socket; nut1.6 and0.5thrust spacers'],
   'DRUM_PIN':['custom ground1.490..1.500 x26; axialX67..93 atY2.5/Z20','deburr; fit1.500..1.510 cross holes; stage2 torque/pin shear NOT MEASURED'],
   'IDLER_SPACER':['steelOD5/ID3.1/t1; axialY; actual two positions in STEP'],
   'INNER_WASHER':['steelOD8/ID5.1/t0.5; SKF abutment7.4..8.3','inner races clamped only, bearing outer faces deliberately retain endplay'],
   'SWIVEL_SPACER':['steelOD4/ID2.1/t0.5; free axle clearance, nut not crushing rotating receiver']})
 rows=[];draw=[]
 for n,v in idx['parts'].items():
  f=ROOT/v['path'];m=trimesh.load(f.with_suffix('.stl'),force='mesh');mat,kind,method=metadata(n);s=n[3:] if n.startswith('F') else n
  if idx.get('design_geometry',{}).get('captive_swivel_nuts') and s.startswith('SWIVEL_BOLT'):
   kind='FINISH PURCHASED';mat='A2-70 procurement requirement, certificate REQUIRED';method='Trim purchased ISO4762M2x8 to7 under-head, guard nut during cut, rechamfer/deburr/gauge6g; no invented measured strength'
  keys={**{k:k for k in ('SHAFT','SKIN','PALM','IDLER','MOTOR_PLATE','JAMMING_DOCK')},**{s:k for k,ss in {'PEDESTAL':['PEDESTAL_L','PEDESTAL_R'],'CAP_':['CAP_L','CAP_R'],'DRUM':['DRUM','DRUM_NIPPLE_CAP'],'COUPLING':['COUPLING_LOWER','COUPLING_UPPER'],'ROOT':['ROOT_FRONT','ROOT_BACK'],'RAIL_':['RAIL_L','RAIL_R'],'TERMINAL':['TERMINAL_FRONT','TERMINAL_BACK'],'SWIVEL':['SWIVEL_LOWER','SWIVEL_UPPER'],'CASSETTE_BLANK':['CASSETTE_BLANK_ADAPTER']}.items() for s in ss}}
  key=keys.get(s,s if s in FEATURES else next((k for k in ('IDLER_SPACER','INNER_WASHER','SWIVEL_SPACER') if s.startswith(k)),''));features=FEATURES.get(key,[])
  rows.append(dict(part_ID=n,quantity=1,purchase_quantity=0 if kind=='BUNDLED PURCHASE' else 1,material=mat,make_or_buy=kind,method=method,actual_producer_detail=v.get('process','See preserved RevH source/audit for inherited part'),dimensions_XYZ_mm=np.round(m.extents,6).tolist(),datum_bounds_mm=np.round(m.bounds,6).tolist(),STEP=str(f.relative_to(ROOT)),STL=str(f.with_suffix('.stl').relative_to(ROOT)),STEP_SHA256=hashlib.sha256(f.read_bytes()).hexdigest(),interface_notes='; '.join(features),physical_qualification='NOT MEASURED; Stage1 geometry only'))
  if n.startswith(('F1_','F2_')) or kind!='MAKE':continue
  lo,hi=m.bounds;parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1000" viewBox="0 0 1400 1000">','<rect width="1400" height="1000" fill="white"/>',f'<text x="20" y="25">{n} / {a.case} / mm / THREE-VIEW REVIEW — NOT SHOP RELEASED</text>']
  # Real exported edges, not a decorative schematic. All-edge projection
  # intentionally exposes hidden features; dimension tables are authoritative.
  edges=m.edges_unique;edges=edges[::max(1,len(edges)//16000)]
  for (u,w),ox,oy,label in [((0,2),20,60,'XZ'),((0,1),470,60,'XY'),((1,2),920,60,'YZ')]:
   scale=min(380/max(hi[u]-lo[u],1),380/max(hi[w]-lo[w],1));parts.append(f'<text x="{ox}" y="{oy}">{label} datum bounds {lo[[u,w]].round(3).tolist()} to {hi[[u,w]].round(3).tolist()}</text>')
   for e in edges:
    q=(m.vertices[e][:,[u,w]]-lo[[u,w]])*scale
    parts.append(f'<path d="M{ox+20+q[0,0]:.4f},{oy+400-q[0,1]:.4f} L{ox+20+q[1,0]:.4f},{oy+400-q[1,1]:.4f}" stroke="#444" stroke-width=".3"/>')
   parts.append(f'<text x="{ox+20}" y="{oy+425}">Overall {hi[u]-lo[u]:.4f} x {hi[w]-lo[w]:.4f} mm; scale{scale:.3f}px/mm</text>')
  notes=[f'Material/process: {mat}; {method}','World coordinate model: sectors0/120/240deg. F1/F2 rotate F0 120/240deg; do not remachine world-angle datums.','Unspecified CNC linear +-0.10mm, drilled clearance +-0.05mm, hole position +-0.05mm DESIGN REQUIREMENTS; inspection mandatory.','Thread faces in STEP use MAJOR envelopes, NOT tap-drill sizes; M2cut drill1.6, M3cut drill2.5, inspect6H after deburr.','CAD omits thread helices. Use actual supplied screw standard; do not substitute larger ISO10642 heads forDIN7991.']+features+['BRep STEP is authority for curved/hidden surfaces; this all-edge view is not a complete fabrication approval.','Supplier bend-radius/terminal-length disposition and independent drawing review remain OPEN.']
  for i,line in enumerate(notes):parts.append(f'<text x="20" y="{540+i*23}" font-size="13">{html.escape(line)}</text>')
  parts.append('</svg>');(out/(n+'.svg')).write_text('\n'.join(parts));draw.append(n)
 with (bom/'STAGE1_BOM.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (bom/'MANUFACTURING_INTERFACES.json').write_text(json.dumps(FEATURES,indent=2));shutil.copyfile(__file__,out/'producer.py')
 result=dict(case=a.case,BOM_rows=len(rows),drawings=draw,scope='Actual CAD-linked BOM and dimensioned three-view review packet; thread/process/fit requirements specified but supplier bend compatibility and final drawing review open.',shop_release=False,stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(BOM_rows=len(rows),review_drawings=len(draw),shop_release=False)))
if __name__=='__main__':main()
