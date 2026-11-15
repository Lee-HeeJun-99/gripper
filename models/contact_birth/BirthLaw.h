#pragma once
#include "BirthIncrement.h"
#include "Crossing.h"
#include "../closure/Quadrature.h"
namespace regrip_birthlaw {
using namespace regrip_history;
// Relative chord in object MATERIAL coordinates, previous endpoint held fixed.
// Not an exact continuous rigid-body trajectory at finite rotation.
inline ContactResult evaluate(const Pose&p,const Pose&o,const History&old,const V&before,unsigned shape,double radius,double height,double skin,double kn,double kt,double mu,bool tangentOnly=false){
 if(old.active)return evaluateContact(p,o,old,shape,radius,height,skin,kn,kt,mu,false,tangentOnly);
 Vec<First>d{},axes[3],local{};for(int j=0;j<3;++j)d[j]=First(p.p[j]-o.p[j])+First::variable(j)-First::variable(j+6);
 for(int j=0;j<3;++j){V axis{};axis[j]=1;auto a=constantV<First>(rotate(o.q,axis));Vec<First>w{First::variable(9),First::variable(10),First::variable(11)};axes[j]=add(a,cross(w,a));local[j]=dot(axes[j],d);}
 auto geo=geometry(local,shape,radius,height);V after{};for(int j=0;j<3;++j)after[j]=local[j].v;
 if(geo.distance.v>=skin){
  if(dot(sub(after,before),sub(after,before))>1e-24&&regrip_closure::sdf(before,shape,radius,height)>=skin){auto range=regrip_closure::activeInterval(before,after,shape,radius,height,skin);if(range.active())throw std::invalid_argument("birth/death within one chord: subdivide event");}
  return evaluateContact(p,o,old,shape,radius,height,skin,kn,kt,mu,false,tangentOnly);
 }
 // A point already inside at initialization has zero initial extension.
 if(regrip_closure::sdf(before,shape,radius,height)<skin)return evaluateContact(p,o,old,shape,radius,height,skin,kn,kt,mu,false,tangentOnly);
 auto increment=regrip_birthfast::increment(before,local,shape,radius,height,skin);auto elastic=increment.elastic;auto trial=elastic;
 ContactResult r=evaluateContact(p,o,History{},shape,radius,height,skin,kn,kt,0,false,tangentOnly);r.capacity=mu*r.normalForce;
 double norm=std::sqrt(dot(elastic,elastic).v);bool sliding=kt*norm>r.capacity;
 if(r.capacity==0)elastic={First(0),First(0),First(0)};
 else if(sliding){auto squared=dot(elastic,elastic);First magnitude(std::sqrt(squared.v));for(int k=0;k<12;++k)magnitude.g[k]=.5*squared.g[k]/magnitude.v;elastic=scale(elastic,First(mu*kn)*(First(skin)-geo.distance)*invAD(First(kt)*magnitude));}
 Vec<First>force{};for(int j=0;j<3;++j)for(int k=0;k<3;++k)force[k]=force[k]-First(kt)*axes[j][k]*elastic[j];auto moment=cross(d,force);std::array<First,12>w{};
 for(int j=0;j<3;++j){w[j]=force[j];w[j+6]=First(-1)*force[j];w[j+9]=First(-1)*moment[j];}
 for(int j=0;j<12;++j){r.wrench.force[j]+=w[j].v;for(int k=0;k<12;++k)r.wrench.jacobian[12*j+k]+=w[j].g[k];}
 r.next.active=true;r.next.sliding=sliding;V plastic{};for(int j=0;j<3;++j){r.next.local[j]=local[j].v;r.next.normal[j]=geo.normal[j].v;r.next.elastic[j]=elastic[j].v;plastic[j]=trial[j].v-elastic[j].v;}
 r.elasticEnergy=.5*kt*dot(r.next.elastic,r.next.elastic);r.plasticDissipation=r.capacity*std::sqrt(dot(plastic,plastic));r.wrench.energy+=r.elasticEnergy;return r;
}
inline ContactResult value(const Pose&p,const Pose&o,const History&h,const V&before,unsigned shape,double radius,double height,double skin,double kn,double kt,double mu){
 if(h.active)return regrip_history::value(p,o,h,shape,radius,height,skin,kn,kt,mu);
 V x=rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));double gap=regrip_closure::sdf(x,shape,radius,height)-skin;
 if(gap>=0||regrip_closure::sdf(before,shape,radius,height)<skin)return regrip_history::value(p,o,h,shape,radius,height,skin,kn,kt,mu);
 auto e=regrip_birthfast::incrementValue(before,x,shape,radius,height,skin);auto trial=e;ContactResult r;r.normalForce=-kn*gap;r.capacity=mu*r.normalForce;double norm=std::sqrt(dot(e,e));r.next.active=true;r.next.sliding=kt*norm>r.capacity;if(r.capacity==0)e={};else if(r.next.sliding)e=scale(e,r.capacity/(kt*norm));r.next.elastic=e;r.next.local=x;r.next.normal=regrip_birthfast::normal(x,shape,radius,height);auto plastic=sub(trial,e);r.elasticEnergy=.5*kt*dot(e,e);r.plasticDissipation=r.capacity*std::sqrt(dot(plastic,plastic));r.wrench.energy=.5*kn*gap*gap+r.elasticEnergy;return r;
}
}
