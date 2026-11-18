#define REGRIP_TRANSMISSION_EMBEDDED
#include "../film_transmission/Owner.cpp"
namespace regrip_transmission {
// Explicit experimental PUBLIC step plan. Not an error-controlled controller.
class FilmTransmissionPlanODE:public FilmTransmissionODE {
public:
 SOFA_CLASS(FilmTransmissionPlanODE,FilmTransmissionODE);
 sofa::core::objectmodel::Data<std::string>planFilename{initData(&planFilename,std::string(),"planFilename","Immutable accepted endpoint plan,not prescribed geometry")};
 std::vector<double>endpoints;std::ofstream clocks;
 FilmTransmissionPlanODE(){f_listening.setValue(true);}
 EventControl prescribedControl()const override{return holdControl();}
 Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double t,double h,const std::vector<double>&mass)const override{return stepGauss(m,q,v,t,h,mass,prescribedControl());}
 void init()override{
  FilmTransmissionODE::init();std::ifstream in(planFilename.getValue());unsigned n;in>>n;if(!in||n!=maxSteps.getValue())throw std::runtime_error("explicit plan budget differs");double prior=0;
  for(unsigned i=0;i<n;++i){double time;in>>time;if(!in||!std::isfinite(time)||time<=prior||time>.05||time-prior>.001)throw std::runtime_error("invalid bounded public physical-time plan");endpoints.push_back(time);prior=time;}std::string extra;if(in>>extra)throw std::runtime_error("plan trailing data");
  if(getContext()->getDt()!=endpoints.front())throw std::runtime_error("initial public plan dt differs");if(std::ifstream(filename.getValue()+".clock.csv"))throw std::runtime_error("clock journal exists");clocks.open(filename.getValue()+".clock.csv");clocks<<std::setprecision(17)<<"time,used_dt,next_dt,contexts,exact_child_time\n";
 }
 double interval(double t,double dt)const override{
  if(count<1||count>endpoints.size()||t!=(count==1?0:endpoints[count-2])||t+dt!=endpoints[count-1])throw std::runtime_error("actual public plan clock differs;NO time reset");return endpoints[count-1]-t;
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;double time=getContext()->getTime(),used=getContext()->getDt();if(count<1||count>endpoints.size()||time!=endpoints[count-1]||time!=last+used)throw std::runtime_error("plan accepted endpoint differs");double next=count==endpoints.size()?used:endpoints[count]-time;
  auto*root=dynamic_cast<sofa::core::objectmodel::BaseNode*>(getContext());std::set<sofa::core::objectmodel::BaseNode*>seen;std::function<void(sofa::core::objectmodel::BaseNode*)>apply=[&](auto*node){if(!seen.insert(node).second)return;if(node->getContext()->getTime()!=time)throw std::runtime_error("plan child time differs;not overwritten");node->getContext()->setDt(next);if(node->getContext()->getDt()!=next)throw std::runtime_error("plan next dt rejected");for(auto*child:node->getChildren())apply(child);};if(!root||!(next>0))throw std::runtime_error("plan root/dt invalid");apply(root);if(seen.size()!=4)throw std::runtime_error("plan scene topology differs");clocks<<time<<','<<used<<','<<next<<','<<seen.size()<<",true\n";clocks.flush();
 }
};
}
#ifndef REGRIP_PLAN_EMBEDDED
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmTransmissionPlan";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL explicit variable public-dt Gauss plan,all child clocks;NOT error-controlled adaptive/contact/grasp certification").add<regrip_transmission::FilmTransmissionPlanODE>());}
}
#endif
