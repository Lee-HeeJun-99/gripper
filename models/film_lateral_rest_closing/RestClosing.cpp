// Separate initial-value problem: stationary sphere, zero external load.
// Existing incoming-sphere owners and their guards remain unchanged.
#define REGRIP_LATERAL_RELEASE_EMBEDDED
#include "../film_lateral_release/LateralRelease.cpp"
namespace regrip_three_resume {
class LateralRestClosingODE:public LateralFreeODE {
public:
 SOFA_CLASS(LateralRestClosingODE,LateralFreeODE);
 void bwdInit()override{
  RoutedThreeFilmDrivenODE::bwdInit();
  if(!ready||!checkpoint.getValue().empty()||getContext()->getTime()!=0||getContext()->getDt()!=.0002||identity.getValue().size()!=64||externalForce.getValue()!=sofa::type::Vec3(0,0,0)||endTime.getValue()<=0||endTime.getValue()>.01)throw std::runtime_error("NEW REST closing fixture requires zero clock/load and no checkpoint");
  SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);Eigen::VectorXd expected=s.initial;expected(3*s.shared.nf+2)+=.0001;
  const auto&orientation=body->read(sofa::core::vec_id::read_access::position)->getValue()[0].getOrientation();
  if((q-expected).cwiseAbs().maxCoeff()!=0||v.norm()!=0||orientation[0]!=0||orientation[1]!=0||orientation[2]!=0||orientation[3]!=1||s.clearance(q)<=0)throw std::runtime_error("NEW stationary sphere/rest films/strict separation initial condition differs");
  initialTime=0;savedDt=.0002;priorSteps=0;count=0;restored=true;clocks(0,savedDt);
 }
 std::string outputCheckpointMagic()const override{return "REGRIP_LATERAL_REST_FREE_V1";}
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&,const Eigen::VectorXd&,double time)override{out<<"FREE_ACTIVE_COUNT 0\nINITIAL_CONDITION STATIONARY_SEPARATED\nACCUMULATED_TIME "<<time<<'\n';}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||dt!=.0002||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>endTime.getValue()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("bounded NEW stationary-sphere closing window required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);if(s.clearance(q)<=0)throw std::runtime_error("rest-closing initial gap lost;separate event solve required");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;auto after=regrip_three_event::freeMidpoint(s,q,v,last,dt,control);auto path=regrip_three_event::denseSurfacePath(s,q,v,after,dt);auto cert=regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);
  if(!cert.clear){auto event=regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius);if(event)throw std::runtime_error("NEW rest-closing birth detected;NO unvalidated contact commit");}
  Eigen::VectorXd middle=(q+after.q)/2,mv=(v+after.v)/2;double gap=std::min({s.clearance(q),s.clearance(middle),s.clearance(after.q)});if(gap< -1e-10)throw std::runtime_error("rest-closing stage clearance fails");
  for(unsigned i=0;i<3;++i){freeStages<<priorSteps+count+1<<','<<(i==0?"initial":i==1?"force_midpoint":"end")<<','<<last+(i==0?0:i==1?dt/2:dt)<<','<<(i==1?dt:0);quote(freeStages,i==0?q:i==1?middle:after.q);quote(freeStages,i==0?v:i==1?mv:after.v);freeStages<<'\n';}freeStages.flush();
  commitActual(s,after.q,after.v,last+dt);accepted<<last+dt<<','<<gap<<','<<after.momentumResidual<<",null,0,"<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
#ifndef REGRIP_LATERAL_REST_EMBEDDED
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripLateralRestClosing";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL stationary free sphere,zero external load,C2 rest closing;rejects first birth;NOT grasp").add<regrip_three_resume::LateralRestClosingODE>());}
}
#endif
