#pragma once
#include <cmath>
#include <stdexcept>
namespace regrip_film_impact {
// Eligibility transaction only: the integrator still has to integrate the
// event and remaining interval. No velocity or position is silently corrected.
class RestartHistory {
 double previousStep=0;bool eligible=false;
public:
 void impact(){eligible=false;previousStep=0;}
 bool useBDF2(double h)const{
  if(!std::isfinite(h)||h<=0)throw std::invalid_argument("restart step");
  return eligible&&h==previousStep;
 }
 void acceptSmoothStep(double h){
  if(!std::isfinite(h)||h<=0)throw std::invalid_argument("accepted step");
  previousStep=h;eligible=true;
 }
};
}
