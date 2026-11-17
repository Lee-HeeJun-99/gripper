#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled {
// Isolated continuation experiment,not a hidden position/velocity correction.
// XML explicitly supplies the full saved event state. This stateless one-step
// owner restores ONLY the public physical clock;no BDF/history approximation.
class CoupledRestartODE final:public CoupledSphereODE {
public:
 SOFA_CLASS(CoupledRestartODE,CoupledSphereODE);
 sofa::core::objectmodel::Data<double>startTime{initData(&startTime,0.,"startTime","Explicit physical clock of the declared initial event state")};
 void init()override{
  CoupledSphereODE::init();auto*c=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());
  if(!c||!std::isfinite(startTime.getValue())||startTime.getValue()<0||startTime.getValue()>1)throw std::runtime_error("bounded restart physical clock required");
  c->setTime(startTime.getValue());
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCoupledRestart";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Explicit saved-event stateless coupled continuation;NOT full-cycle qualification").add<regrip_coupled::CoupledRestartODE>());}
}
