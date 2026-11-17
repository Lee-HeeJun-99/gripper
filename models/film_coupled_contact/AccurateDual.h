#pragma once
#include "../film_native_contact/CoupledContactStep.h"
namespace regrip_coupled {
// Independent tighter numerical LCP solve,not a relaxed physical clearance.
// Original Native solver/default1e-10 stays untouched. No compliance or rank
// regularization. W may be nonsymmetric in midpoint-force/endpoint-gap tests.
inline Eigen::VectorXd accurateDual(const Eigen::MatrixXd&W,const Eigen::VectorXd&d,Eigen::VectorXd lambda,double tolerance){
 if(!(tolerance>0&&tolerance<=1e-10)||!std::isfinite(tolerance))throw std::invalid_argument("contact solve may only tighten original1e-10");
 const int n=lambda.size();if(W.rows()!=n||W.cols()!=n||d.size()!=n||!W.allFinite()||!d.allFinite()||!lambda.allFinite())throw std::invalid_argument("accurate dual dimensions/finite");
 std::vector<bool>passive(n,false);for(int i=0;i<n;++i){if(lambda(i)<0)throw std::invalid_argument("negative initial multiplier");passive[i]=lambda(i)>0;}
 using regrip_film_native::CoupledContactStep;
 for(unsigned iteration=0;iteration<1000;++iteration){
  if(CoupledContactStep::gapError(d+W*lambda,lambda)<=tolerance)return lambda;
  std::vector<int>P;for(int i=0;i<n;++i)if(passive[i])P.push_back(i);
  if(P.empty()){Eigen::VectorXd gradient=d+W*lambda;Eigen::Index entering;gradient.minCoeff(&entering);if(!(W(entering,entering)>0))throw std::runtime_error("zero accurate contact compliance");passive[entering]=true;continue;}
  Eigen::MatrixXd sub(P.size(),P.size());Eigen::VectorXd rhs(P.size());for(unsigned i=0;i<P.size();++i){rhs(i)=-d(P[i]);for(unsigned j=0;j<P.size();++j)sub(i,j)=W(P[i],P[j]);}
  Eigen::VectorXd z=Eigen::VectorXd::Zero(n),solution=sub.completeOrthogonalDecomposition().solve(rhs);for(unsigned i=0;i<P.size();++i)z(P[i])=solution(i);
  bool negative=false;double alpha=1;int blocking=-1;for(int i:P)if(z(i)<0){negative=true;double fraction=lambda(i)/(lambda(i)-z(i));if(fraction<=alpha){alpha=fraction;blocking=i;}}
  if(negative){lambda+=alpha*(z-lambda);for(int i=0;i<n;++i)if(lambda(i)<0)lambda(i)=0;if(blocking<0)throw std::runtime_error("missing accurate blocking row");lambda(blocking)=0;passive[blocking]=false;continue;}
  lambda=z;Eigen::VectorXd gradient=d+W*lambda;int drop=-1;double worst=tolerance;for(int i:P)if(gradient(i)>worst){worst=gradient(i);drop=i;}if(drop>=0){passive[drop]=false;lambda(drop)=0;continue;}
  int entering=-1;double minimum=-tolerance;for(int i=0;i<n;++i)if(!passive[i]&&gradient(i)<minimum){minimum=gradient(i);entering=i;}if(entering>=0){passive[entering]=true;continue;}
  if(CoupledContactStep::gapError(gradient,lambda)<=tolerance)return lambda;
  throw std::runtime_error("accurate rank-deficient constraints;no certified solution/regularization");
 }throw std::runtime_error("accurate dual iteration budget1000");
}
}
