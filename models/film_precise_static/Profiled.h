#pragma once
#include "../film_precise_tendon/Force.h"
#include "../film_profiled_tendon/Route.h"
namespace regrip_precise_static_profile {
using namespace regrip_transmission;
// Separate static design domain,not an extension of the old .5mm Field API.
// Reuse its objective guide geometry;only the declared profile amplitude varies.
inline Vec<AD> guide(const Assembly&m,const Assembly::Local&local,unsigned part,unsigned i,double amplitude,double outboard=6.){
 if(outboard!=6.&&outboard!=8.&&outboard!=10.)throw std::invalid_argument("separate static6/8/10mm outboard design only");
 auto p=regrip_profiled_tendon::guide(m,local,part,i,amplitude);if(outboard==6.)return p;
 auto width=sub(local.point(m.id(part,i,2)),local.point(m.id(part,i,0)));auto unit=scale(width,inverse(root(dot(width,width))));return add(p,scale(unit,AD((part==1?-1:1)*(outboard-6.))));
}
inline double route(const Assembly&m,const std::vector<Point>&q,double T,double amplitude,const Assembly::Visitor&visit,double outboard=6.){
 if(amplitude==0&&outboard==6.)return regrip_precise_tendon::route(m,q,T,6.,visit);
 regrip_lateral_tendon::validate(m,6.);if(m.nx!=21||(amplitude!=0&&amplitude!=.5&&amplitude!=4.5)||(outboard!=6.&&outboard!=8.&&outboard!=10.)||T<0||!std::isfinite(T)||q.size()!=m.size())throw std::invalid_argument("independent static21-row0/.5/4.5mm profile,6/8/10mm outboard domain");
 auto rest=m.rest();for(unsigned i=0;i<q.size();++i)rest[i]=add(rest[i],q[i]);double length=0,reference=std::sqrt((m.L/4)*(m.L/4)+amplitude*amplitude);
 for(unsigned part:{1u,2u})for(unsigned k=0;k<4;++k){unsigned a=(m.nx-1)*k/4,b=(m.nx-1)*(k+1)/4;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local local(ids,rest);auto d=sub(guide(m,local,part,b,amplitude,outboard),guide(m,local,part,a,amplitude,outboard));auto l=root(dot(d,d));length+=l.v;visit({local.ids,AD(T)*(l-AD(reference)),2});}return length;
}
inline double elements(const Assembly&m,const std::vector<Point>&q,double T,double amplitude,const Assembly::Visitor&visit,double outboard=6.){
 if(amplitude==0&&outboard==6.)return regrip_precise_tendon::elements(m,q,T,6.,visit);
 regrip_precise_tendon::elements(m,q,0,6.,[&](const Element&e){if(e.kind!=2)visit(e);});return route(m,q,T,amplitude,visit,outboard);
}
inline Parts parts(const CoupledPlaneStep&map,const std::vector<Point>&q,double T,double amplitude,double outboard=6.){
 if(amplitude==0&&outboard==6.)return regrip_precise_tendon::parts(map,q,T,6.);
 auto out=regrip_precise_tendon::parts(map,q,0,6.);out.cable=route(map.model,q,T,amplitude,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=map.index[ga];if(i<0)continue;double f=-map.weight[ga]*e.energy.g[a];out.force(i)+=f;out.tendon(i)+=f;for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=map.index[gb];if(j>=0)out.stiffness(i,j)+=map.weight[ga]*map.weight[gb]*e.energy.h[regrip_film::N*a+b];}}},outboard);return out;
}
inline double potential(const Assembly&m,const std::vector<Point>&q,double T,double amplitude,double outboard=6.){
 long double value=0;route(m,q,T,amplitude,[&](const Element&e){value+=static_cast<long double>(e.energy.v);},outboard);return double(value);
}
}
