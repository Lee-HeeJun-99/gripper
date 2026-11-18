#pragma once
#include "../film_lateral_tendon/Route.h"
namespace regrip_precise_attachment {
using namespace regrip_lateral_tendon;
// Reference-exact variant of the SAME flat-reference attachment potential.
// No parameters,normal forces,stiffnesses or accepted states are corrected.
// Only attachment geometry uses displacement differences before reference
// offsets. Shell and routed tendon remain the historical implementation.
inline Vec<AD> normalDeviation(const Assembly&m,const Assembly::Local&local,unsigned part,unsigned i){
 auto a=local.point(m.id(part,i,0)),b=local.point(m.id(part,i,2)),next=local.point(m.id(part,i+1<m.nx?i+1:i-1,0));double dx=m.L/(m.nx-1);
 auto longitudinal=i+1<m.nx?sub(next,a):sub(a,next);longitudinal[0]=longitudinal[0]+AD(dx);
 if(m.rootGuideSecondOrder&&i==0){longitudinal=sub(add(scale(a,AD(-3)),scale(next,AD(4))),local.point(m.id(part,2,0)));longitudinal[0]=longitudinal[0]+AD(2*dx);}
 auto width=sub(b,a);width[1]=width[1]+AD(m.parts.at(part).width);auto raw=cross(longitudinal,width);auto squared=dot(raw,raw);
 if(!(squared.v>0)||!std::isfinite(squared.v))throw std::domain_error("undefined precise attachment normal;NO epsilon regularization");
 auto norm=root(squared),inv=inverse(norm);Vec<AD>delta{raw[0]*inv,raw[1]*inv,AD(0)};
 // Algebraic rationalization of n_z/|n|-1 on its safe positive branch.
 // Reverse-facing normals use the direct expression;no singular denominator
 // or arbitrary normalization is introduced at a feature/event boundary.
 delta[2]=raw[2].v>0?AD(-1)*(raw[0]*raw[0]+raw[1]*raw[1])*inverse(norm*(raw[2]+norm)):raw[2]*inv-AD(1);return delta;
}
inline void attachments(const Assembly&m,const std::vector<Point>&u,const Assembly::Visitor&visit){
 if(u.size()!=m.size()||m.bondK<0||!std::isfinite(m.bondK))throw std::invalid_argument("finite precise attachment state/parameters required");
 for(unsigned part:{1u,2u})for(unsigned k=0;k<5;++k){unsigned i=(m.nx-1)*k/4;auto nodes=m.guideIds(part,i);unsigned ja=part==1?0:3,jb=ja+1;nodes.push_back(m.id(0,i,ja));nodes.push_back(m.id(0,i,jb));Assembly::Local local(nodes,u);double eta=part==1?(m.railW/2)/(m.W/4):1-(m.railW/2)/(m.W/4);
  auto skin=add(scale(local.point(m.id(0,i,ja)),AD(1-eta)),scale(local.point(m.id(0,i,jb)),AD(eta)));auto centre=scale(add(local.point(m.id(part,i,0)),local.point(m.id(part,i,2))),AD(.5));auto deviation=normalDeviation(m,local,part,i);
  // Reference interpolated Skin and offset Rail centres coincide by design.
  // This expression is their current gap without subtracting global poses.
  auto gap=sub(sub(skin,centre),scale(deviation,AD((m.skinT+m.railT)/2)));visit({local.ids,AD(.5*m.bondK)*dot(gap,gap),1});
 }
}
inline double elements(const Assembly&m,const std::vector<Point>&u,double T,double lateral,const Assembly::Visitor&visit,const PassiveProfile*profile=nullptr){
 validate(m,lateral);if(u.size()!=m.size()||T<0||!std::isfinite(T))throw std::invalid_argument("finite same-law displacement/tension required");
 // Reuse the existing Film kernel verbatim;preserve shell→bond→tendon visit
 // order without evaluating discarded legacy bonds/global-coordinate guides.
 PassiveProfile disabled;const auto&cost=profile?*profile:disabled;
 {PassiveProfile::Scope timer(cost,"shell_AD_and_dispatch");for(const auto&p:m.parts){Film film(p.nx,p.ny,m.L,p.width,{m.E,m.nu,p.thickness});std::vector<Point>q(u.begin()+p.offset,u.begin()+p.offset+p.nx*p.ny);film.elements(q,[&](const auto&ids,const AD&e,bool){auto global=ids;for(auto&i:global)i+=p.offset;visit({global,e,0});},true,true);}}
 {PassiveProfile::Scope timer(cost,"precise_attachment_AD_and_dispatch");attachments(m,u,visit);}
 PassiveProfile::Scope timer(cost,"lateral_route_AD_dispatch");return regrip_lateral_tendon::route(m,u,T,lateral,visit);
}
}
