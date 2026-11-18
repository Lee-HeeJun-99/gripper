#pragma once
#include "../film_impact/SurfaceEvent.h"
#include "RotatingPlane.h"
namespace regrip_routed_contact {
// Exclusion ONLY. A false result means unresolved, never an impact or a
// license to commit. Same quadratic numerical path, not exact ODE CCD.
template<class Path,class Point>
bool intervalPlaneClear(const Path&p,const std::array<unsigned,3>&tri,const Point&c,
 double radius,double begin,double end,const Point&direction){
 using I=regrip_film_impact::SurfaceInterval;I norm2(0);
 for(unsigned d=0;d<3;++d)norm2=norm2+I(direction[d])*I(direction[d]);
 if(!(norm2.hi>0)||!std::isfinite(norm2.hi))return false;
 I support=I(radius)*I(I::down(std::sqrt(std::max(0.L,norm2.lo))),I::up(std::sqrt(norm2.hi))),a(begin),b(end),half(.5L);
 for(unsigned node:tri){I c0(0),c1(0),c2(0);
  for(unsigned d=0;d<3;++d){I n(direction[d]);c0=c0+n*(I(p.a0[node][d])+I(-c[d]));c1=c1+n*I(p.a1[node][d]);c2=c2+n*I(p.a2[node][d]);}
  for(I v:{c0+a*c1+a*a*c2,c0+half*(a+b)*c1+a*b*c2,c0+b*c1+b*b*c2})if(!(v.lo>support.hi))return false;
 }return true;
}
struct SeparationProof {bool clear=false;unsigned planeQueries=0,subdivisions=0,unresolvedTriangle=0;double unresolvedBegin=0,unresolvedEnd=1,midpointGap=0;};
inline SeparationProof separatedNumericalPath(const regrip_film_impact::QuadraticSurfacePath&p,
 const std::vector<std::array<unsigned,3>>&triangles,regrip_film_impact::SurfacePoint center,double radius){
 p.validate();if(triangles.empty()||!(radius>0)||!std::isfinite(radius))throw std::invalid_argument("separation proof geometry");
 SeparationProof proof;
 for(unsigned id=0;id<triangles.size();++id){const auto&t=triangles[id];proof.unresolvedTriangle=id;regrip_film_impact::certifyTrianglePath(p,t);std::vector<std::pair<double,double>>pending{{0,1}};unsigned budget=0;
  while(!pending.empty()){
   if(++budget>512)return proof;auto [a,b]=pending.back();proof.unresolvedBegin=a;proof.unresolvedEnd=b;pending.pop_back();double middle=(a+b)/2;auto x=p.position(middle);std::vector<regrip_film_rail::Point>local;
   for(unsigned node:t)local.push_back(x.at(node));auto closest=regrip_film_sphere::ClosestPrimitive::evaluate(local,center,radius);regrip_film_rail::Point direction;
   for(unsigned d=0;d<3;++d)direction[d]=closest.point[d].v-center[d];++proof.planeQueries;proof.midpointGap=closest.gap.v;
   if(intervalPlaneClear(p,t,center,radius,a,b,direction)||rotatingPlaneClear(p,t,center,radius,a,b,closest.feature))continue;
   if(closest.gap.v<=0||middle==a||middle==b)return proof;
   pending.emplace_back(middle,b);pending.emplace_back(a,middle);++proof.subdivisions;
  }
 }proof.clear=true;return proof;
}
}
