#pragma once
#include "../contact_history/MaterialHistory.h"

namespace regrip_general_history {
// First-yield event for an AFFINE vector trial in a FIXED tangent plane with
// affine capacity. NOT a changing-normal path or a complete friction integrator.
// Initial state must be strictly sticking; the endpoint must be strictly outside.
// Then g(alpha)=k²|e0+alpha*du|²-(c0+alpha*dc)² has exactly one entering
// root in(0,1). Its IFT derivative is not omitted or regularized.
inline regrip_history::First firstYield(
    const regrip_history::V &old,
    const regrip_history::Vec<regrip_history::First> &du,
    double k,double c0,const regrip_history::First &c1,
    const regrip_history::V &normal={0,0,1}) {
  using namespace regrip_history;
  if(!std::isfinite(k)||k<=0||!std::isfinite(c0)||c0<=0||!std::isfinite(c1.v)||c1.v<0)
    throw std::invalid_argument("positive stiffness/initial capacity and finite final capacity");
  for(double x:old)if(!std::isfinite(x))throw std::invalid_argument("finite old history");
  for(auto x:du)if(!std::isfinite(x.v))throw std::invalid_argument("finite vector increment");
  for(double x:normal)if(!std::isfinite(x))throw std::invalid_argument("finite tangent normal");
  double tolerance=128*std::numeric_limits<double>::epsilon();
  if(std::abs(dot(normal,normal)-1)>tolerance||std::abs(dot(old,normal))>tolerance*std::sqrt(dot(old,old)))
    throw std::invalid_argument("unit normal and tangential initial history required");
  // The affine trial is in the tangent plane. Project the INPUT increment,
  // including its AD derivative,not the returned history or friction components.
  auto tangent=sub(du,scale(constantV<First>(normal),dot(constantV<First>(normal),du)));
  auto dc=c1-First(c0);
  First A=First(k*k)*dot(tangent,tangent)-dc*dc;
  First B=First(2*k*k)*dot(constantV<First>(old),tangent)-First(2*c0)*dc;
  First C(k*k*dot(old,old)-c0*c0);
  if(!(C.v<0&&A.v+B.v+C.v>0))
    throw std::domain_error("strict inside-to-outside yield event required;branch boundaries explicit");
  double lo=0,hi=1;
  for(unsigned j=0;j<64;++j){double m=(lo+hi)/2;
    if((A.v*m+B.v)*m+C.v>0)hi=m;else lo=m;
  }
  double alpha=(lo+hi)/2,denominator=2*A.v*alpha+B.v;
  double scale=std::max(std::abs(A.v),std::abs(B.v));
  if(denominator<=64*std::numeric_limits<double>::epsilon()*scale)
    throw std::domain_error("ill-conditioned yield event;subdivide,do not regularize IFT denominator");
  First out(alpha);
  for(unsigned j=0;j<12;++j)out.g[j]=-(A.g[j]*alpha*alpha+B.g[j]*alpha+C.g[j])/denominator;
  return out;
}
} // namespace regrip_general_history
