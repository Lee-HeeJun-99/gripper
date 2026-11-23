// ONLY the Native potential API is overridden. Native addForce/addDForce/matrix
// assembly/integration are inherited UNMODIFIED. No state writes or SDK edits.
#include <sofa/core/ObjectFactory.h>
#include <sofa/component/solidmechanics/spring/SpringForceField.h>
#include <sofa/defaulttype/VecTypes.h>
namespace regrip {
using NativeSpring=sofa::component::solidmechanics::spring::SpringForceField<sofa::defaulttype::Vec3Types>;
class ReGripTensionSpringPotential: public NativeSpring {
public:
 SOFA_CLASS(ReGripTensionSpringPotential,NativeSpring);
 using NativeSpring::getPotentialEnergy;
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord& x1,const DataVecCoord& x2) const override {
  SReal energy=0;
  const auto& p=x1.getValue();const auto& q=x2.getValue();
  for(const auto& spring:d_springs.getValue()) {
   if(!spring.enabled) continue;
   const auto extension=(q[spring.m2]-p[spring.m1]).norm()-spring.initpos;
   if(spring.elongationOnly && extension<=0) continue;
   energy+=spring.ks*extension*extension/2;
  }
  return energy;
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripSpringPotential";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory* f){f->registerObjects(sofa::core::ObjectRegistrationData("Opt-in Native spring potential API correction only;unchanged Native force/tangent").add<regrip::ReGripTensionSpringPotential>());}
}
