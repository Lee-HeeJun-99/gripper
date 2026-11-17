#pragma once
#include "PersistentRows.h"
namespace regrip_collocation {
// Reject an ENTIRE uncommitted step if either stage violates the original
// whole-surface clearance gate; reintegrate two halves with the same force law.
// No position/velocity projection, no tolerance relaxation, no event/active-set
// handling. Other solver/geometry exceptions propagate instead of being hidden.
struct GapControlledResult {
 Eigen::VectorXd q,v;
 std::vector<RowsResult> accepted;
 unsigned rejected=0,attempts=0;
};
inline GapControlledResult gapControlledRows(const Eigen::MatrixXd&M,double damping,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h,
 const std::function<Force(const Eigen::VectorXd&,double)>&force,
 const std::function<RowGeometry(const Eigen::VectorXd&)>&geometry,
 const std::function<double(const Eigen::VectorXd&)>&clearance,
 unsigned maximumAttempts=32,unsigned maximumDepth=4){
 if(!maximumAttempts)throw std::invalid_argument("gap-controlled attempt budget must be positive");
 GapControlledResult out{q,v};
 std::function<void(double,double,unsigned)>advance;
 advance=[&](double start,double step,unsigned depth){
  if(++out.attempts>maximumAttempts)throw std::runtime_error("gap-controlled local attempt budget;NOT OS exhaustion");
  auto result=persistentRows(M,damping,out.q,out.v,start,step,force,geometry);
  double gap=clearance(result.q);
  for(const auto&stage:result.stages)gap=std::min(gap,clearance(stage.q));
  if(!std::isfinite(gap))throw std::domain_error("nonfinite whole-surface clearance");
  if(gap< -1e-10){
   ++out.rejected;
   if(depth==maximumDepth)throw std::runtime_error("gap-controlled local depth budget;original gap gate NOT relaxed");
   advance(start,step/2,depth+1);advance(start+step/2,step/2,depth+1);return;
  }
  out.q=result.q;out.v=result.v;out.accepted.push_back(std::move(result));
 };
 advance(time,h,0);return out;
}
}
