#pragma once
#include "BracketedFilmBirth.h"
#include "FilmRestartHistory.h"
namespace regrip_film_impact {
struct IsolatedFilmImpactStep {
 BracketedFilmBirth birth;
 FilmEventImpulse impact;
 std::vector<regrip_film_rail::Point>position,velocity;
 double remainingGap=0;
};
// Narrow prototype: externally isolated single-material-point impact bracket,
// fixed sphere, constant tension and a contact-free remainder. Persistent or
// multiple contact needs a separate constrained stage; penetration rejects.
inline IsolatedFilmImpactStep isolatedFilmImpactStep(
 const regrip_film_native::CoupledPlaneStep&mechanics,unsigned node,
 regrip_film_rail::Point center,double radius,bool midpointRestart=false){
 using namespace regrip_film_native;
 IsolatedFilmImpactStep result;
 result.birth=resolveFilmBirthBracket(mechanics,{node},center,radius);
 result.impact=filmEventImpulse(mechanics,result.birth.position,result.birth.velocity,{{node}},center,radius,1e-10,1e-12);
 FilmRestartHistory history(mechanics.previous,mechanics.previousVelocity);
 history.impact(result.birth.position,result.birth.velocity,result.impact.postVelocity,result.birth.time);
 double remainder=mechanics.h-result.birth.time;
 if(remainder<=0)throw std::runtime_error("isolated event requires a positive remainder");
 // One-step restart on the POST-impact velocity, never a BDF stencil across it.
 auto reference=history.reference(remainder);
 if(reference.beta!=1)throw std::runtime_error("impact restart history contamination");
 CoupledContactStep after(mechanics.model,mechanics.mass,remainder*(midpointRestart?.5:1.),mechanics.damping,mechanics.T,
  reference.position,reference.velocity,{},true,true);
 auto state=after.solve(reference.velocity);
 result.position=std::move(state.displacement);result.velocity=std::move(state.velocity);
 if(midpointRestart)for(unsigned i=0;i<result.position.size();++i)for(unsigned d=0;d<3;++d){
  result.position[i][d]=2*result.position[i][d]-reference.position[i][d];
  result.velocity[i][d]=2*result.velocity[i][d]-reference.velocity[i][d];
 }
 auto p=add(mechanics.model.rest().at(node),result.position.at(node));
 result.remainingGap=regrip_film_sphere::ClosestPrimitive::evaluate({p},center,radius).gap.v;
 if(result.remainingGap<0)throw std::domain_error("isolated impact remainder needs sustained contact;not silently projected");
 return result;
}
// Narrow cold-start sequence: at most one isolated point impact, zero tension,
// no sustained/recontact constraint. It rejects instead of allowing penetration.
struct IsolatedFilmSequence {
 regrip_film_rail::Assembly model;std::vector<double>mass;double damping;
 FilmRestartHistory history;unsigned node;regrip_film_rail::Point center;double radius;
 bool impacted=false;double time=0;bool midpointRestart=false;
 IsolatedFilmSequence(const regrip_film_native::CoupledPlaneStep&m,unsigned i,
  regrip_film_rail::Point c,double r,bool midpoint=false):model(m.model),mass(m.mass),damping(m.damping),
  history(m.previous,m.previousVelocity),node(i),center(c),radius(r),midpointRestart(midpoint){
  if(m.T!=0)throw std::invalid_argument("isolated sequence currently requires zero tendon tension");
 }
 std::optional<IsolatedFilmImpactStep> advance(double h){
  using namespace regrip_film_native;
  CoupledPlaneStep original(model,mass,h,damping,0,history.position,history.velocity,std::vector<regrip_film_rail::Point>(model.size()),0);
  auto gap=[&](const std::vector<regrip_film_rail::Point>&q){return regrip_film_sphere::ClosestPrimitive::evaluate({add(model.rest().at(node),q.at(node))},center,radius).gap.v;};
  if(!impacted){
   CoupledContactStep probe(model,mass,h,damping,0,history.position,history.velocity,{},true,true);
   auto state=probe.solve(history.velocity);
   if(gap(state.displacement)<0){
    auto event=isolatedFilmImpactStep(original,node,center,radius,midpointRestart);
    history.impact(event.birth.position,event.birth.velocity,event.impact.postVelocity,time+event.birth.time);
    history.accept(event.position,event.velocity,h-event.birth.time);impacted=true;time+=h;return event;
   }
  }
  auto ref=history.reference(h);
  bool midpoint=midpointRestart&&ref.beta==1;
  CoupledContactStep smooth(model,mass,h*(midpoint?.5:ref.beta),damping,0,ref.position,ref.velocity,{},true,true);
  auto state=smooth.solve(history.velocity);
  if(midpoint)for(unsigned i=0;i<state.displacement.size();++i)for(unsigned d=0;d<3;++d){
   state.displacement[i][d]=2*state.displacement[i][d]-ref.position[i][d];
   state.velocity[i][d]=2*state.velocity[i][d]-ref.velocity[i][d];
  }
  if(gap(state.displacement)<0)throw std::domain_error("isolated sequence encounters unhandled contact/recontact");
  history.accept(state.displacement,state.velocity,h);time+=h;return std::nullopt;
 }
};
}
