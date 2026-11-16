#pragma once
#include "CoupledContactStep.h"
namespace regrip_film_native {
// Uniform-step BDF2 recast as the SAME implicit kernel, not a fitted force.
// Dq=v, M Dv+c Mv-F=J^T lambda/h; beta=2/3.
// q*= (4qn-q[n-1])/3, v*= (4vn-v[n-1])/3, h*=beta h.
// The kernel multiplier is beta times the physical-step impulse.
struct CoupledBDFHistory {
 static constexpr double beta=2./3.;
 static std::vector<Point> extrapolate(const std::vector<Point>&current,const std::vector<Point>&old){
  if(current.size()!=old.size())throw std::invalid_argument("BDF2 history size");
  auto result=current;for(unsigned i=0;i<current.size();++i)for(unsigned d=0;d<3;++d)result[i][d]=(4*current[i][d]-old[i][d])/3;
  return result;
 }
};
}
