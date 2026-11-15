#include "Clock.h"
#include <sofa/simulation/DefaultAnimationLoop.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/UpdateContextVisitor.h>
#include <sofa/core/ObjectFactory.h>
#include <fstream>
#include <iomanip>
// Preserve the SDK animation algorithm. Only the fixed-step clock is evaluated
// from its integer index instead of repeatedly adding binary dt. No physical
// state,force,control threshold or event definition is modified here.
class FixedStepClockAnimationLoop final:public sofa::simulation::DefaultAnimationLoop{
public:
 SOFA_CLASS(FixedStepClockAnimationLoop,sofa::simulation::DefaultAnimationLoop);
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::simulation::Node*clockNode=nullptr;double origin=0,h=0,maxCorrection=0;unsigned steps=0;std::ofstream log;
 FixedStepClockAnimationLoop():filename(initData(&filename,std::string(""),"filename","Exclusive numerical clock log")){}
 void init()override{
  sofa::simulation::DefaultAnimationLoop::init();clockNode=dynamic_cast<sofa::simulation::Node*>(l_node.get());
  if(!clockNode)throw std::runtime_error("fixed clock requires public linked simulation node");origin=clockNode->getTime();h=clockNode->getDt();regrip_clock::timeAt(origin,h,0);
  std::ifstream old(filename.getValue());if(filename.getValue().empty()||old)throw std::runtime_error("refuse empty/old clock output");log.open(filename.getValue());if(!log)throw std::runtime_error("clock output");log<<std::setprecision(17)<<"step,begin_time,end_time,correction_seconds,max_correction_seconds\n";
 }
 void step(const sofa::core::ExecParams*params,SReal dt)override{
  double effective=dt==0?clockNode->getDt():dt;if(effective!=h||steps>=240000)throw std::runtime_error("fixed clock forbids dt changes/excess steps;use an independently validated variable-step loop");
  double target=regrip_clock::timeAt(origin,h,steps),old=clockNode->getTime(),correction=target-old;
  if(std::abs(correction)>regrip_clock::accumulationBound(origin,h,steps))throw std::runtime_error("clock jump/reset is not roundoff;fresh validated scene required");
  maxCorrection=std::max(maxCorrection,std::abs(correction));clockNode->setTime(target);clockNode->execute<sofa::simulation::UpdateSimulationContextVisitor>(params);
  sofa::simulation::DefaultAnimationLoop::step(params,dt);
  double end=clockNode->getTime(),expected=target+h,tolerance=8*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(expected));
  if(std::abs(end-expected)>tolerance)throw std::runtime_error("SDK did not advance the requested step");
  if(steps%1000==0){log<<steps<<','<<target<<','<<end<<','<<correction<<','<<maxCorrection<<'\n';log.flush();}++steps;
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripFixedStepClock";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Integer-index fixed-step SDK clock;unchanged animation mechanics").add<FixedStepClockAnimationLoop>());}
}
