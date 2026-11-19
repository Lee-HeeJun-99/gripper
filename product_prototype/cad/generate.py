"""Shared parametric geometry: OpenSCAD CAD source, STL, tetra FEM, drawings,BOM.
No CAD kernel installed: STEP is deliberately NOT fabricated as a text surrogate.
"""
import argparse,csv,json,math,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def width(c,x):
 f=c['finger'];return f['root_width']+(f['tip_width']-f['root_width'])*max(0,x-f['taper_start'])/(f['length']-f['taper_start'])
def guide_normal(c,x):
 """Shared physical guide route;flat/constant legacy path is unchanged."""
 td=c['tendon'];base=td['normal_offset'];profile=td.get('distal_profile')
 if profile is None:return base
 u=max(0.,min(1.,(x-profile['start_mm'])/(c['finger']['length']-profile['start_mm'])))
 return base+(profile['tip_offset_mm']-base)*u*u*(3-2*u)
def reference_local(c,p):
 """Stress-free manufactured circular distal reference;NOT prescribed motion."""
 x,y,z=p;curve=c['finger'].get('precurve')
 if curve is None or curve['angle_deg']==0 or x<=curve['start_mm']:return [x,y,z]
 start=curve['start_mm'];k=math.radians(curve['angle_deg'])/(c['finger']['length']-start);phi=k*(x-start)
 return [start+math.sin(phi)/k-z*math.sin(phi),y,(1-math.cos(phi))/k+z*math.cos(phi)]
def world(c,p,angle=0):
 x,y,z=reference_local(c,p);tilt=math.radians(c['palm'].get('root_angle_deg',0));x,z=x*math.cos(tilt)-z*math.sin(tilt),x*math.sin(tilt)+z*math.cos(tilt);a=math.radians(angle);r=c['palm']['mount_radius']-z
 # Proper right-handed mount:longitudinal down,width -tangent,normal inward.
 return [r*math.cos(a)+y*math.sin(a),r*math.sin(a)-y*math.cos(a),-x]
def mesh(c):
 f=c['finger'];nx=c['simulation']['nx'];v=[]
 for i in range(nx):
  x=f['length']*i/(nx-1);w=width(c,x)
  for y in (-w/2,-w/2+f['rail_width'],w/2-f['rail_width'],w/2):
   for z in (-f['rail_thickness'],0,f['skin_thickness']):v.append([x,y,z])
 idx=lambda i,j,k:(i*4+j)*3+k
 t=[]
 # Conforming Freudenthal split for each stepped cell;shared interface nodes.
 for i in range(nx-1):
  for j in range(3):
   for k in range(2):
    if k==0 and j==1:continue
    ids=[idx(i+a,j+b,k+d) for a,b,d in ((0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1))]
    for q in ((0,1,3,7),(0,3,2,7),(0,2,6,7),(0,6,4,7),(0,4,5,7),(0,5,1,7)):
     tet=[ids[n] for n in q];p=np.array([v[n] for n in tet]);det=np.linalg.det((p[1:]-p[0]).T)
     if det<0:tet[1],tet[2]=tet[2],tet[1]
     if det==0:raise ValueError('zero tetra volume')
     t.append(tet)
 # Remove unused interior void nodes before exporting.
 used=sorted({n for q in t for n in q});remap={n:i for i,n in enumerate(used)};v=[v[n] for n in used];t=[[remap[n] for n in q] for q in t]
 faces={}
 for q in t:
  for face in ((q[1],q[2],q[3]),(q[0],q[3],q[2]),(q[0],q[1],q[3]),(q[0],q[2],q[1])):faces.setdefault(tuple(sorted(face)),[]).append(face)
 surf=[p[0] for p in faces.values() if len(p)==1]
 if any(len(p)>2 for p in faces.values()):raise ValueError('nonmanifold tets')
 return v,t,surf
