// Compatibility registration ONLY. No contact arithmetic,return mapping,
// mechanical state,force,Jacobian,ODE,constraint solver or SDK implementation.
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/component/collision/detection/intersection/LocalMinDistance.h>
#include <sofa/component/collision/detection/intersection/MinProximityIntersection.h>
#include <sofa/component/collision/detection/intersection/MeshMinProximityIntersection.h>
#include <memory>
namespace regrip {
namespace native=sofa::component::collision::detection::intersection;
namespace geometry=sofa::component::collision::geometry;
class NativeRigidSphereLocalProximity:public native::LocalMinDistance {
public:
 SOFA_CLASS(NativeRigidSphereLocalProximity,native::LocalMinDistance);
 using RigidSphereModel=geometry::SphereCollisionModel<sofa::defaulttype::Rigid3Types>;
 using PointModel=geometry::PointCollisionModel<sofa::defaulttype::Vec3Types>;
 using LineModel=geometry::LineCollisionModel<sofa::defaulttype::Vec3Types>;
 using TriangleModel=geometry::TriangleCollisionModel<sofa::defaulttype::Vec3Types>;
 // Lifetime owns stock helper. DummyMin is NOT added to scene or initialized
 // as another intersection. addSelf=false prevents stock map registration.
 native::MinProximityIntersection::SPtr dummyMin;
 std::unique_ptr<native::MeshMinProximityIntersection> stockRigidMesh;
 void init()override {
  native::LocalMinDistance::init();
  dummyMin=sofa::core::objectmodel::New<native::MinProximityIntersection>();
  stockRigidMesh=std::make_unique<native::MeshMinProximityIntersection>(dummyMin.get(),false);
  // Stock helper signatures use currentIntersection->getAlarm/ContactDistance.
  // All sphere/point/line/triangle calculations are installed SDK functions.
  intersectors.add<RigidSphereModel,PointModel>(stockRigidMesh.get());
  intersectors.add<LineModel,RigidSphereModel>(stockRigidMesh.get());
  intersectors.add<TriangleModel,RigidSphereModel>(stockRigidMesh.get());
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripRigidSphereDispatch";}
__attribute__((visibility("default")))const char*getModuleVersion(){return "1.0";}
__attribute__((visibility("default")))const char*getModuleDescription(){return "Stock Min RigidSphere mesh function registration on stock Local;no new physics solver";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Native compatibility registration for experimentally missing Local RigidSphere mesh pairs").add<regrip::NativeRigidSphereLocalProximity>());}
}
