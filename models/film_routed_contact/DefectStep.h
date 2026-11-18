#pragma once
#include "../film_coupled_collocation/PersistentRows.h"
#include <string>
namespace regrip_defect_step {
using namespace regrip_collocation;
struct Leaf{double begin=0,h=0;Eigen::VectorXd q0,v0;RowsResult result;};
struct Result{Eigen::VectorXd q,v;std::vector<Leaf>leaves;unsigned trials=0,rejected=0,maximumDepth=0;double minimumGap=0;};
// Constraint-defect controlled local refinement,NOT a state-error controller.
// No state projection,force change,negative multiplier or tolerance relaxation.
inline Result integrate(const Eigen::MatrixXd&M,double damping,const Eigen::VectorXd&q,
 const Eigen::VectorXd&v,double time,double h,
 const std::function<Force(const Eigen::VectorXd&,double)>&force,
 const std::function<RowGeometry(const Eigen::VectorXd&)>&geometry,
 const std::function<double(const Eigen::VectorXd&)>&clearance){
 if(!(h>0)||time+h==time)throw std::invalid_argument("representable defect-step interval required");
 Result out{q,v};out.minimumGap=clearance(q);
 std::function<void(const Eigen::VectorXd&,const Eigen::VectorXd&,double,double,unsigned)>visit;
 visit=[&](const auto&q0,const auto&v0,double t,double dt,unsigned depth){
  if(++out.trials>64)throw std::runtime_error("defect-step trial budget64;no accepted macro commit");
  out.maximumDepth=std::max(out.maximumDepth,depth);bool split=false;RowsResult r;
  try{
   r=persistentRows(M,damping,q0,v0,t,dt,force,geometry);
   for(const auto&s:r.stages){double gap=clearance(s.q);if(gap< -1e-10||s.geometry.gap.cwiseAbs().maxCoeff()>1e-10)split=true;}
  }catch(const std::domain_error&e){
   // Release/rank/geometry failures are NOT reclassified as integration defects.
   if(std::string(e.what())!="persistent rows endpoint drift;no projection")throw;
   split=true;
  }
  if(!split){
   for(const auto&s:r.stages)out.minimumGap=std::min(out.minimumGap,clearance(s.q));
   out.q=r.q;out.v=r.v;out.leaves.push_back({t,dt,q0,v0,std::move(r)});return;
  }
  ++out.rejected;
  if(depth==8)throw std::runtime_error("defect-step depth8;no accepted macro commit");
  const double mid=t+dt/2,end=t+dt,h1=mid-t,h2=end-mid;
  if(!(h1>0&&h2>0)||t+h1!=mid||mid+h2!=end)throw std::runtime_error("defect-step clock not representable;no reset");
  visit(q0,v0,t,h1,depth+1);auto qm=out.q,vm=out.v;
  visit(qm,vm,mid,h2,depth+1);
 };
 visit(q,v,time,h,0);return out;
}
}
