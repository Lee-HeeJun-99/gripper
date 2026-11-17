#pragma once
#include "../film_native_contact/CoupledBDFHistory.h"
#include <optional>
namespace regrip_film_impact {
// State ownership for an event-split integrator. This is not itself a solver.
// Older pre-impact states remain in Jump for auditing, never in BDF references.
struct FilmRestartHistory {
 using State=std::vector<regrip_film_rail::Point>;
 struct Jump{State position,preVelocity,postVelocity,preStepPosition,preStepVelocity;double time;};
 struct Reference{State position,velocity;double beta;};
 State position,velocity,olderPosition,olderVelocity;double lastStep=0;bool ready=false;
 std::optional<Jump> lastJump;
 FilmRestartHistory(State q,State v):position(std::move(q)),velocity(std::move(v)){validate(position,velocity);}
 static void validate(const State&q,const State&v){
  if(q.empty()||q.size()!=v.size())throw std::invalid_argument("film restart state size");
  for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)
   if(!std::isfinite(q[i][d])||!std::isfinite(v[i][d]))throw std::invalid_argument("nonfinite film restart state");
 }
 Reference reference(double h)const{
  if(!std::isfinite(h)||h<=0)throw std::invalid_argument("film restart h");
  if(!ready||h!=lastStep)return {position,velocity,1.};
  using regrip_film_native::CoupledBDFHistory;
  return {CoupledBDFHistory::extrapolate(position,olderPosition),
   CoupledBDFHistory::extrapolate(velocity,olderVelocity),CoupledBDFHistory::beta};
 }
 void accept(State q,State v,double h){
  validate(q,v);if(q.size()!=position.size()||!std::isfinite(h)||h<=0)throw std::invalid_argument("film restart accept");
  olderPosition=position;olderVelocity=velocity;position=std::move(q);velocity=std::move(v);lastStep=h;ready=true;
 }
 void impact(State q,State pre,State post,double eventTime){
  validate(q,pre);validate(q,post);if(q.size()!=position.size()||!std::isfinite(eventTime))throw std::invalid_argument("film restart event");
  lastJump=Jump{q,pre,post,position,velocity,eventTime};position=std::move(q);velocity=std::move(post);
  olderPosition.clear();olderVelocity.clear();ready=false;lastStep=0;
 }
};
}
