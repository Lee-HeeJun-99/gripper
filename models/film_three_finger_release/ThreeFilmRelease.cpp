#define REGRIP_THREE_PRIMITIVE_EMBEDDED
#include "../film_three_finger_primitive/ThreeFilmPrimitive.cpp"
#include "../film_three_finger_resume/AccelerationRelease.h"
#include "../film_three_finger_event/BlockFree.h"
#include "../film_three_finger_event/DenseSurfacePath.h"
namespace regrip_three_resume {
class ThreeFilmAccelerationReleaseODE:public ThreeFilmEdgeODE {
public:
 SOFA_CLASS(ThreeFilmAccelerationReleaseODE,ThreeFilmEdgeODE);
 std::string outputCheckpointMagic()const override{return "REGRIP_FREE_V3";}
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{out<<"FREE_ACTIVE_COUNT 0\nRELEASED_EDGES "<<edges.size()<<'\n';for(unsigned i=0;i<edges.size();++i){const auto&e=edges[i];out<<e.finger<<' '<<e.sourceTriangle<<' '<<e.nodes[0]<<' '<<e.nodes[1]<<' '<<birthTimes[i]<<'\n';}out<<"ACCUMULATED_TIME "<<time<<'\n';}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0001||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("isolated one-step acceleration release window guard");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);double window=dt/5;
  auto release=accelerationRelease(s,q,v,last,window,edges,64);if(release.finalMask!=0)throw std::runtime_error("acceleration interval did not release all rows");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;
  const double finish=last+dt,remaining=finish-release.endTime;
  auto after=regrip_three_event::freeMidpoint(s,release.q,release.v,release.endTime,remaining,control);Eigen::VectorXd middle=(release.q+after.q)/2;double gap=std::min({release.minimumGap,s.clearance(middle),s.clearance(after.q)}),momentum=release.momentumResidual+after.momentumResidual;
  if(gap< -1e-10||momentum>1e-17)throw std::runtime_error("release/free remaining interval gap or momentum gate fails");
  std::string path=filename.getValue()+".release.stages.csv";if(std::ifstream(path))throw std::runtime_error("release journal exists");std::ofstream journal(path);journal<<std::setprecision(17)<<"time,weight_s,mask,linear_solve_residual,force,q,v\n";for(const auto&stage:release.stages){journal<<stage.time<<','<<stage.weight<<','<<stage.mask<<','<<stage.residual;quote(journal,stage.force);quote(journal,stage.q);quote(journal,stage.v);journal<<'\n';}journal.flush();
  std::ofstream freeJournal(filename.getValue()+".release.free.csv");freeJournal<<std::setprecision(17)<<"kind,time,weight_s,q,v\n";Eigen::VectorXd middleV=(release.v+after.v)/2;for(unsigned i=0;i<3;++i){const auto&x=i==0?release.q:i==1?middle:after.q;const auto&vel=i==0?release.v:i==1?middleV:after.v;double t=i==0?release.endTime:i==1?release.endTime+remaining/2:finish;freeJournal<<(i==0?"initial":i==1?"midpoint":"end")<<','<<t<<','<<(i==1?remaining:0);quote(freeJournal,x);quote(freeJournal,vel);freeJournal<<'\n';}freeJournal.flush();
  // Public mapped Film and Rigid3 APIs are checked exactly by the reused commit.
  auto finalGeometry=edgeGeometry(s,after.q,edges);double outgoing=(finalGeometry.J*after.v).minCoeff();if(outgoing<=0)throw std::runtime_error("released endpoint is not separating");
  std::ofstream metrics(filename.getValue()+".release.metrics.csv");metrics<<std::setprecision(17)<<"time,minimum_gap_mm,momentum_Ns,minimum_force_N,final_active_mask,outgoing_normal_velocity_min_mm_s\n"<<last+dt<<','<<gap<<','<<momentum<<','<<release.minimumForce<<",0,"<<outgoing<<'\n';metrics.flush();
  commitActual(s,after.q,after.v,last+dt);accepted<<last+dt<<','<<gap<<','<<momentum<<",null,"<<release.stages.size()<<','<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
class ThreeFilmFreeODE:public ThreeFilmAccelerationReleaseODE {
public:
 SOFA_CLASS(ThreeFilmFreeODE,ThreeFilmAccelerationReleaseODE);
 std::ofstream freeStages;
 std::string inputCheckpointMagic()const override{return "REGRIP_FREE_V3";}
 void init()override{ThreeFilmAccelerationReleaseODE::init();if(!ready)return;std::string path=filename.getValue()+".free.stages.csv";if(std::ifstream(path))throw std::runtime_error("free-stage journal exists");freeStages.open(path);freeStages<<std::setprecision(17)<<"macro,kind,time,weight_s,q,v\n";}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&)override{
  std::string label;unsigned active,count;in>>label>>active;if(label!="FREE_ACTIVE_COUNT"||active!=0)throw std::runtime_error("FREE V3 requires explicitly empty active set");in>>label>>count;if(label!="RELEASED_EDGES"||count!=3)throw std::runtime_error("FREE V3 released owner audit required");edges.clear();birthTimes.clear();
  for(unsigned f=0;f<3;++f){EdgeOwner e;double born;in>>e.finger>>e.sourceTriangle>>e.nodes[0]>>e.nodes[1]>>born;if(!in||e.finger!=f||born>initialTime||e.nodes[0]==e.nodes[1]||e.sourceTriangle>=s.shared.films[f].triangles.size())throw std::runtime_error("FREE released owner identity invalid");const auto&tri=s.shared.films[f].triangles[e.sourceTriangle];for(unsigned node:e.nodes)if(std::find(tri.begin(),tri.end(),node)==tri.end())throw std::runtime_error("FREE released edge topology invalid");edges.push_back(e);birthTimes.push_back(born);}
  double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=initialTime||s.clearance(q)<=0)throw std::runtime_error("FREE accumulated clock or strictly separated surface invalid");
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||dt!=.0001||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("explicit FREE V3 bounded physical clock window");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);if(s.clearance(q)<=0)throw std::runtime_error("FREE initial state is not separated");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;auto after=regrip_three_event::freeMidpoint(s,q,v,last,dt,control);
  auto path=regrip_three_event::denseSurfacePath(s,q,v,after,dt);auto event=regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(event)throw std::runtime_error("FREE dense numerical path has reimpact;separate event solve required,not committed");
  Eigen::VectorXd middle=(q+after.q)/2,middleV=(v+after.v)/2;double gap=std::min({s.clearance(q),s.clearance(middle),s.clearance(after.q)});if(gap< -1e-10)throw std::runtime_error("FREE whole force-stage gap fails");
  for(unsigned i=0;i<3;++i){const auto&x=i==0?q:i==1?middle:after.q;const auto&vel=i==0?v:i==1?middleV:after.v;freeStages<<priorSteps+count+1<<','<<(i==0?"initial":i==1?"force_midpoint":"end")<<','<<(last+(i==0?0:i==1?dt/2:dt))<<','<<(i==1?dt:0);quote(freeStages,x);quote(freeStages,vel);freeStages<<'\n';}freeStages.flush();
  commitActual(s,after.q,after.v,last+dt);accepted<<last+dt<<','<<gap<<','<<after.momentumResidual<<",null,0,"<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmRelease";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated20us three-row acceleration complementarity release plus80us free midpoint;NOT full time/energy/grasp").add<regrip_three_resume::ThreeFilmAccelerationReleaseODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL separated FREE V3 resume and midpoint continuation;rejects dense-path reimpact;NOT grasp").add<regrip_three_resume::ThreeFilmFreeODE>());}
}
