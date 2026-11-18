#pragma once
#include "../film_lateral_tendon/Route.h"
namespace regrip_distributed_attachment {
using namespace regrip_film_rail;
inline void validate(const Assembly&m,double mode){regrip_lateral_tendon::validate(m,6);if((mode!=0&&mode!=1&&mode!=2)||m.bondK!=.001||(m.nx-1)%20)throw std::invalid_argument("separate0/1/2 attachment modes,nominalK.001,physical5mm epochs required");}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double mode,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 validate(m,mode);
 if(mode==0)return regrip_lateral_tendon::elements(m,u,T,6,visit,profile);
 double length=regrip_lateral_tendon::elements(m,u,T,6,[&](const Element&e){if(e.kind!=1)visit(e);},profile);
 auto actual=m.rest();for(unsigned i=0;i<u.size();++i)actual[i]=add(actual[i],u[i]);
 // Physical epochs0,5,...100mm,NOT all mesh nodes under mesh refinement.
 // Mode1 trapezoid matches nominal total but increases FREE scalar K because
 // the fixed-root spring is weaker. Mode2 preserves that root clip AND the
 // old FREE sum4*.001N/mm,distributed at20 right-Riemann physical stations.
 for(unsigned part:{1u,2u})for(unsigned k=0;k<=20;++k){unsigned i=(m.nx-1)*k/20;auto nodes=m.guideIds(part,i);unsigned ja=part==1?0:3,jb=ja+1;nodes.push_back(m.id(0,i,ja));nodes.push_back(m.id(0,i,jb));Assembly::Local local(nodes,actual);double eta=part==1?(m.railW/2)/(m.W/4):1-(m.railW/2)/(m.W/4);auto skin=add(scale(local.point(m.id(0,i,ja)),AD(1-eta)),scale(local.point(m.id(0,i,jb)),AD(eta)));auto rail=m.guide(local,part,i,(m.skinT+m.railT)/2),gap=sub(skin,rail);double weight=mode==1?(k==0||k==20?.5:1)*5./20:(k==0?1:4./20);visit({local.ids,AD(.5*m.bondK*weight)*dot(gap,gap),1});}
 return length;
}
inline double length(const Assembly&m,const std::vector<Point>&u,double mode){validate(m,mode);return regrip_lateral_tendon::length(m,u,6);}
}
