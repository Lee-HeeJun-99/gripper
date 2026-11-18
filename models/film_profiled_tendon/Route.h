#pragma once
#include "../film_lateral_tendon/Route.h"
// Separate experimental route. No change to the qualified lateral route.
namespace regrip_profiled_tendon {
using namespace regrip_film_rail;
inline void validate(const Assembly&m,double amplitude){regrip_lateral_tendon::validate(m,6);if(amplitude!=0&&amplitude!=.5)throw std::invalid_argument("separate 0/.5mm guide profile only");}
inline Vec<AD> guide(const Assembly&m,const Assembly::Local&local,unsigned part,unsigned i,double amplitude){
 const unsigned quarter=(m.nx-1)/4;
 if((m.nx-1)%4||i%quarter)throw std::invalid_argument("profile requires exact quarter stations");
 const unsigned k=i/quarter;
 if(k>4)throw std::invalid_argument("profile station outside finger");
 const double coefficients[5]={1,0,-1,0,1};
 // Reuse the objective cross-section normal rather than a global z offset.
 auto centre=regrip_lateral_tendon::guide(m,local,part,i,6);
 auto ordinary=m.guide(local,part,i,-m.guideOffset);
 auto shifted=m.guide(local,part,i,-m.guideOffset-amplitude*coefficients[k]);
 return add(centre,sub(shifted,ordinary));
}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double amplitude,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 if(amplitude==0)return regrip_lateral_tendon::elements(m,u,T,6,visit,profile);
 regrip_lateral_tendon::validate(m,6);
 if(amplitude!=.5||u.size()!=m.size()||T<0||!std::isfinite(T))throw std::invalid_argument("separate 0/.5mm profile only");
 m.elements(u,0,[&](const Element&e){if(e.kind!=2)visit(e);});
 auto actual=m.rest();for(unsigned i=0;i<u.size();++i)actual[i]=add(actual[i],u[i]);
 const double segment=m.L/4,reference=std::sqrt(segment*segment+amplitude*amplitude);
 double length=0;
 for(unsigned part:{1u,2u})for(unsigned k=0;k<4;++k){unsigned a=(m.nx-1)*k/4,b=(m.nx-1)*(k+1)/4;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local local(ids,actual);auto d=sub(guide(m,local,part,b,amplitude),guide(m,local,part,a,amplitude));auto L=root(dot(d,d));length+=L.v;visit({local.ids,AD(T)*(L-AD(reference)),2});}
 return length;
}
inline double length(const Assembly&m,const std::vector<Point>&u,double amplitude){return elements(m,u,0,amplitude,[](const Element&){});}
}
