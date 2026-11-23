#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/type/Vec.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <stdexcept>
class NativeCableOrigin:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeCableOrigin,sofa::core::objectmodel::BaseObject);
 using BL=sofa::core::objectmodel::BaseLink;
 using Vec=sofa::type::Vec<3,double>;
 sofa::core::objectmodel::SingleLink<NativeCableOrigin,sofa::core::objectmodel::BaseObject,BL::FLAG_STOREPATH|BL::FLAG_STRONGLINK>target;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<bool>drive;
 sofa::core::objectmodel::Data<double>begin,end,height;
 Vec origin;std::ofstream file;
 NativeCableOrigin():target(initLink("target","Actual Native CableConstraint;public PullPoint only")),filename(initData(&filename,std::string(),"filename","Exclusive origin journal")),drive(initData(&drive,false,"drive","False is read-only observer;true drives ONLY cable origin")),begin(initData(&begin,0.,"begin","Accepted end-clock ramp start s")),end(initData(&end,.01,"end","Accepted end-clock ramp end s")),height(initData(&height,.0001,"height","Prescribed fixture origin travel m")){f_listening.setValue(true);}
 sofa::core::objectmodel::Data<Vec>*data(){return target?dynamic_cast<sofa::core::objectmodel::Data<Vec>*>(target->findData("pullPoint")):nullptr;}
 void init()override{BaseObject::init();if(!data()||end.getValue()<=begin.getValue()||std::ifstream(filename.getValue()))throw std::runtime_error("explicit valid cable origin and exclusive journal required");origin=data()->getValue();file.open(filename.getValue());if(!file)throw std::runtime_error("origin journal open failed");file<<std::setprecision(17)<<"accepted_time_s,actual_pullPoint_m,initial_pullPoint_m,drive_enabled\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(drive.getValue()&&dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e)){const double t=getContext()->getTime()+getContext()->getDt();const double u=std::max(0.,std::min(1.,(t-begin.getValue())/(end.getValue()-begin.getValue())));auto q=origin;q[2]+=height.getValue()*u;data()->setValue(q);}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  file<<getContext()->getTime()<<",\""<<data()->getValue()<<"\",\""<<origin<<"\","<<drive.getValue()<<'\n';file.flush();
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCableOrigin";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "1";}
__attribute__((visibility("default")))const char*getModuleLicense(){return "Research";}
__attribute__((visibility("default")))const char*getModuleDescription(){return "Public cable origin observation/fixture control;no force/ODE/state solver";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Public actual cable origin journal and optional fixture motion").add<NativeCableOrigin>());}
}
