#pragma once
#include "TemporalYield.h"

namespace regrip_general_history {
// Independent prescribed-path integrator. All intermediate elastic history,
// normalized normals and capacity carry endpoint derivatives. This is a
// substepped backward return,NOT event-exact CCD or the production SOFA law.
// Preconditions:already active contact,positive capacity throughout,no death.
// Path:affine material displacement,normalized normal chord,affine capacity.
struct MovingResult {
 regrip_history::Vec<regrip_history::First> elastic;
 regrip_history::First plasticLoss,storedEnergy,work,projection;
 unsigned slippingSubsteps=0;
};
inline MovingResult movingReturn(const regrip_history::V&old,
 const regrip_history::V&normal0,
 const regrip_history::Vec<regrip_history::First>&increment,
 const regrip_history::Vec<regrip_history::First>&normal1raw,
 double k,double capacity0,const regrip_history::First&capacity1,unsigned subdivisions){
 using namespace regrip_history;
 if(!subdivisions||subdivisions>512||k<=0||!std::isfinite(k)||capacity0<=0||capacity1.v<=0||!std::isfinite(capacity0)||!std::isfinite(capacity1.v))
  throw std::invalid_argument("bounded active positive-capacity path required");
 for(int j=0;j<3;++j)if(!std::isfinite(old[j])||!std::isfinite(normal0[j])||!std::isfinite(increment[j].v)||!std::isfinite(normal1raw[j].v))throw std::invalid_argument("finite path state required");
 auto normalize=[](const Vec<First>&n){auto q=dot(n,n);if(q.v<=0)throw std::domain_error("zero normal");return scale(n,invAD(sqrtAD(q)));};
 auto n0=constantV<First>(normal0);auto n1=normalize(normal1raw);
 if(std::abs(dot(normal0,normal0)-1)>128*std::numeric_limits<double>::epsilon()||
    std::abs(dot(old,normal0))>128*std::numeric_limits<double>::epsilon()*std::sqrt(dot(old,old)))throw std::invalid_argument("initial tangent state");
 if(dot(n0,n1).v<=-1+1e-8)throw std::domain_error("antipodal normal chord;split path");
 auto rotateNormal=[](const Vec<First>&e,const Vec<First>&a,const Vec<First>&b){auto axis=cross(a,b);auto c=dot(a,b);if(c.v<=-1+1e-8)throw std::domain_error("antipodal transport");return add(e,add(cross(axis,e),scale(cross(axis,cross(axis,e)),invAD(First(1)+c))));};
 MovingResult out;auto e=constantV<First>(old),previous=n0;
 for(unsigned i=1;i<=subdivisions;++i){
  First t(double(i)/subdivisions);auto n=normalize(add(scale(n0,First(1)-t),scale(n1,t)));
  auto delta=scale(increment,First(1./subdivisions));
  auto d0=sub(delta,scale(previous,dot(previous,delta))),d1=sub(delta,scale(n,dot(n,delta)));
  auto du=scale(add(rotateNormal(d0,previous,n),d1),First(.5));
  auto transported=rotateNormal(e,previous,n),trial=add(transported,du);
  auto cap=First(capacity0)+(capacity1-First(capacity0))*t;
  auto squared=dot(trial,trial);auto next=trial;
  if(k*k*squared.v>cap.v*cap.v){next=scale(trial,cap*invAD(First(k)*sqrtAD(squared)));++out.slippingSubsteps;}
  auto plastic=sub(trial,next),change=sub(next,transported);
  // Plastic loss may be far smaller than a geometric distance. Do NOT use
  // the inherited geometry sqrt guard(1e-24 squared distance),or a loss cutoff.
  double magnitude=std::hypot(std::hypot(plastic[0].v,plastic[1].v),plastic[2].v);
  if(magnitude>0){First norm(magnitude);for(unsigned a=0;a<12;++a)for(int j=0;j<3;++j)norm.g[a]+=(plastic[j].v/magnitude)*plastic[j].g[a];out.plasticLoss=out.plasticLoss+cap*norm;}
  out.work=out.work+First(k)*dot(next,du);
  out.projection=out.projection+First(.5*k)*dot(change,change);
  e=next;previous=n;
 }
 out.elastic=e;out.storedEnergy=First(.5*k)*dot(e,e);return out;
}
} // namespace regrip_general_history
