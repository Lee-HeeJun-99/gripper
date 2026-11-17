#pragma once
#include "../film_coupled_contact/CoupledSphere.h"
namespace regrip_coupled_adaptive {
using namespace regrip_coupled;
struct Segment {double time,h,error;State before;Result result;};
struct AdaptiveResult {std::vector<Segment>segments;unsigned trials=0,rejected=0,coarseReuses=0,subintegrations=0;double maximumAcceptedError=0,maximumInstantaneousRelativeError=0;};
using EnergyEvaluator=std::function<std::array<double,2>(const Assembly&,const std::vector<Point>&)>;
// Step doubling,not extrapolation:accept the TWO physical half steps only.
// Error includes SMALL nonzero energies/impulse inventories with NO absolute
// floor. A newly resolved nonzero term against zero has relative error1.
// Local tolerance does not itself certify global time convergence.
inline AdaptiveResult adaptiveStep(const System&system,double time,const EventControl&control,
 double tolerance=1e-4,unsigned maxTrials=256,unsigned maxDepth=12,std::ostream*trace=nullptr,bool horizonNorm=false,const EnergyEvaluator&valueEnergy={},bool reuseCoarse=false){
 if(!(tolerance>0&&tolerance<1)||!std::isfinite(tolerance)||maxTrials==0||maxDepth>20)throw std::invalid_argument("adaptive coupled error/budget");
 AdaptiveResult out;
 auto run=[&](const State&s,double t,double h){++out.subintegrations;CoupledPlaneStep m(system.film.model,system.film.mass,h,system.film.damping,control.sample(t).tension,s.q,s.v,std::vector<Point>(s.q.size()),0);return System(m,system.triangles,s.body,system.radius,system.strictNewton,system.reuseAccepted).advance(t,control);};
 auto energies=[&](const State&s){std::array<double,5>e{};if(valueEnergy){auto stored=valueEnergy(system.film.model,s.q);e[0]=stored[0];e[1]=stored[1];}else system.film.model.elements(s.q,0,[&](const Element&el){if(el.kind==0)e[0]+=el.energy.v;if(el.kind==1)e[1]+=el.energy.v;});for(unsigned i=0;i<s.v.size();++i)e[2]+=.5*system.film.mass[i]*dot(s.v[i],s.v[i]);e[3]=.5*s.body.mass*s.body.linear.squaredNorm();e[4]=.5*s.body.inertia*s.body.angular.squaredNorm();return e;};
 auto relative=[](double a,double b){double scale=std::max(std::abs(a),std::abs(b));return scale==0?0.:std::abs(a-b)/scale;};
 auto vectorError=[&](const Eigen::VectorXd&a,const Eigen::VectorXd&b){double scale=std::max(a.norm(),b.norm());return scale==0?0.:(a-b).norm()/scale;};
 auto strip=[](Result&r){for(auto*rows:{&r.contactRows,&r.projectionRows})for(auto&row:*rows)row.hessian.resize(0,0);};
 std::optional<std::array<Result,3>>root;std::array<double,5>energyScale{};double velocityScale=0,centerScale=0,pScale=0,lossScale=0,projectionScale=0;
 auto atomImpulse=[](const Result&r){return r.impact?r.impact->state.impulse.sum():0.;};auto atomLoss=[](const Result&r){return r.impact?r.impact->state.energyLoss:0.;};
 if(horizonNorm){Result coarse=run(system.before,time,system.film.h),left=run(system.before,time,system.film.h/2),right=run(left.state,time+system.film.h/2,system.film.h/2);for(const auto*s:std::array<const State*,4>{&system.before,&coarse.state,&left.state,&right.state}){auto e=energies(*s);for(unsigned i=0;i<e.size();++i)energyScale[i]=std::max(energyScale[i],std::abs(e[i]));velocityScale=std::max(velocityScale,system.pack(*s).norm());centerScale=std::max(centerScale,(s->body.center-system.before.body.center).norm());}pScale=std::max(std::abs(atomImpulse(coarse)),std::abs(atomImpulse(left)+atomImpulse(right)));lossScale=std::max(std::abs(atomLoss(coarse)),std::abs(atomLoss(left)+atomLoss(right)));projectionScale=std::max(std::abs(coarse.projectionLoss),std::abs(left.projectionLoss+right.projectionLoss));root=std::array<Result,3>{std::move(coarse),std::move(left),std::move(right)};}
 auto normalized=[](double difference,double scale){return scale>0?std::abs(difference)/scale:difference==0?0.:std::numeric_limits<double>::infinity();};
 std::function<State(const State&,double,double,unsigned,std::optional<Result>)>advance;
 advance=[&](const State&s,double t,double h,unsigned depth,std::optional<Result>known)->State{
  if(++out.trials>maxTrials)throw std::runtime_error("adaptive coupled trial budget;NOT OS exhaustion");
  // Invalid geometry/Newton failures are NOT swallowed as error estimates.
  Result coarse,left,right;if(depth==0&&root){coarse=std::move((*root)[0]);left=std::move((*root)[1]);right=std::move((*root)[2]);root.reset();}else{if(known){coarse=std::move(*known);++out.coarseReuses;}else coarse=run(s,t,h);left=run(s,t,h/2);right=run(left.state,t+h/2,h/2);}auto a=energies(coarse.state),b=energies(right.state);double error=0;for(unsigned i=0;i<a.size();++i)error=std::max(error,relative(a[i],b[i]));
  error=std::max(error,vectorError(system.pack(coarse.state),system.pack(right.state)));error=std::max(error,vectorError(coarse.state.body.center-s.body.center,right.state.body.center-s.body.center));
  auto impulse=[](const Result&r){return r.impact?r.impact->state.impulse.sum():0.;};auto loss=[](const Result&r){return r.impact?r.impact->state.energyLoss:0.;};
  error=std::max(error,relative(impulse(coarse),impulse(left)+impulse(right)));error=std::max(error,relative(loss(coarse),loss(left)+loss(right)));error=std::max(error,relative(coarse.projectionLoss,left.projectionLoss+right.projectionLoss));
  out.maximumInstantaneousRelativeError=std::max(out.maximumInstantaneousRelativeError,error);
  if(horizonNorm){error=0;for(unsigned i=0;i<a.size();++i)error=std::max(error,normalized(a[i]-b[i],energyScale[i]));error=std::max(error,normalized((system.pack(coarse.state)-system.pack(right.state)).norm(),velocityScale));error=std::max(error,normalized((coarse.state.body.center-right.state.body.center).norm(),centerScale));error=std::max(error,normalized(impulse(coarse)-impulse(left)-impulse(right),pScale));error=std::max(error,normalized(loss(coarse)-loss(left)-loss(right),lossScale));error=std::max(error,normalized(coarse.projectionLoss-left.projectionLoss-right.projectionLoss,projectionScale));error*=system.film.h/h;}
  unsigned coarseEvents=bool(coarse.event),fineEvents=unsigned(bool(left.event))+unsigned(bool(right.event));if(coarseEvents!=fineEvents)error=std::numeric_limits<double>::infinity();
  if(trace){*trace<<std::setprecision(17)<<"trial "<<out.trials<<" time "<<t<<" h "<<h<<" depth "<<depth<<" error "<<error<<" event_counts "<<coarseEvents<<' '<<fineEvents<<" energies";for(unsigned i=0;i<a.size();++i)*trace<<' '<<a[i]<<' '<<b[i]<<' '<<relative(a[i],b[i]);*trace<<" projection "<<coarse.projectionLoss<<' '<<left.projectionLoss+right.projectionLoss<<" impulses "<<impulse(coarse)<<' '<<impulse(left)+impulse(right)<<'\n';}
  if(error<=tolerance){out.maximumAcceptedError=std::max(out.maximumAcceptedError,error);strip(left);strip(right);State accepted=right.state;out.segments.push_back({t,h/2,error,s,std::move(left)});State middle=out.segments.back().result.state;out.segments.push_back({t+h/2,h/2,error,std::move(middle),std::move(right)});return accepted;}
  ++out.rejected;if(depth>=maxDepth)throw std::runtime_error("adaptive coupled depth budget;unresolved relative energy/impulse error NOT ignored");auto middle=advance(s,t,h/2,depth+1,reuseCoarse?std::optional<Result>(std::move(left)):std::nullopt);return advance(middle,t+h/2,h/2,depth+1,std::nullopt);
 };
 advance(system.before,time,system.film.h,0,std::nullopt);return out;
}
}
