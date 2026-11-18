#define REGRIP_PLAN_EMBEDDED
#include "../film_transmission_plan/PlanOwner.cpp"
#include "Step.h"
namespace regrip_lateral_tendon {
class FilmLateralPlanODE:public regrip_transmission::FilmTransmissionPlanODE {
public:
 SOFA_CLASS(FilmLateralPlanODE,regrip_transmission::FilmTransmissionPlanODE);
 double frozenLateral=-1;
 std::string expectedFieldClass()const override{return "FilmLateralTendon";}
 void init()override{regrip_transmission::FilmTransmissionPlanODE::init();frozenLateral=parameter<double>("lateralOffset");validate(model(),frozenLateral);}
 Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const override{if(parameter<double>("lateralOffset")!=frozenLateral)throw std::runtime_error("lateral geometry changed without parameter-work model");return step(m,q,v,time,h,mass,frozenLateral);}
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmLateralTransmission";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL objective outboard cable route,same core Gauss/public clock;NO object/contact/grasp qualification").add<regrip_lateral_tendon::FilmLateralPlanODE>());}
}
