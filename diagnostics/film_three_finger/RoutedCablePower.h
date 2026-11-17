#pragma once
#include "../../models/film_rail_tendon/Kernel.h"
namespace regrip_cable_observer {
using namespace regrip_film_rail;
struct Power {double length=0,shorteningRate=0;};
// Read-only derivative of the EXISTING guide geometry. No new cable force law,
// history update or stored energy. Positive actuator power is T*shorteningRate.
inline Power evaluate(const Assembly&m,const std::vector<Point>&u,const std::vector<Point>&v){
 if(u.size()!=m.size()||v.size()!=m.size()||!m.guideIntervals||(m.nx-1)%m.guideIntervals)throw std::invalid_argument("routed power dimensions/guide intervals");
 auto actual=m.rest();for(unsigned i=0;i<u.size();++i)actual[i]=add(actual[i],u[i]);Power out;
 for(unsigned part:{1u,2u})for(unsigned k=0;k<m.guideIntervals;++k){unsigned a=(m.nx-1)*k/m.guideIntervals,b=(m.nx-1)*(k+1)/m.guideIntervals;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local local(ids,actual);auto d=sub(m.guide(local,part,b,-m.guideOffset),m.guide(local,part,a,-m.guideOffset));AD length=root(dot(d,d));
  if(!std::isfinite(length.v)||!(length.v>0))throw std::domain_error("undefined routed length/normal;no regularization");out.length+=length.v;
  for(unsigned i=0;i<3*local.ids.size();++i){if(!std::isfinite(length.g[i])||!std::isfinite(v[local.ids[i/3]][i%3]))throw std::domain_error("nonfinite cable derivative/velocity");out.shorteningRate-=length.g[i]*v[local.ids[i/3]][i%3];}
 }
 return out;
}
}
