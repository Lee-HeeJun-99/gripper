#define REGRIP_LATERAL_REST_EMBEDDED
#include "../film_lateral_rest_closing/RestClosing.cpp"
namespace regrip_three_resume {
class LateralRestResumeODE:public LateralRestClosingODE {
public:
 SOFA_CLASS(LateralRestResumeODE,LateralRestClosingODE);
 std::string inputCheckpointMagic()const override{return "REGRIP_LATERAL_REST_FREE_V1";}
 double maximumResumeEndTime()const override{return .05;}
 void bwdInit()override{
  if(externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("stationary-origin resume requires zero external force");
  // Existing reader validates exact mass/root/quaternion/q/v/time; its local
  // external parameter is unused by the restore geometry/mass operations.
  RoutedThreeFilmResumeODE::bwdInit();
 }
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&)override{
  std::string label,value;unsigned count;double time;in>>label>>count;if(label!="FREE_ACTIVE_COUNT"||count!=0)throw std::runtime_error("stationary-origin FREE active set differs");in>>label>>value;if(label!="INITIAL_CONDITION"||value!="STATIONARY_SEPARATED")throw std::runtime_error("stationary-origin history required");in>>label>>time;if(!in||label!="ACCUMULATED_TIME"||time!=initialTime||s.clearance(q)<=0)throw std::runtime_error("stationary-origin separated clock/state differs");
 }
};
}
#ifndef REGRIP_LATERAL_REST_RESUME_EMBEDDED
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripLateralRestResume";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL typed stationary-origin free continuation,zero external force;rejects first birth;NOT grasp").add<regrip_three_resume::LateralRestResumeODE>());}
}
#endif
