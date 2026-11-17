#pragma once
#include "ProjectedImpact.h"
#include <sstream>
#include <iomanip>
namespace regrip_film_impact {
struct ManyRowImpact {ImpactResult state;unsigned sweeps;int rank;double velocityResidual;
 double subtractedKineticLoss=0,momentumEnergyDefect=0,subtractionResidual=0;
};
// Plastic normal-impact dual QP. No contact compliance/regularization and no
// exponential active-subset enumeration. Bounded solver,not global qualification.
inline ManyRowImpact manyRowImpact(const Eigen::MatrixXd&M,const Eigen::MatrixXd&J,
 const Eigen::VectorXd&before,double velocityTolerance,unsigned maxSweeps=4096){
 if(M.rows()!=before.size()||M.cols()!=before.size()||J.cols()!=before.size()||J.rows()==0||J.rows()>1024||
  !M.allFinite()||!J.allFinite()||!before.allFinite()||!std::isfinite(velocityTolerance)||velocityTolerance<=0||maxSweeps==0||
  !(M.array()==M.transpose().array()).all())throw std::invalid_argument("many-row impact input");
 Eigen::LLT<Eigen::MatrixXd> factor(M);if(factor.info()!=Eigen::Success)throw std::domain_error("many-row impact mass not SPD");
 Eigen::MatrixXd inverseJ=factor.solve(J.transpose()),W=J*inverseJ;
 if(!inverseJ.allFinite()||!W.allFinite())throw std::domain_error("nonfinite impact effective mass;no accepted state");
 Eigen::VectorXd incoming=J*before,p=Eigen::VectorXd::Zero(J.rows());
 for(unsigned sweep=0;sweep<maxSweeps;++sweep){
  for(int i=0;i<J.rows();++i){if(W(i,i)<=0){if(J.row(i).norm()!=0)throw std::domain_error("invalid impact effective mass");continue;}
   double vn=incoming(i)+W.row(i).dot(p);p(i)=std::max(0.,p(i)-vn/W(i,i));
  }
  Eigen::VectorXd after=before+inverseJ*p,vn=J*after;double residual=0;
  if(!after.allFinite()||!p.allFinite()||!vn.allFinite())throw std::domain_error("nonfinite impact state;no accepted velocity");
  for(int i=0;i<J.rows();++i)residual=std::max(residual,p(i)>0?std::abs(vn(i)):std::max(0.,-vn(i)));
  if(residual<=velocityTolerance){ImpactResult result{after,p,vn};result.momentumResidual=(M*(after-before)-J.transpose()*p).norm();
   // Stable impulse work, not subtraction of two large kinetic energies.
   // Exact identity: K- - K+ = -.5*p.J(v-+v+) -.5*(v-+v+).r,
   // r=M(v+-v-)-J^T*p. The second term is a recorded numerical momentum
   // defect, NOT friction heat or an invented physical dissipation.
   double rawLoss=.5*(before.dot(M*before)-after.dot(M*after));
   result.energyLoss=-.5*p.dot(incoming+vn);
   Eigen::VectorXd momentum=M*(after-before)-J.transpose()*p;
   double momentumWork=-.5*(before+after).dot(momentum);
   if(!std::isfinite(rawLoss)||!std::isfinite(result.energyLoss)||!std::isfinite(momentumWork))throw std::domain_error("nonfinite impact energy inventory");
   if(result.energyLoss < -velocityTolerance*p.norm()){
    std::ostringstream error;error<<std::setprecision(17)<<"many-row impulse work creates energy beyond unchanged residual inventory:raw_loss="<<rawLoss<<" impulse_work="<<result.energyLoss<<" momentum_work="<<momentumWork<<" tolerance_inventory="<<velocityTolerance*p.norm();throw std::runtime_error(error.str());
   }
   int rank=-1;if(J.rows()<=256){Eigen::FullPivLU<Eigen::MatrixXd> rankSolver(J);rank=rankSolver.rank();}
   return {result,sweep+1,rank,residual,rawLoss,momentumWork,rawLoss-result.energyLoss-momentumWork};
  }
 }
 throw std::runtime_error("many-row impact complementarity budget;no unverified accepted velocity");
}
}
