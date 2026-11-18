#define REGRIP_PLAN_EMBEDDED
#include "../film_transmission_plan/PlanOwner.cpp"
#include "Step.h"
namespace regrip_routed_tendon {
class FilmRoutedPlanODE:public regrip_transmission::FilmTransmissionPlanODE {
public:
 SOFA_CLASS(FilmRoutedPlanODE,regrip_transmission::FilmTransmissionPlanODE);
 double frozenAmplitude=-1;
 std::string expectedFieldClass()const override{return "FilmRoutedTendon";}
 void init()override{regrip_transmission::FilmTransmissionPlanODE::init();frozenAmplitude=parameter<double>("routeAmplitude");validate(model(),frozenAmplitude);}
 Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const override{if(parameter<double>("routeAmplitude")!=frozenAmplitude)throw std::runtime_error("route geometry changed without parameter-work model");return step(m,q,v,time,h,mass,frozenAmplitude);}
};
}
void registerFilmRoutedField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmRoutedTransmission";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL quadratic material-coordinate cable route,same core Gauss/public clock;NO object/contact/grasp qualification").add<regrip_routed_tendon::FilmRoutedPlanODE>());}
}
