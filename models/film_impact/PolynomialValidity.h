#pragma once
#include "SweptPlane.h"
#include <vector>
#include <stdexcept>
namespace regrip_film_impact {
// Certify a nonzero triangle cross product throughout a quadratic path.
// An unresolved interval REJECTS; it is not declared physically degenerate.
// Edge coefficients are differenced BEFORE bounding, so common translations
// do not create a fictitious deformation bound.
template<class Path>
void certifyTrianglePath(const Path&path,const std::array<unsigned,3>&triangle){
 using I=SurfaceInterval;
 struct Coefficient{std::array<I,3>v;Coefficient():v{I(0),I(0),I(0)}{}};
 std::array<std::array<Coefficient,3>,2>edges;
 for(unsigned edge=0;edge<2;++edge)for(unsigned d=0;d<3;++d){
  unsigned i=triangle[0],j=triangle[edge+1];
  edges[edge][d].v={I(path.a0.at(j)[d])+I(-path.a0.at(i)[d]),I(path.a1.at(j)[d])+I(-path.a1.at(i)[d]),I(path.a2.at(j)[d])+I(-path.a2.at(i)[d])};
 }
 struct Interval{double a,b;unsigned depth;};std::vector<Interval>pending{{0,1,0}};unsigned visited=0;
 auto negative=[](I x){return I(-x.hi,-x.lo);};
 while(!pending.empty()){
  auto part=pending.back();pending.pop_back();if(++visited>512)throw std::runtime_error("uncertified polynomial triangle validity:interval budget512;not OS exhaustion");
  I a(part.a),b(part.b),half(.5L);std::array<std::array<I,3>,2>box{{{I(0),I(0),I(0)},{I(0),I(0),I(0)}}};
  for(unsigned edge=0;edge<2;++edge)for(unsigned d=0;d<3;++d){const auto&c=edges[edge][d].v;
   std::array<I,3>controls{c[0]+a*c[1]+a*a*c[2],c[0]+half*(a+b)*c[1]+a*b*c[2],c[0]+b*c[1]+b*b*c[2]};
   box[edge][d]=I(std::min({controls[0].lo,controls[1].lo,controls[2].lo}),std::max({controls[0].hi,controls[1].hi,controls[2].hi}));
  }
  bool certified=false;
  for(unsigned d=0;d<3;++d){unsigned j=(d+1)%3,k=(d+2)%3;I cross=box[0][j]*box[1][k]+negative(box[0][k]*box[1][j]);certified|=cross.lo>0||cross.hi<0;}
  if(certified)continue;
  if(part.depth>=20)throw std::runtime_error("uncertified/possibly degenerate polynomial triangle:depth20;normal NOT fabricated");
  double middle=(part.a+part.b)/2;pending.push_back({middle,part.b,part.depth+1});pending.push_back({part.a,middle,part.depth+1});
 }
}
}
