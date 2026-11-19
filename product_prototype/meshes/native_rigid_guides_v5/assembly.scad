// PRODUCT CANDIDATE:dimensions mm;hardware/actuator UNCONFIRMED
$fn=64;part="assembly";explode=0;
L=100;W=24;tip=12;skin=0.1;rail=0.5;rw=2;
function w(x)=x<=50?W:W+(tip-W)*(x-50)/50;
module film(){linear_extrude(skin)polygon([[0,-W/2],[50,-W/2],[L,-tip/2],[L,tip/2],[50,W/2],[0,W/2]]);}
module backing(side){translate([0,0,-rail])linear_extrude(rail)polygon([[0,side*W/2],[50,side*W/2],[L,side*tip/2],[L,side*(tip/2-rw)],[50,side*(W/2-rw)],[0,side*(W/2-rw)]]);}
module mount(){difference(){union(){translate([0,-18,-4])cube([7,36,4+skin]);translate([-5,-18,-7])cube([5,36,14]);}for(y=[-14,14]){translate([2.5,y,-5])cylinder(h=10,r=1.7);translate([-6,y,0])rotate([0,90,0])cylinder(h=7,r=1.7);}translate([0,-W/2,-rail])cube([7,W,5]);}}
module guide(){difference(){rotate([0,90,0])cylinder(h=2,r=1.5,center=true);rotate([0,90,0])cylinder(h=3,r=0.6,center=true);}}
module clamp(){difference(){translate([0,-18,skin])cube([5,36,3]);for(y=[-14,14])translate([2.5,y,-1])cylinder(h=5,r=1.7);}}
module palm(){translate([0,0,5])difference(){cylinder(h=8,r=64);translate([0,0,-1])cylinder(h=10,r=30);for(a=[0,120,240],y=[-14,14])rotate([0,0,a])translate([50,y,-1])cylinder(h=10,r=1.7);}}
module motor_plate(){difference(){translate([-25,-20,17])cube([50,40,4]);for(x=[-15,15])hull()for(y=[-12,12])translate([x,y,16])cylinder(h=6,r=1.7);}}
function xa(x)=min(95,5*round(x/5));
function xc(x)=x==90?xa(x)-5:xa(x)+5;
module guide_support(x,side){hull(){for(p=[[xa(x),side*w(xa(x))/2],[xa(x),side*(w(xa(x))/2-2)],[xc(x),side*w(xc(x))/2]])translate([p[0]-.4,p[1]-.4,-rail-.8])cube([.8,.8,.8]);translate([x-1,side*(w(x)/2+14.0)-.6,3-1.5])cube([2,1.2,.8]);}}
module anchor(){guide();} // terminal eyelet;wire knot/end-stop still unverified
module pulley(){difference(){union(){cylinder(h=5,r=8);cylinder(h=1,r=10);translate([0,0,4])cylinder(h=1,r=10);}translate([0,0,-1])cylinder(h=7,r=3);}}
module coupling(){difference(){cylinder(h=12,r=8);translate([0,0,-1])cylinder(h=14,r=3);translate([0,-.5,5])cube([9,1,8]);translate([-9,0,9])rotate([0,90,0])cylinder(h=18,r=1.7);}}
module cartridge(){film();backing(-1);backing(1);translate([0,0,explode])clamp();mount();for(x=[10, 30, 50, 70, 90, 98],side=[-1,1]){guide_support(x,side);translate([x,side*(w(x)/2+14.0),3])if(x==98)anchor();else guide();}}
module finger_frame(a){rotate([0,0,a])translate([50,0,0])multmatrix([[0,0,-1,0],[0,-1,0,0],[-1,0,0,0],[0,0,0,1]])rotate([0,0,0])children();}
if(part=="assembly"){palm();motor_plate();translate([0,0,22])pulley();translate([0,0,29])coupling();for(a=[0,120,240])finger_frame(a)cartridge();}
else if(part=="skin")film();else if(part=="rail_left")backing(-1);else if(part=="rail_right")backing(1);else if(part=="mount")mount();else if(part=="clamp")clamp();else if(part=="guide")guide();else if(part=="palm")palm();else if(part=="motor_plate")motor_plate();else if(part=="anchor")anchor();else if(part=="pulley")pulley();else if(part=="coupling")coupling();
// Guide support stalks,anchors,pulley,coupling and fastening stack require detailed design.
