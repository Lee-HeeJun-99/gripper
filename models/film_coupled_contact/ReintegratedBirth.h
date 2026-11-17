#pragma once
#include "CoupledSphere.h"
namespace regrip_coupled {
struct ReintegratedBirth {
 double time=0,gap=0,familyRate=0,mechanicalResidual=0;
 unsigned evaluations=0,mechanicalEvaluations=0,acceptedReuses=0;
 State state;
 std::vector<Row>rows;
 Eigen::MatrixXd J,positionIncoming,velocityIncoming;
 Eigen::VectorXd familyRates;
 Eigen::RowVectorXd timeIncoming;
 std::optional<double>absoluteStartSensitivity;
};
// ONE externally isolated strict entering bracket on the coupled implicit
// midpoint ENDPOINT FAMILY. Every trial solves both q AND v with the same C2.
// This is not a claim of globally earliest CCD for that nonlinear family.
// Dense-path CCD and endpoint-family roots define different numerical paths.
inline ReintegratedBirth resolveCoupledBirthBracket(const System&original,double start,
 const EventControl&control,double gapTolerance=1e-12,double timeTolerance=1e-13){
 if(!(gapTolerance>0&&gapTolerance<=1e-10&&timeTolerance>0)||!std::isfinite(gapTolerance+timeTolerance))throw std::invalid_argument("tight finite coupled event tolerances");
 double leftGap=original.clearance(original.before);
 if(!(leftGap>0))throw std::domain_error("reintegrated birth requires strict initial separation");
 unsigned evaluations=0,mechanicalEvaluations=0,reuses=0;
 auto make=[&](double h){CoupledPlaneStep m(original.film.model,original.film.mass,h,original.film.damping,control.sample(start).tension,original.before.q,original.before.v,std::vector<Point>(original.before.q.size()),0);return System(m,original.triangles,original.before.body,original.radius,original.strictNewton,original.reuseAccepted,original.midpointContact,original.absoluteNewtonResidual,original.contactSolveGap);};
 auto sample=[&](double h){++evaluations;auto result=make(h).smooth(start,control,false);mechanicalEvaluations+=result.evaluations;reuses+=result.acceptedReuses;return result;};
 double lo=0,hi=original.film.h;auto right=sample(hi);
 if(!(right.minimumGap<0))throw std::domain_error("no strict endpoint-family entering bracket;transient/global CCD remains caller responsibility");
 for(unsigned i=0;i<80;++i){
  if(hi-lo<=timeTolerance&&std::abs(right.minimumGap)<=gapTolerance)break;
  double middle=(lo+hi)/2;
  if(middle==lo||middle==hi)throw std::runtime_error("coupled family root at roundoff;no epsilon");
  auto trial=sample(middle);
  if(trial.minimumGap>0){lo=middle;leftGap=trial.minimumGap;}
  else{hi=middle;right=std::move(trial);}
 }
 if(hi-lo>timeTolerance||std::abs(right.minimumGap)>gapTolerance||!(leftGap>0))throw std::runtime_error("coupled family root budget80");
 auto at=make(hi);Eigen::VectorXd v0=at.pack(at.before),middle=(v0+at.pack(right.state))/2;
 auto controlAt=control.sample(start+hi/2);auto e=at.evaluate(middle,controlAt.tension);
 Eigen::LDLT<Eigen::MatrixXd>factor(e.tangent);
 if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("coupled family tangent not SPD");
 Eigen::VectorXd forceT=Eigen::VectorXd::Zero(at.n);auto qmid=at.before.q;auto vm=at.film.expand(middle.head(at.nf));
 for(unsigned i=0;i<qmid.size();++i)for(unsigned d=0;d<3;++d)qmid[i][d]+=hi/2*vm[i][d];
 at.film.model.elements(qmid,1,[&](const Element&el){if(el.kind!=2)return;for(unsigned j=0;j<3*el.ids.size();++j){unsigned a=3*el.ids[j/3]+j%3;int k=at.film.index[a];if(k>=0)forceT(k)+=at.film.weight[a]*el.energy.g[j];}});
 // Partial dG/dh at fixed midpoint velocity,including C2 T'(start+h/2).
 Eigen::VectorXd Gh=(e.gradient-at.M*(middle-v0))/hi+(e.tangent-at.M-hi/2*at.film.damping*at.M)*middle/hi+hi/4*controlAt.rate*forceT;
 Eigen::VectorXd velocityRate=factor.solve(-Gh),positionRate=middle+hi*velocityRate;
 ReintegratedBirth result;result.time=hi;result.gap=right.minimumGap;result.mechanicalResidual=2*e.gradient.norm();result.evaluations=evaluations;result.mechanicalEvaluations=mechanicalEvaluations+1;result.acceptedReuses=reuses;result.state=std::move(right.state);
 for(unsigned id=0;id<at.triangles.size();++id){auto row=at.geometry(result.state,id);double rate=row.gradient.dot(positionRate);if(std::abs(row.gap)>gapTolerance||rate>=0)continue;if(row.gap>0&&row.gap/(-rate)>timeTolerance)continue;result.rows.push_back(std::move(row));}
 if(result.rows.empty())throw std::runtime_error("coupled family root has no entering owner row");
 result.J.resize(result.rows.size(),at.n);for(unsigned k=0;k<result.rows.size();++k)result.J.row(k)=result.rows[k].gradient;
 result.familyRates=result.J*positionRate;result.familyRate=result.familyRates(0);
 if(!(result.familyRate<0)||!std::isfinite(result.familyRate))throw std::domain_error("nontransversal coupled endpoint family;no denominator regularization");
 bool unique=true;for(int k=1;k<result.J.rows();++k)if((result.J.row(k).array()!=result.J.row(0).array()).any())unique=false;
 if(unique){
  Eigen::MatrixXd base=factor.solve(at.M),Q=hi*base;
  result.timeIncoming=-(result.J.row(0)*Q)/result.familyRate;
  result.positionIncoming=Q+positionRate*result.timeIncoming;
  result.velocityIncoming=2*base-Eigen::MatrixXd::Identity(at.n,at.n)+2*velocityRate*result.timeIncoming;
  Eigen::VectorXd startRate=factor.solve(-hi/2*controlAt.rate*forceT);
  result.absoluteStartSensitivity=1-hi*result.J.row(0).dot(startRate)/result.familyRate;
 }
 return result;
}
}
