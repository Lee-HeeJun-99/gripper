#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <fstream>
#include <iomanip>
#include <cmath>
// Explicit actuator INPUT contrast,NOT observer/force/ODE/constraint solver.
class ReGripCablePause:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ReGripCablePause,sofa::core::objectmodel::BaseObject);
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<ReGripCablePause,BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>target;
 sofa::core::objectmodel::Data<double>endTime;sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<double>*maximum=nullptr;double original=0;std::ofstream log;
 ReGripCablePause():target(initLink("target","Existing NativeCableSequence input owner")),endTime(initData(&endTime,.05,"endTime","ONE step ending at this time")),filename(initData(&filename,std::string(),"filename","Exclusive input journal")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!target||std::ifstream(filename.getValue()))throw std::runtime_error("explicit input and unique log required");maximum=dynamic_cast<sofa::core::objectmodel::Data<double>*>(target->findData("maximumForceN"));if(!maximum)throw std::runtime_error("typed existing maximumForceN required");original=maximum->getValue();if(original<0)throw std::runtime_error("force mode required");log.open(filename.getValue());log<<std::setprecision(17)<<"begin_time_s,end_time_s,maximumForceN,paused\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e))return;double end=getContext()->getTime()+getContext()->getDt();bool pause=std::abs(end-endTime.getValue())<1e-12;maximum->setValue(pause?0:original);log<<getContext()->getTime()<<','<<end<<','<<maximum->getValue()<<','<<pause<<'\n';log.flush();}
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCablePause";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Declared one-step actuator input pause,no state changes").add<ReGripCablePause>());}
}
