#pragma once
#include "FilmEventImpulse.h"
#include "../film_native_contact/CoupledContactStep.h"
namespace regrip_film_impact {
struct BracketedFilmBirth {
 using Point=regrip_film_rail::Point;
 double time=0,gap=0,gapRate=0;
 unsigned evaluations=0;
 std::vector<Point>position,velocity;
 Eigen::RowVectorXd timeIncomingDerivative;
 Eigen::MatrixXd positionIncomingDerivative,velocityIncomingDerivative;
};
// Resolve ONE externally isolated entering bracket on the *numerically defined*
// implicit-Euler subintegration q(t)=q0+t B v(t), G(v,t)=0. Constant tension.
// This is not interpolating stored frames, nor a claim of global earliest CCD.
// A missing bracket, initial contact or grazing explicitly rejects.
inline BracketedFilmBirth resolveFilmBirthBracket(
 const regrip_film_native::CoupledPlaneStep&original,
 const std::vector<unsigned>&support,regrip_film_rail::Point center,double radius,
 double gapTolerance=1e-10,double timeTolerance=1e-12){
 using namespace regrip_film_native;using regrip_film_sphere::ClosestPrimitive;
 if(!std::isfinite(gapTolerance)||gapTolerance<=0||!std::isfinite(timeTolerance)||timeTolerance<=0)
  throw std::invalid_argument("film event root tolerances");
 const auto rest=original.model.rest();
 auto geometry=[&](const std::vector<Point>&q){std::vector<Point>p;for(auto i:support)p.push_back(add(rest.at(i),q.at(i)));return ClosestPrimitive::evaluate(p,center,radius);};
 if(!(geometry(original.previous).gap.v>0))throw std::domain_error("birth bracket must start strictly separated");
 struct Sample{CoupledContactStep::Result state;double gap;};unsigned evaluations=0;
 auto sample=[&](double t){
  CoupledContactStep free(original.model,original.mass,t,original.damping,original.T,original.previous,original.previousVelocity,{},true,true);
  auto state=free.solve(original.previousVelocity);++evaluations;double gap=geometry(state.displacement).gap.v;
  return Sample{std::move(state),gap};
 };
 double lo=0,hi=original.h;auto right=sample(hi);
 if(!(right.gap<0))throw std::domain_error("no strict entering bracket;transient/simultaneous/global event search remains caller responsibility");
 for(unsigned i=0;i<80;++i){
  if(hi-lo<=timeTolerance&&std::abs(right.gap)<=gapTolerance)break;
  double mid=(lo+hi)/2;if(mid==lo||mid==hi)throw std::runtime_error("event root unresolved at roundoff");
  auto point=sample(mid);if(point.gap>0)lo=mid;else{hi=mid;right=std::move(point);}
 }
 if(hi-lo>timeTolerance||std::abs(right.gap)>gapTolerance)throw std::runtime_error("film event root budget80");
 CoupledPlaneStep at(original.model,original.mass,hi,original.damping,original.T,original.previous,original.previousVelocity,std::vector<Point>(rest.size()),0);
 auto y=at.pack(right.state.velocity);auto evaluation=at.evaluate(y);auto M=filmMass(at);
 Eigen::VectorXd force=Eigen::VectorXd::Zero(at.freeSize);Eigen::MatrixXd K=Eigen::MatrixXd::Zero(at.freeSize,at.freeSize);
 at.model.elements(right.state.displacement,at.T,[&](const Element&el){
  for(unsigned a=0;a<3*el.ids.size();++a){unsigned ia=3*el.ids[a/3]+a%3;int i=at.index[ia];if(i<0)continue;
   force(i)+=at.weight[ia]*el.energy.g[a];
   for(unsigned b=0;b<3*el.ids.size();++b){unsigned ib=3*el.ids[b/3]+b%3;int j=at.index[ib];if(j>=0)K(i,j)+=at.weight[ia]*at.weight[ib]*el.energy.h[N*a+b];}
  }
 });
 Eigen::LDLT<Eigen::MatrixXd> factor(evaluation.tangent);
 if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("event mechanical tangent not SPD");
 Eigen::VectorXd dvdt=factor.solve(-at.damping*M*y-force-hi*K*y);
 auto g=geometry(right.state.displacement);std::vector<Point>nodal(rest.size());
 for(unsigned a=0;a<3*support.size();++a)nodal[support[a/3]][a%3]+=g.gap.g[a];
 Eigen::RowVectorXd C=filmRow(at,nodal);double rate=(C*(y+hi*dvdt))(0);
 if(!std::isfinite(rate)||rate>=0)throw std::domain_error("nontransversal/incorrect entering branch;no denominator regularization");
 BracketedFilmBirth result;result.time=hi;result.gap=right.gap;result.gapRate=rate;result.evaluations=evaluations;
 result.position=std::move(right.state.displacement);result.velocity=std::move(right.state.velocity);
 Eigen::MatrixXd base=factor.solve(M);
 result.timeIncomingDerivative=-(hi*C*base)/rate;
 result.positionIncomingDerivative=hi*base+(y+hi*dvdt)*result.timeIncomingDerivative;
 result.velocityIncomingDerivative=base+dvdt*result.timeIncomingDerivative;return result;
}
}
