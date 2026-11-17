#include "CoupledOwnerClass.h"
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCoupledSphere";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Experimental shared-mass free-sphere/film whole-surface event and constrained midpoint;NOT friction/general rigid/grasp qualification").add<regrip_coupled::CoupledSphereODE>());}
}
