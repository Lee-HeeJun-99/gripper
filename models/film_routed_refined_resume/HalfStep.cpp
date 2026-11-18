// Compiled ONLY against a source-verified routed1278 archive by the runner.
// Explicit one-step method dt transition;not a q/v projection or BDF restart.
#define REGRIP_THREE_RESUME_EMBEDDED
#include "../film_three_finger_resume/ThreeFilmResume.cpp"
namespace regrip_three_resume {
class RoutedHalfStepResumeODE:public RoutedThreeFilmResumeODE {
public:
 SOFA_CLASS(RoutedHalfStepResumeODE,RoutedThreeFilmResumeODE);
 sofa::core::objectmodel::Data<std::string>inputMagic{initData(&inputMagic,std::string("REGRIP_ROUTED_PERSISTENT_V1"),"inputMagic","Explicit source checkpoint schema;V1 or HALF_V1 only")};
 std::string inputCheckpointMagic()const override{return inputMagic.getValue();}
 std::string outputCheckpointMagic()const override{return "REGRIP_ROUTED_HALF_V1";}
 void bwdInit()override{
  if(inputMagic.getValue()!="REGRIP_ROUTED_PERSISTENT_V1"&&inputMagic.getValue()!="REGRIP_ROUTED_HALF_V1")throw std::runtime_error("routed source schema not admitted");
  RoutedThreeFilmResumeODE::bwdInit();
  const double used=savedDt;
  if(!restored||(used!=.0002&&used!=.0001)||getContext()->getTime()!=initialTime)throw std::runtime_error("exact source time/used dt required before explicit refinement");
  // Lobatto is a one-step map:there is no multistep physical history to fake.
  // All eleven public contexts are changed before the first animate,not after
  // a solve. Saved physical coordinates,velocities,quaternion remain untouched.
  savedDt=.0001;clocks(initialTime,savedDt);
  std::string path=filename.getValue()+".restart.csv";
  if(std::ifstream(path))throw std::runtime_error("refinement transition journal exists");
  std::ofstream out(path);out<<std::setprecision(17)<<"time,prior_used_dt,next_dt,prior_steps,contexts\n"<<initialTime<<','<<used<<','<<savedDt<<','<<priorSteps<<",11\n";
  if(!out)throw std::runtime_error("refinement journal write failed");
 }
};
}
void registerFilmRoutedField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripRoutedRefinedResume";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL explicit half dt one-step routed checkpoint continuation;NOT adaptive/global time/grasp").add<regrip_three_resume::RoutedHalfStepResumeODE>());}
}
