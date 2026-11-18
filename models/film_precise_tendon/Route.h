#pragma once
#include "../film_precise_attachment/Elements.h"
namespace regrip_precise_tendon {
using namespace regrip_lateral_tendon;
inline Vec<AD> guideDisplacement(const Assembly&m,const Assembly::Local&local,unsigned part,unsigned i,double lateral){
 auto a=local.point(m.id(part,i,0)),b=local.point(m.id(part,i,2));auto width=sub(b,a);width[1]=width[1]+AD(m.parts.at(part).width);auto norm2=dot(width,width);
 if(!(norm2.v>0)||!std::isfinite(norm2.v))throw std::domain_error("undefined material guide width;NO regularization");
 auto norm=root(norm2),inv=inverse(norm);Vec<AD>dw{width[0]*inv,AD(0),width[2]*inv};dw[1]=width[1].v>0?AD(-1)*(width[0]*width[0]+width[2]*width[2])*inverse(norm*(width[1]+norm)):width[1]*inv-AD(1);
 auto normal=regrip_precise_attachment::normalDeviation(m,local,part,i);return add(sub(scale(add(a,b),AD(.5)),scale(normal,AD(m.guideOffset))),scale(dw,AD(part==1?-lateral:lateral)));
}
// EXACT algebraic decomposition for constant tension along each routed rail:
// sum(|d|-L0)=DeltaGuideEnd_x-DeltaGuideRoot_x+sum(|d|-d_x).
// The linear terms telescope BEFORE floating-point assembly. No nodal force,
// stiffness or accepted state is corrected after evaluating the potential.
inline double route(const Assembly&m,const std::vector<Point>&u,double T,double lateral,const Assembly::Visitor&visit){
 validate(m,lateral);if(u.size()!=m.size()||T<0||!std::isfinite(T))throw std::invalid_argument("finite material tendon state required");double increment=0;
 for(unsigned part:{1u,2u}){
  auto ids=m.guideIds(part,0),last=m.guideIds(part,m.nx-1);ids.insert(ids.end(),last.begin(),last.end());Assembly::Local end(ids,u);auto displacement=sub(guideDisplacement(m,end,part,m.nx-1,lateral),guideDisplacement(m,end,part,0,lateral));increment+=displacement[0].v;visit({end.ids,AD(T)*displacement[0],2});
  for(unsigned k=0;k<m.guideIntervals;++k){unsigned a=(m.nx-1)*k/m.guideIntervals,b=(m.nx-1)*(k+1)/m.guideIntervals;auto nodes=m.guideIds(part,a),next=m.guideIds(part,b);nodes.insert(nodes.end(),next.begin(),next.end());Assembly::Local local(nodes,u);auto d=sub(guideDisplacement(m,local,part,b,lateral),guideDisplacement(m,local,part,a,lateral));d[0]=d[0]+AD(m.L/m.guideIntervals);auto squared=dot(d,d);
   if(!(squared.v>0)||!std::isfinite(squared.v))throw std::domain_error("collapsed material tendon segment;NO epsilon");
   auto length=root(squared);AD correction=d[0].v>0?(d[1]*d[1]+d[2]*d[2])*inverse(length+d[0]):length-d[0];increment+=correction.v;visit({local.ids,AD(T)*correction,2});
  }
 }return 2*m.L+increment;
}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double lateral,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 regrip_precise_attachment::elements(m,u,0,lateral,[&](const Element&e){if(e.kind!=2)visit(e);},profile);return route(m,u,T,lateral,visit);
}
}
