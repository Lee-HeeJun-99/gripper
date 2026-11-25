#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <stdexcept>
// Public input-data schedule only. All forces/matrices remain STOCK Native.
// This class NEVER reads or writes a mechanical q/v/free-state or solver row.
class NativeBrakeSchedule: public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeBrakeSchedule,sofa::core::objectmodel::BaseObject);
 using BL=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<NativeBrakeSchedule,sofa::core::objectmodel::BaseObject,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK> target;
 sofa::core::objectmodel::Data<double> begin,end,coefficient;
 sofa::core::objectmodel::Data<std::string> filename;
 std::ofstream journal;
 NativeBrakeSchedule():target(initLink("target","Stock implicit UniformVelocityDampingForceField")),begin(initData(&begin,.5,"begin","End-clock onset s")),end(initData(&end,.6,"end","End-clock full brake s")),coefficient(initData(&coefficient,0.,"coefficient","Nonnegative final coefficient;research input,not material evidence")),filename(initData(&filename,std::string(),"filename","Exclusive applied-data journal")){f_listening.setValue(true);}
 void init() override {
  BaseObject::init();
  if(!target||!target->findData("dampingCoefficient")||!target->findData("implicit")||target->findData("implicit")->getValueString()!="1"||begin.getValue()<0||end.getValue()<=begin.getValue()||!std::isfinite(coefficient.getValue())||coefficient.getValue()<0||std::ifstream(filename.getValue()))throw std::runtime_error("Invalid bounded public brake-data schedule");
  journal.open(filename.getValue());if(!journal)throw std::runtime_error("Cannot open exclusive brake journal");journal<<std::setprecision(17)<<"begin_context_s,applied_end_clock_s,coefficient\n";
 }
 void handleEvent(sofa::core::objectmodel::Event* e) override {
  if(!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e))return;
  const double t=getContext()->getTime()+getContext()->getDt();
  const double u=std::clamp((t-begin.getValue())/(end.getValue()-begin.getValue()),0.,1.);
  const double s=u*u*u*(10.+u*(-15.+6.*u));
  auto* data=dynamic_cast<sofa::core::objectmodel::Data<double>*>(target->findData("dampingCoefficient"));if(!data)throw std::runtime_error("Typed double dampingCoefficient required");
  data->setValue(coefficient.getValue()*s);
  journal<<getContext()->getTime()<<','<<t<<','<<data->getValue()<<'\n';journal.flush();
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripBrakeSchedule";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "1";}
__attribute__((visibility("default")))const char*getModuleLicense(){return "Research";}
__attribute__((visibility("default")))const char*getModuleDescription(){return "Nonnegative public actuator-data schedule,not a physics solver";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory* f){f->registerObjects(sofa::core::ObjectRegistrationData("Stock implicit rotor-loss data schedule").add<NativeBrakeSchedule>());}
}
