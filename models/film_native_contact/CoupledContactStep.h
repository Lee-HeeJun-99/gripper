#pragma once
#include "CoupledPlaneStep.h"
namespace regrip_film_native {
// Nonnegative multipliers on a finite set of frozen, scalar unilateral rows.
// A direct nonnegative active set does not regularize duplicate contact rows.
struct CoupledContactStep {
 struct Plane{std::vector<Point>J;double target,lambda;unsigned row;};
 CoupledPlaneStep mechanics;std::vector<Plane>planes;Eigen::MatrixXd C;Eigen::VectorXd offset;
 CoupledContactStep(Assembly model,std::vector<double>mass,double h,double damping,double T,
  std::vector<Point>q0,std::vector<Point>v0,std::vector<Plane>p):mechanics(model,mass,h,damping,T,q0,v0,std::vector<Point>(model.size()),0),planes(std::move(p)){
  if(planes.size()>256)throw std::invalid_argument("algorithmic contact row budget0..256,not OS exhaustion");C=Eigen::MatrixXd::Zero(mechanics.freeSize,planes.size());offset=Eigen::VectorXd::Zero(planes.size());auto rest=model.rest();
  for(unsigned k=0;k<planes.size();++k){if(planes[k].J.size()!=model.size())throw std::invalid_argument("contact row size");offset(k)=-planes[k].target;for(unsigned a=0;a<3*model.size();++a){offset(k)+=planes[k].J[a/3][a%3]*(rest[a/3][a%3]+q0[a/3][a%3]);if(mechanics.index[a]>=0)C(mechanics.index[a],k)+=mechanics.weight[a]*planes[k].J[a/3][a%3];}}
 }
 static double gapError(const Eigen::VectorXd&w,const Eigen::VectorXd&lambda){double error=0;for(int k=0;k<w.size();++k)error=std::max(error,lambda(k)>0?std::abs(w(k)):std::max(-w(k),0.));return error;}
 static Eigen::VectorXd dual(const Eigen::MatrixXd&W,const Eigen::VectorXd&d,Eigen::VectorXd lambda){
  const int n=lambda.size();std::vector<bool>passive(n,false);for(int i=0;i<n;++i){if(lambda(i)<0)throw std::invalid_argument("negative initial unilateral multiplier");passive[i]=lambda(i)>0;}
  for(unsigned iteration=0;iteration<1000;++iteration){if(gapError(d+W*lambda,lambda)<=1e-10)return lambda;std::vector<int>P;for(int i=0;i<n;++i)if(passive[i])P.push_back(i);
   if(P.empty()){Eigen::VectorXd gradient=d+W*lambda;Eigen::Index entering;gradient.minCoeff(&entering);if(!(W(entering,entering)>0))throw std::runtime_error("zero contact compliance at violated row");passive[entering]=true;continue;}
   Eigen::MatrixXd sub(P.size(),P.size());Eigen::VectorXd rhs(P.size());for(unsigned i=0;i<P.size();++i){rhs(i)=-d(P[i]);for(unsigned j=0;j<P.size();++j)sub(i,j)=W(P[i],P[j]);}Eigen::VectorXd z=Eigen::VectorXd::Zero(n),solution=sub.completeOrthogonalDecomposition().solve(rhs);for(unsigned i=0;i<P.size();++i)z(P[i])=solution(i);
   bool negative=false;double alpha=1;int blocking=-1;for(int i:P)if(z(i)<0){negative=true;double fraction=lambda(i)/(lambda(i)-z(i));if(fraction<=alpha){alpha=fraction;blocking=i;}}
   if(negative){lambda+=alpha*(z-lambda);for(int i=0;i<n;++i)if(lambda(i)<0)lambda(i)=0;if(blocking<0)throw std::runtime_error("unilateral blocking row missing");lambda(blocking)=0;passive[blocking]=false;continue;}
   lambda=z;Eigen::VectorXd gradient=d+W*lambda;int drop=-1;double worst=1e-10;for(int i:P)if(gradient(i)>worst){worst=gradient(i);drop=i;}if(drop>=0){passive[drop]=false;lambda(drop)=0;continue;}
   int entering=-1;double minimum=-1e-10;for(int i=0;i<n;++i)if(!passive[i]&&gradient(i)<minimum){minimum=gradient(i);entering=i;}if(entering>=0){passive[entering]=true;continue;}if(gapError(gradient,lambda)<=1e-10)return lambda;throw std::runtime_error("rank-deficient active constraints: no certified solution;no regularization");
  }throw std::runtime_error("unilateral active-set iteration budget,not memory exhaustion");
 }
 double merit(const Eigen::VectorXd&gradient,const Eigen::VectorXd&gap,const Eigen::VectorXd&lambda,const Eigen::VectorXd&diagonal)const{double squared=(gradient-C*lambda).squaredNorm();for(int k=0;k<gap.size();++k){if(!(diagonal(k)>0)){if(gap(k)<-1e-10)throw std::runtime_error("fixed infeasible contact row");continue;}double complementarity=std::min(lambda(k),gap(k)/diagonal(k));squared+=complementarity*complementarity;}return std::sqrt(squared);}
 struct Result{std::vector<Point>velocity,displacement;Eigen::VectorXd lambda;double residual,gap;unsigned iterations;};
 Result solve(const std::vector<Point>&initial,std::ostream*trace=nullptr)const{auto y=mechanics.pack(initial);Eigen::VectorXd lambda(planes.size());for(unsigned k=0;k<planes.size();++k)lambda(k)=planes[k].lambda;double firstResidual=-1;
  for(unsigned iteration=0;iteration<30;++iteration){auto e=mechanics.evaluate(y);Eigen::VectorXd gap=offset+mechanics.h*C.transpose()*y;double residual=(e.gradient-C*lambda).norm();if(firstResidual<0)firstResidual=residual;double primal=gapError(gap,lambda);if(trace)*trace<<"general_iteration "<<iteration<<" residual "<<residual<<" gap "<<primal<<'\n';
   if(residual<=std::max(1e-15,firstResidual*1e-7)&&primal<=1e-10){Result result;result.velocity=mechanics.expand(y);result.displacement=mechanics.previous;for(unsigned i=0;i<result.velocity.size();++i)for(unsigned d=0;d<3;++d)result.displacement[i][d]+=mechanics.h*result.velocity[i][d];result.lambda=lambda;result.residual=residual;result.gap=primal;result.iterations=iteration;return result;}
   Eigen::LDLT<Eigen::MatrixXd>ldlt(e.tangent);if(ldlt.info()!=Eigen::Success||ldlt.vectorD().minCoeff()<=0)throw std::runtime_error("nonpositive mechanical Hessian;no regularization");Eigen::VectorXd inverseG=ldlt.solve(e.gradient);Eigen::MatrixXd inverseC=ldlt.solve(C),W=mechanics.h*C.transpose()*inverseC;Eigen::VectorXd d=gap-mechanics.h*C.transpose()*inverseG;auto next=dual(W,d,lambda);Eigen::VectorXd increment=-inverseG+inverseC*next;double currentMerit=merit(e.gradient,gap,lambda,W.diagonal());bool accepted=false;double alpha=1;
   for(unsigned trial=0;trial<16;++trial){auto candidate=mechanics.evaluate(y+alpha*increment);Eigen::VectorXd candidateLambda=lambda+alpha*(next-lambda),candidateGap=offset+mechanics.h*C.transpose()*(y+alpha*increment);double value=merit(candidate.gradient,candidateGap,candidateLambda,W.diagonal());if(value<=(1-1e-4*alpha)*currentMerit){y+=alpha*increment;lambda=candidateLambda;accepted=true;break;}alpha*=.5;}if(!accepted)throw std::runtime_error("coupled unilateral residual line search failed");
  }throw std::runtime_error("coupled unilateral Newton budget");
 }
};
}
