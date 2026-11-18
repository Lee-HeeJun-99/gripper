#pragma once
#include "../film_three_finger_resume/AccelerationRelease.h"
#include "../film_three_finger_event/BlockFree.h"
#include <chrono>
#include <optional>
namespace regrip_routed_release {
using namespace regrip_three_resume;
struct Result {
 regrip_collocation::RowsResult pre;
 AccelerationRelease release;
 regrip_three_event::FreeState after;
 double preH=0,window=4e-5,rootLo=0,rootHi=0,minimumGap=0,momentumBound=0,minimumForce=0,outgoing=0;
 double rootSeconds=0,rkSeconds=0,freeSeconds=0;
 unsigned rootEvaluations=0;
};
// NEW bounded numerical composition of EXISTING laws. The signed root trials
// are diagnostic ONLY. All committed pre-stages remain compressive. The root
// is a collocation admissibility boundary,NOT a claimed continuous exit time.
inline Result resolve(const SharedFilmSystem&s,const Eigen::VectorXd&q,
 const Eigen::VectorXd&v,double time,double h,const std::vector<EdgeOwner>&edges,unsigned grid){
 if(h!=.0002||grid<16||grid>128||edges.size()!=3||time<.027||time+h>.03)throw std::invalid_argument("bounded200us routed release fixture,16..128 grid required");
 Result out;auto begin=std::chrono::steady_clock::now();
 auto applied=[&](const auto&x,double t){return s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension);};
 auto geometry=[&](const auto&x){return edgeGeometry(s,x,edges);};
 auto signedTrial=[&](double interval){
  ++out.rootEvaluations;std::optional<regrip_collocation::RowsResult>rejected;
  try{return regrip_collocation::persistentRows(s.shared.M,2,q,v,time,interval,applied,geometry,false,{},[&](const auto&r){rejected=r;});}
  catch(const std::domain_error&e){if(std::string(e.what())!="persistent stage row releases;active-set transition NOT implemented"||!rejected)throw;return *rejected;}
 };
 auto minimum=[](const auto&r){return std::min({r.initialForce.minCoeff(),r.stages[0].force.minCoeff(),r.stages[1].force.minCoeff()});};
 auto whole=signedTrial(h);if(whole.initialForce.minCoeff()<=0||minimum(whole)>=0)throw std::runtime_error("compressive-to-negative stage root not bracketed");
 out.rootHi=h;
 for(unsigned i=0;i<48&&out.rootHi-out.rootLo>1e-13;++i){double mid=(out.rootLo+out.rootHi)/2;auto trial=signedTrial(mid);if(minimum(trial)>=0)out.rootLo=mid;else out.rootHi=mid;}
 out.preH=out.rootLo-2e-5;const double finish=time+h,preTime=time+out.preH;
 if(!(out.preH>0&&preTime+out.window<finish))throw std::runtime_error("bounded20us safety/40us release window does not fit;no forced release");
 out.pre=regrip_collocation::persistentRows(s.shared.M,2,q,v,time,out.preH,applied,geometry);
 out.minimumGap=s.clearance(q);for(const auto&stage:out.pre.stages)out.minimumGap=std::min(out.minimumGap,s.clearance(stage.q));
 if(out.minimumGap< -1e-10||minimum(out.pre)<0)throw std::runtime_error("pre-release physical stage gate failed");
 auto rkStart=std::chrono::steady_clock::now();out.rootSeconds=std::chrono::duration<double>(rkStart-begin).count();
 out.release=accelerationRelease(s,out.pre.q,out.pre.v,preTime,out.window,edges,grid);
 if(out.release.finalMask!=0)throw std::runtime_error("local acceleration window did not release all rows;no forced mask");
 auto freeStart=std::chrono::steady_clock::now();out.rkSeconds=std::chrono::duration<double>(freeStart-rkStart).count();
 double remaining=finish-out.release.endTime;if(!(remaining>0))throw std::runtime_error("actual accumulated RK clock leaves no positive free remainder;no clock reset");
 regrip_film_impact::EventControl control{.0001,.01,.02,.03,true};out.after=regrip_three_event::freeMidpoint(s,out.release.q,out.release.v,out.release.endTime,remaining,control);
 out.freeSeconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-freeStart).count();
 Eigen::VectorXd middle=(out.release.q+out.after.q)/2;
 out.minimumGap=std::min({out.minimumGap,out.release.minimumGap,s.clearance(middle),s.clearance(out.after.q)});
 out.momentumBound=out.pre.momentumResidual+out.release.momentumResidual+out.after.momentumResidual;
 out.minimumForce=std::min(minimum(out.pre),out.release.minimumForce);out.outgoing=(geometry(out.after.q).J*out.after.v).minCoeff();
 if(out.minimumGap< -1e-10||s.clearance(out.after.q)<=0||out.momentumBound>1e-17||out.minimumForce<0||out.outgoing<=0)throw std::runtime_error("composed release/separation/segment momentum-bound gate failed");
 return out;
}
}
