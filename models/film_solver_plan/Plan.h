#pragma once
#include <cmath>
#include <stdexcept>
namespace regrip_solver_plan {
struct Plan{unsigned microsteps;double newtonTolerance;bool startup;};
// Explicit bounded numerical candidate, NOT a physical tolerance waiver.
// Control is always evaluated at the accumulated stage clock. The index only
// selects the declared plan; no clock/state/history is overwritten at transition.
inline Plan select(unsigned completed,unsigned steps,double time,double h){
 if((steps!=40&&steps!=80&&steps!=160)||completed>=steps||!(h>0&&h<=.000025000000000001)||time<0||time+h>.001000000000000001||std::abs(time-completed*(.001/steps))>1e-15)throw std::runtime_error("bounded1ms plan clock/index mismatch");
 bool early=completed<steps/5;return {early?8u:1u,early?1e-24:1e-22,early};
}
}
