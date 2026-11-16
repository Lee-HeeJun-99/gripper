#pragma once
#include "../film_rail_tendon/Kernel.h"
namespace regrip_film_sphere {
using namespace regrip_film_rail;
struct ClosestPrimitive {
 struct Evaluation{AD gap;Vec<AD>point;unsigned feature;};
 static Evaluation evaluate(const std::vector<Point>&positions,Point center,double radius){
  if(positions.empty()||positions.size()>3)throw std::invalid_argument("point/segment/triangle support required");std::vector<Vec<AD>>x;for(unsigned i=0;i<positions.size();++i)x.push_back({AD::variable(positions[i][0],3*i),AD::variable(positions[i][1],3*i+1),AD::variable(positions[i][2],3*i+2)});Vec<AD>c{AD(center[0]),AD(center[1]),AD(center[2])},p=x[0];unsigned feature=0;
  auto ratio=[](const AD&a,const AD&b){if(!(b.v>0))throw std::runtime_error("degenerate closest-feature denominator;no epsilon");return a*inverse(b);};
  if(x.size()==2){auto edge=sub(x[1],x[0]);auto denominator=dot(edge,edge);if(!(denominator.v>0))throw std::runtime_error("collapsed contact edge");auto t=ratio(dot(sub(c,x[0]),edge),denominator);if(t.v>=1){p=x[1];feature=1;}else if(t.v>0){p=add(x[0],scale(edge,t));feature=3;}}
  if(x.size()==3){auto ab=sub(x[1],x[0]),ac=sub(x[2],x[0]),normal=cross(ab,ac);if(!(dot(normal,normal).v>0))throw std::runtime_error("collapsed contact triangle");auto ap=sub(c,x[0]);auto d1=dot(ab,ap),d2=dot(ac,ap);bool selected=false;
   if(d1.v<=0&&d2.v<=0){p=x[0];feature=0;selected=true;}
   auto bp=sub(c,x[1]);auto d3=dot(ab,bp),d4=dot(ac,bp);
   if(!selected&&d3.v>=0&&d4.v<=d3.v){p=x[1];feature=1;selected=true;}
   auto vc=d1*d4-d3*d2;
   if(!selected&&vc.v<=0&&d1.v>=0&&d3.v<=0){p=add(x[0],scale(ab,ratio(d1,d1-d3)));feature=3;selected=true;}
   auto cp=sub(c,x[2]);auto d5=dot(ab,cp),d6=dot(ac,cp);
   if(!selected&&d6.v>=0&&d5.v<=d6.v){p=x[2];feature=2;selected=true;}
   auto vb=d5*d2-d1*d6;
   if(!selected&&vb.v<=0&&d2.v>=0&&d6.v<=0){p=add(x[0],scale(ac,ratio(d2,d2-d6)));feature=4;selected=true;}
   auto va=d3*d6-d5*d4;
   if(!selected&&va.v<=0&&(d4-d3).v>=0&&(d5-d6).v>=0){p=add(x[1],scale(sub(x[2],x[1]),ratio(d4-d3,(d4-d3)+(d5-d6))));feature=5;selected=true;}
   if(!selected){auto denominator=va+vb+vc;p=add(x[0],add(scale(ab,ratio(vb,denominator)),scale(ac,ratio(vc,denominator))));feature=6;}
  }
  auto delta=sub(p,c);if(!(dot(delta,delta).v>0))throw std::runtime_error("undefined sphere normal at closest-point zero distance");return {root(dot(delta,delta))-AD(radius),p,feature};
 }
};
}
