// Built only against the qualified frozen face-release reference archive.
#define REGRIP_STATIONARY_CONTACT_EMBEDDED
#include "../film_lateral_rest_contact/StationaryImpact.cpp"
#include "../film_routed_contact/AdmissibleRelease.h"
#include "../film_routed_contact/SeparatedPath.h"
#include "../film_three_finger_event/DenseSurfacePath.h"
#include "FreeFooter.h"
namespace regrip_three_resume {
class StationaryReleaseODE:public StationaryPersistentODE {
public:
 SOFA_CLASS(StationaryReleaseODE,StationaryPersistentODE);
 sofa::core::objectmodel::Data<unsigned> releaseGrid;
 StationaryReleaseODE():releaseGrid(initData(&releaseGrid,unsigned(32),"releaseGrid","Source-bound independently qualified local release grid")){}
 std::vector<ContactOwner> releaseRows;
 std::string outputCheckpointMagic()const override{return "REGRIP_STATIONARY_FREE_V1";}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v)override{
  StationaryPersistentODE::readContactCheckpoint(in,s,q,v);releaseRows.clear();
  for(unsigned f=0;f<3;++f){auto row=s.selected(q,f);if(row.triangle!=116||row.feature!=6)throw std::runtime_error("qualified stationary face116/6 release fixture required");releaseRows.push_back({f,row.triangle,row.feature});}
  auto a=s.geometry(q),b=ownedGeometry(s,q,releaseRows);
  if((a.gap-b.gap).cwiseAbs().maxCoeff()>1e-12||(a.J-b.J).cwiseAbs().maxCoeff()>1e-12)throw std::runtime_error("selected/owned stationary face pullback differs");
  for(unsigned f=0;f<3;++f)if((a.H[f]-b.H[f]).cwiseAbs().maxCoeff()>1e-12)throw std::runtime_error("selected/owned stationary face Hessian differs");
 }
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{
  regrip_stationary_release::writeFreeFooter(out,{initialTime,time,lastImpactTime},time);
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0002||getContext()->getTime()!=initialTime||initialTime<.0267||initialTime>.0269||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("isolated zero-load stationary26.8ms release fixture required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);
  if(releaseGrid.getValue()!=32&&releaseGrid.getValue()!=64&&releaseGrid.getValue()!=128)throw std::runtime_error("bounded independently qualified release grid required");
  auto r=regrip_routed_release::resolve(s,q,v,last,dt,releaseRows,releaseGrid.getValue());
  auto open=[&](const char*suffix){std::string path=filename.getValue()+suffix;if(std::ifstream(path))throw std::runtime_error("stationary release journal exists");std::ofstream out(path);out<<std::setprecision(17);return out;};
  auto pre=open(".release.pre.csv");pre<<"time,weight_s,finger,force,gap,normal_velocity,q,v\n";
  for(unsigned k=0;k<3;++k){const auto&x=k?r.pre.stages[k-1].q:q;const auto&vel=k?r.pre.stages[k-1].v:v;auto g=ownedGeometry(s,x,releaseRows);for(unsigned f=0;f<3;++f){pre<<last+r.preH*(k==0?0:k==1?.5:1)<<','<<r.preH*(k==1?2./3:1./6)<<','<<f<<','<<(k?r.pre.stages[k-1].force(f):r.pre.initialForce(f))<<','<<g.gap(f)<<','<<g.J.row(f).dot(vel);quote(pre,x);quote(pre,vel);pre<<'\n';}}
  auto rk=open(".release.rk.csv");rk<<"time,weight_s,mask,force,q,v\n";for(const auto&z:r.release.stages){rk<<z.time<<','<<z.weight<<','<<z.mask;quote(rk,z.force);quote(rk,z.q);quote(rk,z.v);rk<<'\n';}rk.flush();
  const double finish=last+dt,remaining=finish-r.release.endTime;auto free=open(".release.free.csv");free<<"kind,time,weight_s,q,v\n";Eigen::VectorXd mid=(r.release.q+r.after.q)/2,mv=(r.release.v+r.after.v)/2;
  for(unsigned k=0;k<3;++k){free<<(k==0?"initial":k==1?"midpoint":"end")<<','<<(k==0?r.release.endTime:k==1?r.release.endTime+remaining/2:finish)<<','<<(k==1?remaining:0);quote(free,k==0?r.release.q:k==1?mid:r.after.q);quote(free,k==0?r.release.v:k==1?mv:r.after.v);free<<'\n';}
  auto metrics=open(".release.metrics.csv");metrics<<"time,pre_h_s,root_lo_s,root_hi_s,RK_end_time_s,minimum_gap_mm,momentum_bound_Ns,outgoing_normal_velocity_mm_s,final_mask\n"<<finish<<','<<r.preH<<','<<r.rootLo<<','<<r.rootHi<<','<<r.release.endTime<<','<<r.minimumGap<<','<<r.momentumBound<<','<<r.outgoing<<",0\n";
  commitActual(s,r.after.q,r.after.v,finish);accepted<<finish<<','<<r.minimumGap<<','<<r.momentumBound<<",null,"<<r.release.stages.size()<<','<<r.after.mechanicalEvaluations;quote(accepted,r.after.q);quote(accepted,r.after.v);accepted<<'\n';accepted.flush();++count;save(finish);
 }
};
class StationaryFreeODE:public StationaryReleaseODE {
public:
 SOFA_CLASS(StationaryFreeODE,StationaryReleaseODE);
 regrip_stationary_release::FreeProvenance provenance;
 std::string inputCheckpointMagic()const override{return "REGRIP_STATIONARY_FREE_V1";}
 double maximumResumeEndTime()const override{return .05;}
 // LateralFreeODE already owns and opens the inherited free stage stream.
 // Do not open that same immutable output path a second time in this subclass.
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&)override{provenance=regrip_stationary_release::readFreeFooter(in,initialTime);lastImpactTime=provenance.lastImpact;if(s.clearance(q)<=0)throw std::runtime_error("stationary FREE initial separation required");}
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{regrip_stationary_release::writeFreeFooter(out,provenance,time);}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||dt!=.0002||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("bounded zero-load stationary FREE clock required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);if(s.clearance(q)<=0)throw std::runtime_error("stationary FREE separation lost");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;auto after=regrip_three_event::freeMidpoint(s,q,v,last,dt,control);
  auto path=regrip_three_event::denseSurfacePath(s,q,v,after,dt);auto certificate=regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);
  if(!certificate.clear){auto event=regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(event)throw std::runtime_error("stationary FREE reimpact needs separate event solve;NO commit");}
  Eigen::VectorXd middle=(q+after.q)/2,mv=(v+after.v)/2;double gap=std::min({s.clearance(q),s.clearance(middle),s.clearance(after.q)});if(gap< -1e-10)throw std::runtime_error("stationary FREE whole-stage gap fails");
  for(unsigned i=0;i<3;++i){freeStages<<priorSteps+count+1<<','<<(i==0?"initial":i==1?"force_midpoint":"end")<<','<<(last+(i==0?0:i==1?dt/2:dt))<<','<<(i==1?dt:0);quote(freeStages,i==0?q:i==1?middle:after.q);quote(freeStages,i==0?v:i==1?mv:after.v);freeStages<<'\n';}freeStages.flush();
  commitActual(s,after.q,after.v,last+dt);accepted<<last+dt<<','<<gap<<','<<after.momentumResidual<<",null,0,"<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
#ifndef REGRIP_STATIONARY_RELEASE_EMBEDDED
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStationaryRelease";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL zero-load stationary-origin face release;NOT time/energy/grasp certification").add<regrip_three_resume::StationaryReleaseODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL typed zero-load stationary FREE continuation;reimpact rejects;NOT grasp").add<regrip_three_resume::StationaryFreeODE>());}
}
#endif
