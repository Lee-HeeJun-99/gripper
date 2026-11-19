// PRODUCT CANDIDATE:dimensions mm;hardware/actuator UNCONFIRMED
$fn=64;part="assembly";explode=0;
L=100;W=24;tip=12;skin=0.1;rail=0.5;rw=2;
function w(x)=x<=50?W:W+(tip-W)*(x-50)/50;
module film(){linear_extrude(skin)polygon([[0,-W/2],[50,-W/2],[L,-tip/2],[L,tip/2],[50,W/2],[0,W/2]]);}
module backing(side){translate([0,0,-rail])linear_extrude(rail)polygon([[0,side*W/2],[50,side*W/2],[L,side*tip/2],[L,side*(tip/2-rw)],[50,side*(W/2-rw)],[0,side*(W/2-rw)]]);}
module mount(){difference(){translate([-5,-18,-4])cube([12,36,8]);for(y=[-14,14])translate([1,y,-5])cylinder(h=10,r=1.7);translate([0,-12,-.5])cube([7,24,1.2]);}}
module guide(){difference(){rotate([0,90,0])cylinder(h=2,r=1.5,center=true);rotate([0,90,0])cylinder(h=3,r=0.6,center=true);}}
module clamp(){difference(){translate([-3,-18,0])cube([8,36,3]);for(y=[-14,14])translate([1,y,-1])cylinder(h=5,r=1.7);}}
module palm(){difference(){cylinder(h=8,r=64);translate([0,0,-1])cylinder(h=10,r=30);for(a=[0,120,240],y=[-14,14])rotate([0,0,a])translate([50,y,-1])cylinder(h=10,r=1.7);}}
module motor_plate(){difference(){translate([-25,-20,12])cube([50,40,4]);for(x=[-15,15])hull()for(y=[-12,12])translate([x,y,11])cylinder(h=6,r=1.7);}}
module cartridge(){film();backing(-1);backing(1);translate([0,0,explode])clamp();mount();for(x=[10, 30, 50, 70, 90, 98],side=[-1,1])translate([x,side*(w(x)/2+4),3])guide();}
module finger_frame(a){rotate([0,0,a])translate([50,0,0])multmatrix([[0,0,-1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1]])children();}
if(part=="assembly"){palm();motor_plate();for(a=[0,120,240])finger_frame(a)cartridge();}
else if(part=="skin")film();else if(part=="rail_left")backing(-1);else if(part=="rail_right")backing(1);else if(part=="mount")mount();else if(part=="clamp")clamp();else if(part=="guide")guide();else if(part=="palm")palm();else if(part=="motor_plate")motor_plate();
// Guide support stalks,anchors,pulley,coupling and fastening stack require detailed design.
