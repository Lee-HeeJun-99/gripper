#pragma once
#include "../film_three_finger_event/BracketedBirth.h"
#include "../film_coupled_collocation/EndpointControlledRows.h"
namespace regrip_stationary_contact {
struct Result {
 regrip_three_event::BracketedBirth birth;
 regrip_collocation::EndpointControlledResult after;
 double minimumGap,momentumBound;
};
// EXTERNALLY isolated endpoint-family fixture, NOT a general earliest CCD.
// Reuses the qualified impact and persistent-contact laws, no new forces.
inline Result firstImpact(const regrip_three_finger::SharedFilmSystem&s,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h){
 if(!(time>.0201&&time<.0203)||h!=.0002)throw std::invalid_argument("isolated stationary-origin20.2ms200us fixture required");
 regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
 auto b=regrip_three_event::bracketedBirth(s,q,v,time,h/4,h,c);
 const double remaining=time+h-b.time;if(!(remaining>0))throw std::runtime_error("positive impact remainder required");
 auto after=regrip_collocation::endpointControlledRows(s.shared.M,2,b.before.q,b.impact.state.velocity,b.time,remaining,
  [&](const auto&x,double t){return s.force(x,c.sample(t).tension);},
  [&](const auto&x){return s.geometry(x);},[&](const auto&x){return s.clearance(x);});
 double gap=s.clearance(b.before.q),momentum=b.momentumResidual;
 for(const auto&step:after.accepted){momentum+=step.momentumResidual;for(const auto&stage:step.stages)gap=std::min(gap,s.clearance(stage.q));}
 if(gap< -1e-10||momentum>1e-17)throw std::runtime_error("unchanged impact/remainder gap/momentum bounds failed");
 return {std::move(b),std::move(after),gap,momentum};
}
}
