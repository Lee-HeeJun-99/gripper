#include <sofa/core/ObjectFactory.h>
namespace tangential_v110 { void registerTangentialRigidForceField(sofa::core::ObjectFactory*); }
extern "C" {
#ifdef _WIN32
#define V110_EXPORT __declspec(dllexport)
#else
#define V110_EXPORT __attribute__((visibility("default")))
#endif
V110_EXPORT void initExternalModule() {}
V110_EXPORT const char* getModuleName() {return "SofaTangentialV110";}
V110_EXPORT const char* getModuleVersion() {return "1.1.0";}
V110_EXPORT const char* getModuleLicense() {return "MIT (original prototype source)";}
V110_EXPORT const char* getModuleDescription() {return "Small angle tangential bilayer shear ForceField";}
V110_EXPORT const char* getModuleComponentList() {return "TangentialRigidForceField";}
V110_EXPORT void registerObjects(sofa::core::ObjectFactory* f) {
    tangential_v110::registerTangentialRigidForceField(f);
}
}
