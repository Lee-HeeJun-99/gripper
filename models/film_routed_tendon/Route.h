#pragma once
#include "../film_rail_tendon/Kernel.h"
namespace regrip_routed_tendon {
using namespace regrip_film_rail;
inline void validate(const Assembly&m,double amplitude){if(!std::isfinite(amplitude)||(amplitude!=0&&amplitude!=4.5)||m.guideOffset!=5||m.guideIntervals!=4||!m.rootGuideSecondOrder)throw std::invalid_argument("separate frozen0/4.5mm quadratic route,5mm endpoint offset/four intervals/quadratic root required");}
inline double offset(const Assembly&m,unsigned i,double amplitude){if(amplitude==0)return m.guideOffset;double s=double(i)/(m.nx-1);return m.guideOffset-4*amplitude*s*(1-s);}
// SAME original objective guide/local AD. No new nodal force prescription.
// External potential gauge remains T*(combined_length-200mm),NOT stored energy.
inline double route(const Assembly&m,const std::vector<Point>&u,double T,double amplitude,const Assembly::Visitor&visit){
 validate(m,amplitude);if(u.size()!=m.size()||T<0||!std::isfinite(T))throw std::invalid_argument("routed state/tension invalid");auto actual=m.rest();for(unsigned i=0;i<u.size();++i)actual[i]=add(actual[i],u[i]);double length=0;
 for(unsigned part:{1u,2u})for(unsigned k=0;k<m.guideIntervals;++k){unsigned a=(m.nx-1)*k/m.guideIntervals,b=(m.nx-1)*(k+1)/m.guideIntervals;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local local(ids,actual);auto d=sub(m.guide(local,part,b,-offset(m,b,amplitude)),m.guide(local,part,a,-offset(m,a,amplitude)));auto L=root(dot(d,d));length+=L.v;visit({local.ids,AD(T)*(L-AD(m.L/m.guideIntervals)),2});}return length;
}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double amplitude,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 // Reuse ALL original shell/attachment terms. Discard only zero baseline cable.
 // Conservative limitation:the reused zero-T baseline guide path must also be
 // nondegenerate. This is not a general large-wrap/self-contact model.
 m.elements(u,0,[&](const Element&e){if(e.kind!=2)visit(e);else if(profile)profile->count("discarded_zero_baseline_cable_AD");},profile);
 PassiveProfile disabled;const auto&cost=profile?*profile:disabled;PassiveProfile::Scope timer(cost,"quadratic_route_AD_dispatch");return route(m,u,T,amplitude,visit);
}
inline double length(const Assembly&m,const std::vector<Point>&u,double amplitude){return route(m,u,0,amplitude,[](const Element&){});}
}
