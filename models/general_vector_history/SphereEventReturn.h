#pragma once
#include "MovingReturn.h"

namespace regrip_general_history {
// Independent fixed-sphere/chord reference. Not arbitrary SDF CCD and not yet
// installed in CurvedContact. The two sphere intersections partition birth,
// active evolution and death, including outside -> outside transit.
struct SphereEventResult {
 regrip_history::Vec<regrip_history::First> elastic;
 regrip_history::First plasticLoss,storedEnergy,detachmentInventory,work,projection;
 double entry=0,exit=1;
 bool birth=false,death=false;
};
inline SphereEventResult sphereEventReturn(const regrip_history::V&before,
 const regrip_history::V&old,const regrip_history::Vec<regrip_history::First>&after,
 double radius,double k,double muKn,unsigned subdivisions){
 using namespace regrip_history;
 if(!(radius>0&&k>0&&muKn>0)||!std::isfinite(radius+k+muKn)||!subdivisions||subdivisions>512)
  throw std::invalid_argument("bounded positive sphere event parameters required");
 for(int j=0;j<3;++j)if(!std::isfinite(before[j])||!std::isfinite(old[j])||!std::isfinite(after[j].v))throw std::invalid_argument("finite sphere event state required");
 auto a=constantV<First>(before),d=sub(after,a);auto aa=dot(d,d),bb=First(2)*dot(a,d),cc=dot(a,a)-First(radius*radius);
 SphereEventResult out;
 auto norm=[](const Vec<First>&v){double h=std::hypot(std::hypot(v[0].v,v[1].v),v[2].v);First n(h);if(h>0)for(int j=0;j<3;++j)for(int q=0;q<12;++q)n.g[q]+=v[j].v/h*v[j].g[q];return n;};
 First lo(0),hi(1);
 if(aa.v==0){if(cc.v>=0){if(dot(old,old)!=0)throw std::invalid_argument("inactive stored history");return out;}}
 else {
  auto disc=bb*bb-First(4)*aa*cc;
  if(disc.v==0&&-bb.v/(2*aa.v)>=0&&-bb.v/(2*aa.v)<=1)throw std::domain_error("grazing event has no unique derivative");
  if(disc.v<=0){if(cc.v<0)throw std::domain_error("inconsistent sphere chord");if(dot(old,old)!=0)throw std::invalid_argument("inactive stored history");return out;}
  // Root values selected geometrically; derivatives follow the IFT, avoiding
  // cancellation-sensitive differentiation of the quadratic root formula.
  double root=std::sqrt(disc.v),r0=(-bb.v-root)/(2*aa.v),r1=(-bb.v+root)/(2*aa.v);
  auto event=[&](double t){First v(t);auto p=add(a,scale(d,First(t)));double denominator=2*dot(p,d).v;
   if(denominator==0)throw std::domain_error("grazing event has no unique derivative");
   auto gap=dot(p,p)-First(radius*radius);for(int q=0;q<12;++q)v.g[q]=-gap.g[q]/denominator;return v;};
  if(r1<=0||r0>=1){if(dot(old,old)!=0)throw std::invalid_argument("inactive stored history");return out;}
  if(r0>=0){lo=event(r0);out.birth=true;}if(r1<=1){hi=event(r1);out.death=true;}
 }
 out.entry=lo.v;out.exit=hi.v;
 if(out.birth&&dot(old,old)!=0)throw std::invalid_argument("new contact must have no stored history");
 auto position=[&](const First&t){return add(a,scale(d,t));};
 auto normalize=[&](const Vec<First>&p){auto n=norm(p);if(n.v==0)throw std::domain_error("sphere center normal undefined;split geometry");return scale(p,invAD(n));};
 auto transport=[](const Vec<First>&e,const Vec<First>&n0,const Vec<First>&n1){auto c=dot(n0,n1);if(c.v<=-1+1e-8)throw std::domain_error("antipodal event transport");auto v=cross(n0,n1);return add(e,add(cross(v,e),scale(cross(v,cross(v,e)),invAD(First(1)+c))));};
 auto e=constantV<First>(old),previous=normalize(position(lo));
 if(std::abs(dot(e,previous).v)>1e-12)throw std::invalid_argument("history not tangent");
 for(unsigned i=1;i<=subdivisions;++i){auto t=lo+(hi-lo)*First(double(i)/subdivisions);auto p=position(t),n=normalize(p);
  auto delta=scale(d,(hi-lo)*First(1./subdivisions));
  auto du=scale(add(transport(sub(delta,scale(previous,dot(previous,delta))),previous,n),sub(delta,scale(n,dot(n,delta)))),First(.5));
  auto carried=transport(e,previous,n),trial=add(carried,du);auto capacity=First(muKn)*(First(radius)-norm(p));
  // At an exactly selected exit root, capacity is mathematically zero. This
  // is an event boundary definition, not a small-denominator/loss cutoff.
  if(out.death&&i==subdivisions)capacity=First(0);
  if(capacity.v<0)throw std::domain_error("negative active sphere capacity");
  auto next=trial;auto length=norm(trial);
  if(k*length.v>capacity.v)next=scale(trial,capacity*invAD(First(k)*length));
  out.plasticLoss=out.plasticLoss+capacity*norm(sub(trial,next));
  out.work=out.work+First(k)*dot(next,du);
  auto change=sub(next,carried);out.projection=out.projection+First(.5*k)*dot(change,change);
  e=next;previous=n;
 }
 out.storedEnergy=First(.5*k)*dot(e,e);out.elastic=e;
 if(out.death){out.detachmentInventory=out.storedEnergy;out.storedEnergy=First(0);out.elastic={};}
 return out;
}
}
