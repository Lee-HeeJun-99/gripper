#pragma once
#include "../contact_birth/BirthLaw.h"
// A discrete identity for the EXISTING radial return, not fitted dissipation.
// In the current tangent frame e1 = T e0 + d - p, T is an isometry.
// U1-U0 = kt e1.d - cap|p| - .5 kt |e1-T e0|^2.
// The last term is a derived endpoint-spring integration term, not Coulomb
// dissipation. This does NOT equate material increment work to global nodal work.
namespace regrip_return_audit {
using namespace regrip_history;
struct Balance {
 double oldEnergy=0,newEnergy=0,endpointWork=0,plastic=0,projection=0,detachment=0,residual=0;
};
inline Balance evaluate(const History&old,const regrip_birthlaw::ContactResult&r,
 const V&before,unsigned shape,double radius,double height,double skin,double kt){
 Balance b;b.oldEnergy=old.active?.5*kt*dot(old.elastic,old.elastic):0;
 if(!r.next.active){b.detachment=b.oldEnergy;b.residual=-b.oldEnergy+b.detachment;return b;}
 V e0{},d{};
 if(old.active){
  e0=transport(old.elastic,old.normal,r.next.normal);
  auto delta=sub(r.next.local,old.local);
  auto a=sub(delta,scale(old.normal,dot(old.normal,delta)));
  auto c=sub(delta,scale(r.next.normal,dot(r.next.normal,delta)));
  d=scale(add(transport(a,old.normal,r.next.normal),c),.5);
 }else if(regrip_closure::sdf(before,shape,radius,height)>=skin){
  d=regrip_birthfast::incrementValue(before,r.next.local,shape,radius,height,skin);
 }
 b.newEnergy=r.elasticEnergy;b.endpointWork=kt*dot(r.next.elastic,d);
 auto increment=sub(r.next.elastic,e0);b.projection=.5*kt*dot(increment,increment);
 b.plastic=r.plasticDissipation;
 b.residual=b.newEnergy-b.oldEnergy-b.endpointWork+b.plastic+b.projection;
 return b;
}
}
