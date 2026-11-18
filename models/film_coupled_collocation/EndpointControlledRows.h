#pragma once
#include "PersistentRows.h"
namespace regrip_collocation {
struct EndpointControlledResult {
 Eigen::VectorXd q,v;
 std::vector<RowsResult> accepted;
 std::vector<double> durations;
 unsigned attempts=0,stageRejected=0,endpointRejected=0;
};
// Same one-step force/constraint law. ONLY an explicitly observed endpoint
// drift exception or returned stage-clearance violation admits reintegration.
// Unilateral release,ambiguous geometry and all other failures propagate.
// This controls contact admissibility,NOT the full temporal truncation error.
inline EndpointControlledResult endpointControlledRows(const Eigen::MatrixXd&M,double damping,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h,
 const std::function<Force(const Eigen::VectorXd&,double)>&force,
 const std::function<RowGeometry(const Eigen::VectorXd&)>&geometry,
 const std::function<double(const Eigen::VectorXd&)>&clearance,
 unsigned maximumAttempts=63,unsigned maximumDepth=5,
 const std::function<void(const RowsResult&,const Eigen::VectorXd&,const Eigen::VectorXd&,double,double)>&releaseObserver={}){
 if(!maximumAttempts||!(h>0))throw std::invalid_argument("positive bounded local attempt budget/step required");
 EndpointControlledResult out{q,v};
 std::function<void(double,double,unsigned)>advance;
 advance=[&](double start,double step,unsigned depth){
  if(++out.attempts>maximumAttempts)throw std::runtime_error("endpoint-controlled attempt budget;NOT OS exhaustion");
  bool endpoint=false;RowsResult result;
  try{result=persistentRows(M,damping,out.q,out.v,start,step,force,geometry,false,[&](const RowsResult&){endpoint=true;},[&](const RowsResult&r){if(releaseObserver)releaseObserver(r,out.q,out.v,start,step);});}
  catch(const std::domain_error&){if(!endpoint)throw;}
  bool split=endpoint;
  if(endpoint)++out.endpointRejected;
  else{
   double gap=clearance(out.q);bool activeGap=false;
   for(const auto&s:result.stages){gap=std::min(gap,clearance(s.q));activeGap=activeGap||s.geometry.gap.cwiseAbs().maxCoeff()>1e-10;}
   if(!std::isfinite(gap))throw std::domain_error("nonfinite whole-surface clearance");
   if(result.momentumResidual>1e-17||result.velocityResidual>1e-10)throw std::runtime_error("unchanged momentum/velocity gates failed");
   if(gap< -1e-10||activeGap){split=true;++out.stageRejected;}
  }
  if(split){
   if(depth>=maximumDepth)throw std::runtime_error("endpoint-controlled depth budget;original gates unchanged");
   const double end=start+step,middle=start+step/2;
   if(!(start<middle&&middle<end))throw std::runtime_error("nonrepresentable physical subdivision");
   advance(start,middle-start,depth+1);advance(middle,end-middle,depth+1);return;
  }
  out.q=result.q;out.v=result.v;out.accepted.push_back(std::move(result));out.durations.push_back(step);
 };
 advance(time,h,0);return out;
}
}
