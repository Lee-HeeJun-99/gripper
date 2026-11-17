#include "../film_coupled_contact/CoupledOwnerClass.h"
#include "../film_coupled_contact/ReintegratedStep.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled {
class IsolatedReintegratedSphereODE final:public CoupledSphereODE {
public:
 SOFA_CLASS(IsolatedReintegratedSphereODE,CoupledSphereODE);
 sofa::core::objectmodel::Data<double>startTime{initData(&startTime,0.,"startTime","Explicit initial-state physical clock")};
 sofa::core::objectmodel::Data<bool>reintegratedEvent{initData(&reintegratedEvent,true,"reintegratedEvent","False is SAME-BINARY dense-event control;all force/solve parameters unchanged")};
 void init()override{
  CoupledSphereODE::init();auto*c=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());
  if(!c||!std::isfinite(startTime.getValue())||startTime.getValue()<0||startTime.getValue()>1||!strictNewton.getValue()||!midpointContact.getValue())throw std::runtime_error("isolated family prototype requires explicit clock/strictNewton/midpointContact");
  c->setTime(startTime.getValue());
 }
 Result advanceSystem(const System&original,double time,const EventControl&control)override{
  if(original.film.h>.001)throw std::runtime_error("isolated family prototype max1ms physical steps;not global/full-cycle certification");
  System system=original;system.absoluteNewtonResidual=1e-17;system.contactSolveGap=1e-14;
  return reintegratedEvent.getValue()?reintegratedStep(system,time,control):system.advance(time,control);
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCoupledReintegrated";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated entering-bracket coupled midpoint event;NOT global earliest CCD or qualified grasp").add<regrip_coupled::IsolatedReintegratedSphereODE>());}
}
