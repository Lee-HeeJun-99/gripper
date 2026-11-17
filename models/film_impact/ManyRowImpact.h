#pragma once
#include "ProjectedImpact.h"
namespace regrip_film_impact {
struct ManyRowImpact {ImpactResult state;unsigned sweeps;int rank;double velocityResidual;};
// Plastic normal-impact dual QP. No contact compliance/regularization and no
// exponential active-subset enumeration. Bounded solver,not global qualification.
inline ManyRowImpact manyRowImpact(const Eigen::MatrixXd&M,const Eigen::MatrixXd&J,
 const Eigen::VectorXd&before,double velocityTolerance,unsigned maxSweeps=4096){
 if(M.rows()!=before.size()||M.cols()!=before.size()||J.cols()!=before.size()||J.rows()==0||J.rows()>1024||
  !M.allFinite()||!J.allFinite()||!before.allFinite()||!std::isfinite(velocityTolerance)||velocityTolerance<=0||maxSweeps==0||
  !(M.array()==M.transpose().array()).all())throw std::invalid_argument("many-row impact input");
 Eigen::LLT<Eigen::MatrixXd> factor(M);if(factor.info()!=Eigen::Success)throw std::domain_error("many-row impact mass not SPD");
 Eigen::MatrixXd inverseJ=factor.solve(J.transpose()),W=J*inverseJ;
 Eigen::VectorXd incoming=J*before,p=Eigen::VectorXd::Zero(J.rows());
 for(unsigned sweep=0;sweep<maxSweeps;++sweep){
  for(int i=0;i<J.rows();++i){if(W(i,i)<=0){if(J.row(i).norm()!=0)throw std::domain_error("invalid impact effective mass");continue;}
   double vn=incoming(i)+W.row(i).dot(p);p(i)=std::max(0.,p(i)-vn/W(i,i));
  }
  Eigen::VectorXd after=before+inverseJ*p,vn=J*after;double residual=0;
  for(int i=0;i<J.rows();++i)residual=std::max(residual,p(i)>0?std::abs(vn(i)):std::max(0.,-vn(i)));
  if(residual<=velocityTolerance){ImpactResult result{after,p,vn};result.momentumResidual=(M*(after-before)-J.transpose()*p).norm();
   result.energyLoss=.5*(before.dot(M*before)-after.dot(M*after));
   if(result.energyLoss < -velocityTolerance*p.norm())throw std::runtime_error("many-row impact energy creation exceeds residual inventory");
   int rank=-1;if(J.rows()<=256){Eigen::FullPivLU<Eigen::MatrixXd> rankSolver(J);rank=rankSolver.rank();}
   return {result,sweep+1,rank,residual};
  }
 }
 throw std::runtime_error("many-row impact complementarity budget;no unverified accepted velocity");
}
}
