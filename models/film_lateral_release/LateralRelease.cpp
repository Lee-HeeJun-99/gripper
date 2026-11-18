// Prepared/compiled ONLY by the source-bound lateral release runner.
#define REGRIP_THREE_PRIMITIVE_EMBEDDED
#include "../film_three_finger_primitive/ThreeFilmPrimitive.cpp"
#include "../film_routed_contact/AdmissibleRelease.h"
#include "../film_routed_contact/SeparatedPath.h"
#include "../film_three_finger_event/DenseSurfacePath.h"
#include "FreeFooter.h"
namespace regrip_three_resume {
class LateralReleaseODE:public RoutedThreeFilmEdgeODE {
public:
 SOFA_CLASS(LateralReleaseODE,RoutedThreeFilmEdgeODE);
 std::string inputCheckpointMagic()const override{return "REGRIP_LATERAL_CONTROLLED_V1";}
 std::string outputCheckpointMagic()const override{return "REGRIP_LATERAL_FREE_V1";}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v)override{
  edges.clear();birthTimes.clear();
  for(unsigned f=0;f<3;++f){unsigned triangle,feature;in>>triangle>>feature;auto row=s.selected(q,f);if(!in||triangle!=116||feature!=5||row.triangle!=triangle||row.feature!=feature)throw std::runtime_error("exact current lateral edge owner required");auto tri=s.shared.films[f].triangles[triangle];edges.push_back({f,triangle,{tri[1],tri[2]}});}
  auto selected=s.geometry(q),owned=edgeGeometry(s,q,edges);if((selected.gap-owned.gap).cwiseAbs().maxCoeff()>1e-12||(selected.J-owned.J).cwiseAbs().maxCoeff()>1e-12||s.clearance(q)<-1e-10||owned.gap.cwiseAbs().maxCoeff()>1e-10||(owned.J*v).cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("lateral material-edge geometry/state mismatch");
 }
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{
  out<<"FREE_ACTIVE_COUNT 0\nRELEASED_EDGE_GEOMETRY "<<edges.size()<<'\n';for(const auto&e:edges)out<<e.finger<<' '<<e.sourceTriangle<<' '<<e.nodes[0]<<' '<<e.nodes[1]<<'\n';out<<"RELEASE_INTERVAL "<<initialTime<<' '<<time<<"\nEDGE_BIRTH_HISTORY_UNMEASURED\nACCUMULATED_TIME "<<time<<'\n';
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0002||getContext()->getTime()!=initialTime||initialTime<.0269||initialTime>.0271||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("isolated actual27ms200us lateral release fixture required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);auto r=regrip_routed_release::resolve(s,q,v,last,dt,edges,128);
  auto open=[&](const char*suffix){std::string path=filename.getValue()+suffix;if(std::ifstream(path))throw std::runtime_error("release journal exists");std::ofstream out(path);out<<std::setprecision(17);return out;};
  auto pre=open(".release.pre.csv");pre<<"time,weight_s,finger,force,gap,normal_velocity,q,v\n";
  for(unsigned k=0;k<3;++k){const auto&x=k?r.pre.stages[k-1].q:q;const auto&vel=k?r.pre.stages[k-1].v:v;auto g=edgeGeometry(s,x,edges);for(unsigned f=0;f<3;++f){pre<<last+r.preH*(k==0?0:k==1?.5:1)<<','<<r.preH*(k==1?2./3:1./6)<<','<<f<<','<<(k?r.pre.stages[k-1].force(f):r.pre.initialForce(f))<<','<<g.gap(f)<<','<<g.J.row(f).dot(vel);quote(pre,x);quote(pre,vel);pre<<'\n';}}
  auto rk=open(".release.rk.csv");rk<<"time,weight_s,mask,force,q,v\n";for(const auto&z:r.release.stages){rk<<z.time<<','<<z.weight<<','<<z.mask;quote(rk,z.force);quote(rk,z.q);quote(rk,z.v);rk<<'\n';}rk.flush();
  const double finish=last+dt,remaining=finish-r.release.endTime;auto free=open(".release.free.csv");free<<"kind,time,weight_s,q,v\n";Eigen::VectorXd mid=(r.release.q+r.after.q)/2,mv=(r.release.v+r.after.v)/2;
  for(unsigned k=0;k<3;++k){free<<(k==0?"initial":k==1?"midpoint":"end")<<','<<(k==0?r.release.endTime:k==1?r.release.endTime+remaining/2:finish)<<','<<(k==1?remaining:0);quote(free,k==0?r.release.q:k==1?mid:r.after.q);quote(free,k==0?r.release.v:k==1?mv:r.after.v);free<<'\n';}
  auto metrics=open(".release.metrics.csv");metrics<<"time,pre_h_s,root_lo_s,root_hi_s,RK_end_time_s,minimum_gap_mm,momentum_bound_Ns,outgoing_normal_velocity_mm_s,final_mask\n"<<finish<<','<<r.preH<<','<<r.rootLo<<','<<r.rootHi<<','<<r.release.endTime<<','<<r.minimumGap<<','<<r.momentumBound<<','<<r.outgoing<<",0\n";
  commitActual(s,r.after.q,r.after.v,finish);accepted<<finish<<','<<r.minimumGap<<','<<r.momentumBound<<",null,"<<r.release.stages.size()<<','<<r.after.mechanicalEvaluations;quote(accepted,r.after.q);quote(accepted,r.after.v);accepted<<'\n';accepted.flush();++count;save(finish);
 }
};
class LateralFreeODE:public LateralReleaseODE {
public:
 SOFA_CLASS(LateralFreeODE,LateralReleaseODE);
 std::ofstream freeStages;regrip_lateral_release::AuditEdges auditEdges;double releaseBegin=0,releaseEnd=0;
 std::string inputCheckpointMagic()const override{return "REGRIP_LATERAL_FREE_V1";}
 double maximumResumeEndTime()const override{return .03;}
 void init()override{LateralReleaseODE::init();if(!ready)return;std::string path=filename.getValue()+".free.stages.csv";if(std::ifstream(path))throw std::runtime_error("free journal exists");freeStages.open(path);freeStages<<std::setprecision(17)<<"macro,kind,time,weight_s,q,v\n";}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&)override{
  auditEdges=regrip_lateral_release::readFreeFooter(in,s,initialTime,releaseBegin,releaseEnd);
  if(s.clearance(q)<=0)throw std::runtime_error("FREE initial surface not strictly separated");
 }
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{
  out<<"FREE_ACTIVE_COUNT 0\nRELEASED_EDGE_GEOMETRY "<<auditEdges.size()<<'\n';for(const auto&e:auditEdges)out<<e[0]<<' '<<e[1]<<' '<<e[2]<<' '<<e[3]<<'\n';out<<"RELEASE_INTERVAL "<<releaseBegin<<' '<<releaseEnd<<"\nEDGE_BIRTH_HISTORY_UNMEASURED\nACCUMULATED_TIME "<<time<<'\n';
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||dt!=.0002||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("bounded lateral FREE physical clock required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);if(s.clearance(q)<=0)throw std::runtime_error("FREE initial separation lost");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;auto after=regrip_three_event::freeMidpoint(s,q,v,last,dt,control);
  auto path=regrip_three_event::denseSurfacePath(s,q,v,after,dt);auto certificate=regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);
  if(!certificate.clear){auto event=regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(event)throw std::runtime_error("FREE numerical path reimpact requires separate event solve;not committed");}
  Eigen::VectorXd middle=(q+after.q)/2,mv=(v+after.v)/2;double gap=std::min({s.clearance(q),s.clearance(middle),s.clearance(after.q)});if(gap< -1e-10)throw std::runtime_error("FREE whole-stage gap fails");
  for(unsigned i=0;i<3;++i){freeStages<<priorSteps+count+1<<','<<(i==0?"initial":i==1?"force_midpoint":"end")<<','<<(last+(i==0?0:i==1?dt/2:dt))<<','<<(i==1?dt:0);quote(freeStages,i==0?q:i==1?middle:after.q);quote(freeStages,i==0?v:i==1?mv:after.v);freeStages<<'\n';}freeStages.flush();
  commitActual(s,after.q,after.v,last+dt);accepted<<last+dt<<','<<gap<<','<<after.momentumResidual<<",null,0,"<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripLateralRelease";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL actual bounded lateral deformed release;no whole time/energy/grasp certification").add<regrip_three_resume::LateralReleaseODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL typed separated lateral FREE resume;rejects reimpact;NOT grasp").add<regrip_three_resume::LateralFreeODE>());}
}
