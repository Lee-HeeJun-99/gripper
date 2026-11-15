#include "Schedule.h"
#include <sofa/simulation/DefaultAnimationLoop.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/UpdateContextVisitor.h>
#include <sofa/core/ObjectFactory.h>
#include <fstream>
#include <iomanip>
#include <memory>
// Independent nonuniform integration contrast. SDK mechanics are unchanged;
// only the explicitly logged time grid changes at predeclared control epochs.
class EventStepClockAnimationLoop final:public sofa::simulation::DefaultAnimationLoop{
public:
 SOFA_CLASS(EventStepClockAnimationLoop,sofa::simulation::DefaultAnimationLoop);
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<sofa::type::vector<double>>eventTimes;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>>stepDivisors;
 sofa::simulation::Node*node=nullptr;std::unique_ptr<regrip_event_clock::Schedule>clock;std::ofstream log;
 EventStepClockAnimationLoop():filename(initData(&filename,std::string(""),"filename","Exclusive step grid log")),eventTimes(initData(&eventTimes,"eventTimes","Explicit event time grid")),stepDivisors(initData(&stepDivisors,"stepDivisors","Dyadic base-dt subdivisions")){}
 void init()override{
  sofa::simulation::DefaultAnimationLoop::init();node=dynamic_cast<sofa::simulation::Node*>(l_node.get());
  if(!node||node->getTime()!=0)throw std::runtime_error("fresh event grid requires time0");
  clock=std::make_unique<regrip_event_clock::Schedule>(node->getDt(),std::vector<double>(eventTimes.getValue().begin(),eventTimes.getValue().end()),std::vector<unsigned>(stepDivisors.getValue().begin(),stepDivisors.getValue().end()));
  std::ifstream old(filename.getValue());if(filename.getValue().empty()||old)throw std::runtime_error("refuse empty/old event grid log");log.open(filename.getValue());if(!log)throw std::runtime_error("event grid log");log<<std::setprecision(17)<<"step,begin_time,dt,end_time\n";
 }
 void step(const sofa::core::ExecParams*params,SReal)override{
  double begin=clock->time(),h=clock->dt(),old=node->getTime();
  if(std::abs(old-begin)>32*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(begin)))throw std::runtime_error("unrequested clock reset/jump");
  node->setTime(begin);node->setDt(h);node->execute<sofa::simulation::UpdateSimulationContextVisitor>(params);
  sofa::simulation::DefaultAnimationLoop::step(params,h);
  auto step=clock->steps;clock->advance();
  if(std::abs(node->getTime()-clock->time())>16*std::numeric_limits<double>::epsilon()*std::max(1.,clock->time()))throw std::runtime_error("SDK event step advance mismatch");
  if(step%1000==0){log<<step<<','<<begin<<','<<h<<','<<node->getTime()<<'\n';log.flush();}
 }
};
extern "C"{
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripEventStepClock";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Explicit event-aligned nonuniform SDK time grid").add<EventStepClockAnimationLoop>());}
}
