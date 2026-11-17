#pragma once
#include "../film_sphere_contact/ClosestPrimitive.h"
#include "SweptPlane.h"
#include <array>
#include <optional>
namespace regrip_film_impact {
using SurfacePoint=regrip_film_rail::Point;
// q(a)=a0+a*a1+a*a*a2. For implicit midpoint dense output,
// a1=h*v0,a2=h*(v_mid-v0). Not interpolation of two saved frames.
struct QuadraticSurfacePath {
 std::vector<SurfacePoint>a0,a1,a2;
 void validate()const{
  if(a0.empty()||a0.size()!=a1.size()||a0.size()!=a2.size())throw std::invalid_argument("surface path dimensions");
  for(unsigned i=0;i<a0.size();++i)for(unsigned d=0;d<3;++d)
   if(!std::isfinite(a0[i][d])||!std::isfinite(a1[i][d])||!std::isfinite(a2[i][d]))throw std::invalid_argument("nonfinite surface path");
 }
 std::vector<SurfacePoint> position(double a)const{auto p=a0;for(unsigned i=0;i<p.size();++i)for(unsigned d=0;d<3;++d)p[i][d]+=a*(a1[i][d]+a*a2[i][d]);return p;}
 std::vector<SurfacePoint> derivative(double a)const{auto p=a1;for(unsigned i=0;i<p.size();++i)for(unsigned d=0;d<3;++d)p[i][d]+=2*a*a2[i][d];return p;}
 double speedBound()const{
  // Norm of an affine derivative is convex: maximum at an endpoint.
  long double speed=0;for(unsigned i=0;i<a0.size();++i)for(double a:{0.,1.}){
   long double square=0;for(unsigned d=0;d<3;++d){long double v=static_cast<long double>(a1[i][d])+2*a*a2[i][d];square+=v*v;}
   speed=std::max(speed,std::sqrt(square));
  }return std::nextafter(static_cast<double>(speed),std::numeric_limits<double>::infinity());
 }
 double triangleSpeedBound(const std::array<unsigned,3>&triangle,double begin)const{
  long double speed=0;for(unsigned i:triangle)for(double a:{begin,1.}){
   long double square=0;for(unsigned d=0;d<3;++d){long double v=static_cast<long double>(a1.at(i)[d])+2*static_cast<long double>(a)*a2.at(i)[d];square+=v*v;}
   speed=std::max(speed,std::sqrt(square));
  }return std::nextafter(static_cast<double>(speed),std::numeric_limits<double>::infinity());
 }
};
struct SurfaceEventRow {unsigned owner,triangle,feature;double gap,rate;std::array<unsigned,3>support;std::array<double,3>barycentric;SurfacePoint normal;};
struct SurfaceEvent {double fraction,clearUntil;unsigned evaluations;std::vector<SurfaceEventRow>rows;};
inline std::optional<SurfaceEvent> earliestSurfaceEvent(const QuadraticSurfacePath&path,
 const std::vector<std::array<unsigned,3>>&triangles,SurfacePoint center,double radius,
 double fractionTolerance=1e-10,double gapTolerance=1e-10,bool sweptPlaneExclusion=true){
 using namespace regrip_film_rail;using regrip_film_sphere::ClosestPrimitive;
 path.validate();if(triangles.empty()||!std::isfinite(radius)||radius<=0||fractionTolerance<=0||gapTolerance<=0)
  throw std::invalid_argument("surface event input");
 for(double v:center)if(!std::isfinite(v))throw std::invalid_argument("surface center");
 unsigned evaluations=0;
 struct Sample{double gap,rate,advance;};
 auto sample=[&](double a){auto x=path.position(a),v=path.derivative(a);Sample result{std::numeric_limits<double>::infinity(),0,std::numeric_limits<double>::infinity()};
  for(auto t:triangles){std::vector<Point>p;for(unsigned i:t)p.push_back(x.at(i));auto e=ClosestPrimitive::evaluate(p,center,radius);++evaluations;
   Point direction{e.point[0].v-center[0],e.point[1].v-center[1],e.point[2].v-center[2]};
   if(sweptPlaneExclusion&&sweptSupportingPlaneClear(path,t,center,radius,a,direction))continue;
   // Every remaining triangle must remain clear, but distant fast nodes do
   // not bound the motion of this material triangle. This retains the same
   // Hausdorff-distance proof with a sharper per-triangle speed bound.
   result.advance=std::min(result.advance,e.gap.v/path.triangleSpeedBound(t,a));
   double rate=0;for(unsigned j=0;j<9;++j)rate+=e.gap.g[j]*v[t[j/3]][j%3];
   if(e.gap.v<result.gap){result.gap=e.gap.v;result.rate=rate;}
  }return result;
 };
 double a=0,L=path.speedBound();auto current=sample(a);
 if(!(current.gap>0))throw std::domain_error("surface birth requires strictly separated initial surface;use sustained/release state");
 if(L==0)return std::nullopt;
 for(unsigned iteration=0;iteration<512;++iteration){
  if(current.advance>1-a)return std::nullopt;
  double root=a;
  bool found=current.gap==0&&current.rate<0;
  if(!found&&current.gap<=gapTolerance&&current.rate<0){
   double hi=std::min(1.,a+2*current.gap/(-current.rate));
   // All prior time is cleared by conservative advances. Do not allow a
   // Newton probe to jump over distinguishable intervening events.
   if(hi>a&&hi-a<=fractionTolerance){auto right=sample(hi);
    if(right.gap<=0){double lo=a;
     for(unsigned j=0;j<64;++j){double mid=(lo+hi)/2;if(mid==lo||mid==hi)break;auto s=sample(mid);if(s.gap>0)lo=mid;else{hi=mid;right=s;}}
     root=hi;found=std::abs(right.gap)<=gapTolerance&&right.rate<0;
    }
   }
  }
  if(found){SurfaceEvent event{root,a,evaluations,{}};auto x=path.position(root),v=path.derivative(root);
   for(unsigned id=0;id<triangles.size();++id){auto t=triangles[id];std::vector<Point>p;for(unsigned i:t)p.push_back(x.at(i));auto e=ClosestPrimitive::evaluate(p,center,radius);
    double rate=0;for(unsigned j=0;j<9;++j)rate+=e.gap.g[j]*v[t[j/3]][j%3];
    if(std::abs(e.gap.v)>gapTolerance||rate>=0)continue;
    if(e.gap.v>0&&e.gap.v/(-rate)>fractionTolerance)continue;
    Point point{e.point[0].v,e.point[1].v,e.point[2].v};auto normal=sub(point,center);normal=scale(normal,1/std::sqrt(dot(normal,normal)));
    auto ab=sub(p[1],p[0]),ac=sub(p[2],p[0]),ap=sub(point,p[0]);double aa=dot(ab,ab),bb=dot(ab,ac),cc=dot(ac,ac),den=aa*cc-bb*bb;
    if(!(den>0))throw std::domain_error("surface row degenerate barycentric basis");double b=(cc*dot(ab,ap)-bb*dot(ac,ap))/den,c=(aa*dot(ac,ap)-bb*dot(ab,ap))/den;
    event.rows.push_back({static_cast<unsigned>(event.rows.size()),id,e.feature,e.gap.v,rate,t,{1-b-c,b,c},normal});
   }
   if(event.rows.empty())throw std::runtime_error("surface event has no owned entering rows");return event;
  }
  double next=std::min(1.,a+current.advance);
  if(next<=a)throw std::runtime_error("unresolved surface grazing/roundoff;no epsilon denominator");
  a=next;current=sample(a);
  if(current.gap<0&&std::abs(current.gap)>gapTolerance)throw std::runtime_error("surface advance lost clearance bound");
 }
 throw std::runtime_error("surface event budget512;not OS exhaustion");
}
}
