#define REGRIP_RECOVERY_EMBEDDED
#include "../film_three_finger_recovery/ThreeFilmRecovery.cpp"
namespace regrip_three_resume {
// Separate admission scope. Legacy32/38ms classes/guards remain unchanged.
class ThreeFilmAfter38RecoveryODE:public ThreeFilmPersistentRecoveryODE {
public:
 SOFA_CLASS(ThreeFilmAfter38RecoveryODE,ThreeFilmPersistentRecoveryODE);
 double maximumResumeEndTime()const override{return .0444;}
 void init()override{
  if(getContext()->getTime()<.038-1e-14||nominalStep.getValue()!=.0001||observationSteps.getValue()!=8)throw std::runtime_error("new38..44.4ms scope requires qualified100us eight-step free plan");
  ThreeFilmPersistentRecoveryODE::init();
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmRecoveryNext";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL independently admitted38..44.4ms free observation;no contact/friction/lift/recovery completion certificate").add<regrip_three_resume::ThreeFilmAfter38RecoveryODE>());}
}
