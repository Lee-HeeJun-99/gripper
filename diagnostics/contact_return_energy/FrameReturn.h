#pragma once
#include "Audit.h"
struct FrameReturnInventory{
 double oldEnergy=0,newEnergy=0,endpointWork=0,plastic=0,projection=0,residual=0;
};
extern "C" __attribute__((visibility("default"))) FrameReturnInventory auditFrameReturn(
 sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*,
 const sofa::defaulttype::Rigid3Types::VecCoord&);
// Exact public assembly of the UNCHANGED frozen FrameLayerNetwork,not an
// alternative constitutive implementation or a different dynamic class.
using FrameAssemblySnapshot=NormalInventory;
extern "C" __attribute__((visibility("default"))) FrameAssemblySnapshot snapshotFrameAssembly(
 sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*,
 const sofa::defaulttype::Rigid3Types::VecCoord&);
using CableAssemblySnapshot=NormalInventory;
extern "C" __attribute__((visibility("default"))) CableAssemblySnapshot snapshotCableAssembly(
 sofa::core::behavior::ForceField<sofa::defaulttype::Rigid3Types>*,
 const sofa::defaulttype::Rigid3Types::VecCoord&);
