#pragma once
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/behavior/ForceField.h>
#include <istream>
#include <ostream>
#include <stdexcept>
#include <cmath>
using CheckpointTypes=sofa::defaulttype::Rigid3Types;
using CheckpointFF=sofa::core::behavior::ForceField<CheckpointTypes>;
inline void need(bool value,const char*why){if(!value)throw std::runtime_error(why);}
inline double scalar(std::istream&in){double v;need(bool(in>>v)&&std::isfinite(v),"nonfinite/corrupt checkpoint scalar");return v;}
extern "C" {
__attribute__((visibility("default"))) void writeCurveState(CheckpointFF*,std::ostream&);
__attribute__((visibility("default"))) void readCurveState(CheckpointFF*,std::istream&);
__attribute__((visibility("default"))) void writeFrameState(CheckpointFF*,std::ostream&);
__attribute__((visibility("default"))) void readFrameState(CheckpointFF*,std::istream&);
__attribute__((visibility("default"))) void writeCableState(CheckpointFF*,std::ostream&);
__attribute__((visibility("default"))) void readCableState(CheckpointFF*,std::istream&);
__attribute__((visibility("default"))) unsigned curveCheckpointSteps(CheckpointFF*);
}
