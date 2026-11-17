#pragma once
#include <Eigen/Dense>
#include <cmath>
#include <stdexcept>
#include <vector>

namespace regrip_film_impact {
// Independent instantaneous frictionless Newton impact assumption. Coordinates
// are reduced velocities y, physical velocity B*y; J acts on y, not positions.
// Tolerances have separate units: velocity mm/s and impulse F*s.
struct ImpactResult {
 Eigen::VectorXd velocity, impulse, normalVelocity;
 double momentumResidual=0, energyLoss=0;
};
inline Eigen::MatrixXd projectedMass(const Eigen::MatrixXd&B,const Eigen::VectorXd&mass) {
 if(B.rows()!=mass.size()||B.cols()==0||!B.allFinite()||!mass.allFinite()||
    (mass.array()<=0).any()) throw std::invalid_argument("invalid physical mass/projection");
 return B.transpose()*mass.asDiagonal()*B;
}
inline ImpactResult solve(const Eigen::MatrixXd&M,const Eigen::MatrixXd&J,
 const Eigen::VectorXd&before,double restitution,double velocityTolerance,double impulseTolerance) {
 const auto n=before.size(), k=J.rows();
 if(n==0||M.rows()!=n||M.cols()!=n||J.cols()!=n||k>16||
    !M.allFinite()||!J.allFinite()||!before.allFinite()||
    !std::isfinite(restitution)||restitution<0||restitution>1||
    !std::isfinite(velocityTolerance)||velocityTolerance<0||
    !std::isfinite(impulseTolerance)||impulseTolerance<0||
    !(M.array()==M.transpose().array()).all())
  throw std::invalid_argument("impact dimensions/symmetry/parameters");
 Eigen::LLT<Eigen::MatrixXd> factor(M);
 if(factor.info()!=Eigen::Success) throw std::runtime_error("impact mass not positive definite");
 const Eigen::MatrixXd inverseJ=factor.solve(J.transpose());
 const Eigen::MatrixXd W=J*inverseJ;
 const Eigen::VectorXd incoming=J*before;
 // Restitution target applies only to closing rows. Separating rows require
 // nonpenetrating velocity, never an artificial attractive impulse.
 Eigen::VectorXd target=(-restitution*incoming.array().min(0.)).matrix();
 // Exhaustive independent reference, NOT a production many-contact solver.
 // Dependent active subsets are skipped, not regularized. Redundant rows can
 // have nonunique impulses; first feasible sparse subset is deterministic.
 for(unsigned mask=0;mask<(1u<<k);++mask) {
  std::vector<unsigned> active;for(unsigned i=0;i<k;++i)if(mask&(1u<<i))active.push_back(i);
  Eigen::VectorXd p=Eigen::VectorXd::Zero(k);
  if(!active.empty()) {
   Eigen::MatrixXd A(active.size(),active.size());Eigen::VectorXd b(active.size());
   for(unsigned i=0;i<active.size();++i){b(i)=target(active[i])-incoming(active[i]);
    for(unsigned j=0;j<active.size();++j)A(i,j)=W(active[i],active[j]);}
   Eigen::FullPivLU<Eigen::MatrixXd> lu(A);if(lu.rank()!=A.rows())continue;
   Eigen::VectorXd pa=lu.solve(b);for(unsigned i=0;i<active.size();++i)p(active[i])=pa(i);
  }
  // Do not clip a negative impulse to zero: a different active subset must solve it.
  if((p.array()<0).any())continue;
  Eigen::VectorXd after=before+inverseJ*p, residual=J*after-target;
  if((residual.array() < -velocityTolerance).any())continue;
  bool valid=true;for(auto i:active)if(std::abs(residual(i))>velocityTolerance)valid=false;
  if(!valid)continue;
  ImpactResult result;result.velocity=after;result.impulse=p;result.normalVelocity=J*after;
  result.momentumResidual=(M*(after-before)-J.transpose()*p).norm();
  result.energyLoss=.5*(before.dot(M*before)-after.dot(M*after));
  // Coupled Newton restitution can inject energy for mixed contacts. Refuse
  // this model regime instead of relabeling energy creation as dissipation.
  if(result.energyLoss < -impulseTolerance*before.norm())
   throw std::runtime_error("Newton impact produced energy; coupled restitution unsupported");
  return result;
 }
 throw std::runtime_error("no feasible independent impact active set");
}
}