def stl(path,v,faces):
 signed=sum(float(np.dot(v[a],np.cross(v[b],v[c]))) for a,b,c in faces)/6
 if signed<0:faces=[(a,c,b) for a,b,c in faces]
 with path.open('w') as s:
  s.write('solid product_candidate\n')
  for tri in faces:
   p=np.array([v[i] for i in tri]);n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n);s.write(' facet normal '+' '.join(map(str,n))+'\n outer loop\n')
   for x in p:s.write(' vertex '+' '.join(map(str,x))+'\n')
   s.write(' endloop\n endfacet\n')
  s.write('endsolid\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--config');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=False);parameter_file=Path(a.config) if a.config else BASE/'config/design_v1.json';c=json.loads(parameter_file.read_text());(out/'config.json').write_text(json.dumps(c,indent=2));v,t,surf=mesh(c);(out/'mesh.json').write_text(json.dumps(dict(local_positions_mm=v,tetrahedra=t,triangles=surf)))
 stl(out/'finger_bonded.stl',v,surf)
 for part in ('skin','rail_left','rail_right'):
  f=c['finger'];vv=[]
  for x in (0,50,100):
   w=width(c,x);ys=(-w/2,w/2) if part=='skin' else ((-w/2,-w/2+f['rail_width']) if part=='rail_left' else (w/2-f['rail_width'],w/2));zs=(0,f['skin_thickness']) if part=='skin' else (-f['rail_thickness'],0)
   vv.extend([[x,y,z] for y in ys for z in zs])
  faces=[]
  for j in range(2):
   b=4*j
   for quad in ((b,b+4,b+5,b+1),(b+2,b+3,b+7,b+6),(b,b+2,b+6,b+4),(b+1,b+5,b+7,b+3)):
    faces.extend([(quad[0],quad[1],quad[2]),(quad[0],quad[2],quad[3])])
  faces.extend([(0,1,3),(0,3,2),(8,10,11),(8,11,9)]);stl(out/(part+'.stl'),vv,faces)
 f=c['finger'];palm=c['palm'];td=c['tendon']
 scad=f'''// PRODUCT CANDIDATE:dimensions mm;hardware/actuator UNCONFIRMED
$fn=64;part="assembly";explode=0;
L={f['length']};W={f['root_width']};tip={f['tip_width']};skin={f['skin_thickness']};rail={f['rail_thickness']};rw={f['rail_width']};
function w(x)=x<=50?W:W+(tip-W)*(x-50)/50;
module film(){{linear_extrude(skin)polygon([[0,-W/2],[50,-W/2],[L,-tip/2],[L,tip/2],[50,W/2],[0,W/2]]);}}
module backing(side){{translate([0,0,-rail])linear_extrude(rail)polygon([[0,side*W/2],[50,side*W/2],[L,side*tip/2],[L,side*(tip/2-rw)],[50,side*(W/2-rw)],[0,side*(W/2-rw)]]);}}
module mount(){{difference(){{union(){{translate([0,-18,-4])cube([7,36,4+skin]);translate([-5,-18,-7])cube([5,36,14]);}}for(y=[-14,14]){{translate([2.5,y,-5])cylinder(h=10,r=1.7);translate([-6,y,0])rotate([0,90,0])cylinder(h=7,r=1.7);}}translate([0,-W/2,-rail])cube([7,W,5]);}}}}
module guide(){{difference(){{rotate([0,90,0])cylinder(h=2,r={td['guide_outer_radius']},center=true);rotate([0,90,0])cylinder(h=3,r={td['guide_hole_radius']},center=true);}}}}
module clamp(){{difference(){{translate([0,-18,skin])cube([5,36,3]);for(y=[-14,14])translate([2.5,y,-1])cylinder(h=5,r=1.7);}}}}
module palm(){{translate([0,0,5])difference(){{cylinder(h=8,r={palm['outer_radius']});translate([0,0,-1])cylinder(h=10,r={palm['inner_radius']});for(a=[0,120,240],y=[-14,14])rotate([0,0,a])translate([50,y,-1])cylinder(h=10,r=1.7);}}}}
module motor_plate(){{difference(){{translate([-25,-20,17])cube([50,40,4]);for(x=[-15,15])hull()for(y=[-12,12])translate([x,y,16])cylinder(h=6,r=1.7);}}}}
function xa(x)=min(95,5*round(x/5));
function xc(x)=x==90?xa(x)-5:xa(x)+5;
module guide_support(x,side){{hull(){{for(p=[[xa(x),side*w(xa(x))/2],[xa(x),side*(w(xa(x))/2-2)],[xc(x),side*w(xc(x))/2]])translate([p[0]-.4,p[1]-.4,-rail-.8])cube([.8,.8,.8]);translate([x-1,side*(w(x)/2+{td['outboard']})-.6,{td['normal_offset']}-1.5])cube([2,1.2,.8]);}}}}
module anchor(){{guide();}} // terminal eyelet;wire knot/end-stop still unverified
module pulley(){{difference(){{union(){{cylinder(h=5,r=8);cylinder(h=1,r=10);translate([0,0,4])cylinder(h=1,r=10);}}translate([0,0,-1])cylinder(h=7,r=3);}}}}
module coupling(){{difference(){{cylinder(h=12,r=8);translate([0,0,-1])cylinder(h=14,r=3);translate([0,-.5,5])cube([9,1,8]);translate([-9,0,9])rotate([0,90,0])cylinder(h=18,r=1.7);}}}}
module cartridge(){{film();backing(-1);backing(1);translate([0,0,explode])clamp();mount();for(x={td['guide_stations']},side=[-1,1]){{guide_support(x,side);translate([x,side*(w(x)/2+{td['outboard']}),{td['normal_offset']}])if(x=={td['guide_stations'][-1]})anchor();else guide();}}}}
module finger_frame(a){{rotate([0,0,a])translate([{palm['mount_radius']},0,0])multmatrix([[0,0,-1,0],[0,-1,0,0],[-1,0,0,0],[0,0,0,1]])rotate([0,{-palm.get('root_angle_deg',0)},0])children();}}
if(part=="assembly"){{palm();motor_plate();translate([0,0,22])pulley();translate([0,0,29])coupling();for(a=[0,120,240])finger_frame(a)cartridge();}}
else if(part=="skin")film();else if(part=="rail_left")backing(-1);else if(part=="rail_right")backing(1);else if(part=="mount")mount();else if(part=="clamp")clamp();else if(part=="guide")guide();else if(part=="palm")palm();else if(part=="motor_plate")motor_plate();else if(part=="anchor")anchor();else if(part=="pulley")pulley();else if(part=="coupling")coupling();
// Guide support stalks,anchors,pulley,coupling and fastening stack require detailed design.
'''
 (out/'assembly.scad').write_text(scad)
 # Orthographic design drawing,not simulated deformation.
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="640" viewBox="0 0 1100 640"><rect width="1100" height="640" fill="white"/><g fill="none" stroke="black"><circle cx="240" cy="240" r="192"/><circle cx="240" cy="240" r="90"/>{''.join(f'<g transform="translate(240 240) rotate({a})"><rect x="140" y="-54" width="36" height="108"/><line x1="150" y1="0" x2="310" y2="0"/></g>' for a in (0,120,240))}<path d="M600 90 L800 90 L1000 114 L1000 138 L800 162 L600 162 Z"/><path d="M600 320 H1000 V322 H600 Z"/><rect x="600" y="325" width="400" height="6"/><rect x="600" y="430" width="240" height="4"/><rect x="600" y="434" width="20" height="20"/><rect x="820" y="434" width="20" height="20"/></g><g font-family="sans-serif" font-size="16"><text x="30" y="30">PRODUCT CANDIDATE — CAD design,NOT simulation</text><text x="75" y="480">TOP:Palm R64/30,mount radius50 mm,3x120deg</text><text x="600" y="65">FINGER PLAN:L100 mm,W24 to12,taper from50</text><text x="600" y="295">SIDE:Skin0.10,Rails0.50 mm (thickness exaggerated)</text><text x="600" y="405">SECTION:Skin + two bonded edge rails</text><text x="600" y="490">M3 clearance3.4 placeholder;motor UNSELECTED</text><text x="30" y="575">Exploded CAD:set explode=15 in assembly.scad. Guide support/anchor/coupling NOT detailed.</text><text x="30" y="610">All dimensions candidate values;manufacturing readiness NOT approved.</text></g></svg>''';(out/'orthographic.svg').write_text(svg)
 with (out/'BOM.csv').open('w') as s:
  w=csv.writer(s);w.writerow(['part','quantity','candidate_dimensions_mm','material','status'])
  for row in [('palm',1,'R64/R30x8','TBD','parametric CAD source'),('mount',3,'12x36x14 L-bracket','TBD','M3 placeholder;tilted mount seating NOT verified'),('skin',3,'100x24->12x0.1','TBD','STL and CAD source'),('rail',6,'100x2x0.5 tapered path','TBD','STL and CAD source'),('guide',6*(len(td['guide_stations'])-1),'OD3 ID1.2 L2','TBD','terminal station counted as anchor,not double counted'),('guide support',6*len(td['guide_stations']),'3-point rail foot to guide centre','TBD','parametric hull;kernel/interference NOT verified'),('root clamp',3,'5x36x3','TBD','parametric CAD source'),('cartridge',3,'skin+rails+mount','assembly','bonded in FEM'),('terminal eyelet anchor',6,'OD3 ID1.2 L2,centre matches cable endpoint','TBD','knot/end-stop retention NOT verified'),('pulley',1,'bend radius >=5 target','TBD','NOT detailed'),('motor plate',1,'50x40x4 slots','TBD','motor NOT selected'),('coupling',1,'TBD','TBD','BLOCKED actuator spec'),('M3 fastener set',16,'stack length TBD','TBD','NOT supplier confirmed')]:w.writerow(row)
 volumes=[np.linalg.det((np.array([v[n] for n in tet])[1:]-v[tet[0]]).T)/6 for tet in t]
 volumes=list(map(float,volumes))
 # Initial finite-radius wire-to-sphere check using actual candidate path.
 center=np.array(c['simulation']['sphere_center_mm']);r=c['simulation']['sphere_radius_mm'];clear=[]
 for angle in palm['angles_deg']:
  for side in (-1,1):
   path=[np.array(world(c,[x,side*(width(c,x)/2+td['outboard']),td['normal_offset']],angle)) for x in td['guide_stations']]
   for p0,p1 in zip(path,path[1:]):
    d=p1-p0;u=np.clip(np.dot(center-p0,d)/np.dot(d,d),0,1);clear.append(float(np.linalg.norm(p0+u*d-center)-r-td['wire_radius']))
 summary=dict(status='GENERATED_CANDIDATE_NOT_FABRICATION_READY',config_sha256=hashlib.sha256(parameter_file.read_bytes()).hexdigest(),vertices=len(v),tetrahedra=len(t),surface_triangles=len(surf),positive_tetrahedra=min(volumes)>0,volume_mm3_per_finger=sum(volumes),initial_wire_sphere_clearance_mm=min(clear),STEP='NOT GENERATED:no CAD kernel installed',assembly='NOT VERIFIED:moving interference/guide supports/anchors/coupling unfinished',parts_STL=['skin.stl','rail_left.stl','rail_right.stl','finger_bonded.stl']);(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
if __name__=='__main__':main()
