#pragma once
#include <array>
#include <vector>
namespace regrip_value_energy {
struct Parameters {unsigned nx=21,guideIntervals=4;double guideOffset=5,bondK=.001;bool rootGuideSecondOrder=false;};
// Baseline rectangular Assembly only,not arbitrary material/shape fitting.
std::array<double,2> evaluate(const Parameters&,const std::vector<std::array<double,3>>&displacement);
}
