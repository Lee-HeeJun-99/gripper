#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <limits>
namespace regrip_film_impact {
// Outward long-double intervals for a supporting-plane separation proof.
// This is broadphase exclusion only, never a fabricated contact normal/force.
struct SurfaceInterval {
 long double lo,hi;
 explicit SurfaceInterval(long double x):lo(x),hi(x){}
 SurfaceInterval(long double a,long double b):lo(a),hi(b){}
 static long double down(long double x){return std::nextafter(x,-std::numeric_limits<long double>::infinity());}
 static long double up(long double x){return std::nextafter(x,std::numeric_limits<long double>::infinity());}
 friend SurfaceInterval operator+(SurfaceInterval a,SurfaceInterval b){return {down(a.lo+b.lo),up(a.hi+b.hi)};}
 friend SurfaceInterval operator*(SurfaceInterval a,SurfaceInterval b){std::array<long double,4>v{a.lo*b.lo,a.lo*b.hi,a.hi*b.lo,a.hi*b.hi};return {down(*std::min_element(v.begin(),v.end())),up(*std::max_element(v.begin(),v.end()))};}
};
template<class Path,class Point>
bool sweptSupportingPlaneClear(const Path&path,const std::array<unsigned,3>&triangle,
 const Point&center,double radius,double begin,const Point&direction){
 using I=SurfaceInterval;I norm2(0);
 for(unsigned d=0;d<3;++d)norm2=norm2+I(direction[d])*I(direction[d]);
 if(!(norm2.hi>0)||!std::isfinite(norm2.hi))return false;
 I support=I(radius)*I(I::down(std::sqrt(std::max(0.L,norm2.lo))),I::up(std::sqrt(norm2.hi)));
 I a(begin),one(1),half(.5L);
 for(unsigned node:triangle){I c0(0),c1(0),c2(0);
  for(unsigned d=0;d<3;++d){I n(direction[d]);c0=c0+n*(I(path.a0[node][d])+I(-center[d]));c1=c1+n*I(path.a1[node][d]);c2=c2+n*I(path.a2[node][d]);}
  // Degree-two Bernstein controls on [begin,1]. Every material point of
  // every intermediate triangle lies in the hull of these nine controls.
  for(I control:{c0+a*c1+a*a*c2,c0+half*(one+a)*c1+a*c2,c0+c1+c2})
   if(!(control.lo>support.hi))return false;
 }
 return true;
}
}
