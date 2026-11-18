#pragma once
#include "../film_rail_tendon/Kernel.h"
namespace regrip_lateral_tendon {
using namespace regrip_film_rail;
inline void validate(const Assembly&m,double lateral){if(!std::isfinite(lateral)||(lateral!=0&&lateral!=6)||m.guideOffset!=5||m.guideIntervals!=4||!m.rootGuideSecondOrder||m.kn!=0)throw std::invalid_argument("separate0/6mm OUTBOARD lateral route,constant5mm normal lever,four guides/quadratic root,NO contact field required");}
inline Vec<AD>guide(const Assembly&m,const Assembly::Local&local,unsigned part,unsigned i,double lateral){
 auto p=m.guide(local,part,i,-m.guideOffset);if(lateral==0)return p;
 auto width=sub(local.point(m.id(part,i,2)),local.point(m.id(part,i,0)));auto squared=dot(width,width);if(!(squared.v>0))throw std::domain_error("collapsed physical rail width;no regularized frame");width=scale(width,inverse(root(squared)));return add(p,scale(width,AD(part==1?-lateral:lateral)));
}
inline double route(const Assembly&m,const std::vector<Point>&u,double T,double lateral,const Assembly::Visitor&visit){
 validate(m,lateral);if(u.size()!=m.size()||T<0||!std::isfinite(T))throw std::invalid_argument("lateral route state/tension invalid");auto actual=m.rest();for(unsigned i=0;i<u.size();++i)actual[i]=add(actual[i],u[i]);double length=0;
 for(unsigned part:{1u,2u})for(unsigned k=0;k<m.guideIntervals;++k){unsigned a=(m.nx-1)*k/m.guideIntervals,b=(m.nx-1)*(k+1)/m.guideIntervals;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local local(ids,actual);auto d=sub(guide(m,local,part,b,lateral),guide(m,local,part,a,lateral));auto L=root(dot(d,d));length+=L.v;visit({local.ids,AD(T)*(L-AD(m.L/m.guideIntervals)),2});}return length;
}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double lateral,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 m.elements(u,0,[&](const Element&e){if(e.kind!=2)visit(e);},profile);
 PassiveProfile disabled;const auto&cost=profile?*profile:disabled;PassiveProfile::Scope timer(cost,"lateral_route_AD_dispatch");return route(m,u,T,lateral,visit);
}
inline double length(const Assembly&m,const std::vector<Point>&u,double lateral){return route(m,u,0,lateral,[](const Element&){});}
}
