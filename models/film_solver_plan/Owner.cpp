#define REGRIP_PRECISE_TENDON_OWNER_EMBEDDED
#include "../film_precise_tendon/Owner.cpp"
#include "Plan.h"
namespace regrip_solver_plan {
class FilmPreciseSolverPlanODE:public regrip_precise_tendon::FilmPreciseTendonSubcycledODE {
public:
 SOFA_CLASS(FilmPreciseSolverPlanODE,regrip_precise_tendon::FilmPreciseTendonSubcycledODE);
 double horizon()const override{return .001;}
 bool qualifiedSteps(unsigned n)const override{return n==40||n==80||n==160;}
 unsigned microstepCount(double t,double h)const override{return select(count-1,maxSteps.getValue(),t,h).microsteps;}
 double microstepTolerance(double t,double h)const override{return select(count-1,maxSteps.getValue(),t,h).newtonTolerance;}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripPreciseSolverPlan";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmPreciseAttachmentField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL explicit1ms early/late numerical plan;NOT grasp certification").add<regrip_solver_plan::FilmPreciseSolverPlanODE>());}
}
