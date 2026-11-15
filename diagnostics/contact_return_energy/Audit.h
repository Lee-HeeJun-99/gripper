#pragma once
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/behavior/ForceField.h>
struct ReturnInventory{
 double oldEnergy=0,newEnergy=0,endpointWork=0,plastic=0,projection=0,detachment=0,residual=0,maxPointResidual=0;
 unsigned active=0,born=0,dead=0,sliding=0;
};
extern "C" __attribute__((visibility("default"))) ReturnInventory auditCurveReturn(
 sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*);
