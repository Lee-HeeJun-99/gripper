#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <fstream>
#include <iomanip>
// Public stock proximity-data controller;NO force,ODE,contact or state solver.
class NativeAlarmWindow:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeAlarmWindow,sofa::core::objectmodel::BaseObject);
 using BL=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<NativeAlarmWindow,sofa::core::objectmodel::BaseObject,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK>target;
 sofa::core::objectmodel::Data<double>begin,end,narrow,wide;
 sofa::core::objectmodel::Data<std::string>filename;
 std::ofstream journal;
 NativeAlarmWindow():target(initLink("target","Installed native proximity intersection")),begin(initData(&begin,2.386,"begin","Absolute end-clock window start s")),end(initData(&end,2.396,"end","Absolute end-clock window end s")),narrow(initData(&narrow,.001,"narrow","Baseline native alarm m")),wide(initData(&wide,.005,"wide","Expanded native alarm m;contactDistance unchanged")),filename(initData(&filename,std::string(),"filename","Exclusive applied-data journal")){f_listening.setValue(true);}
 void init()override {BaseObject::init();if(!target||!target->findData("alarmDistance")||begin.getValue()>=end.getValue()||narrow.getValue()<=0||wide.getValue()<narrow.getValue()||std::ifstream(filename.getValue()))throw std::runtime_error("invalid explicit detection window");journal.open(filename.getValue());journal<<std::setprecision(17)<<"begin_context_s,applied_end_clock_s,actual_alarm_m,actual_contact_distance\n";}
 void handleEvent(sofa::core::objectmodel::Event*event)override {
  if(!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event))return;
  const double t=getContext()->getTime()+getContext()->getDt();
  const double value=t>=begin.getValue()&&t<=end.getValue()?wide.getValue():narrow.getValue();
  auto*data=dynamic_cast<sofa::core::objectmodel::Data<double>*>(target->findData("alarmDistance"));if(!data)throw std::runtime_error("typed native alarm required");data->setValue(value);
  journal<<getContext()->getTime()<<','<<t<<','<<data->getValue()<<','<<target->findData("contactDistance")->getValueString()<<'\n';journal.flush();
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripAlarmWindow";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "1";}
__attribute__((visibility("default")))const char*getModuleLicense(){return "Research";}
__attribute__((visibility("default")))const char*getModuleDescription(){return "Native public detection-data schedule;not a physics solver";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Bounded native alarm controller").add<NativeAlarmWindow>());}
}
