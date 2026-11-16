#pragma once
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace regrip_film_rail {
// Prescribed research tension, not a model of motor efficiency or vacuum work.
struct ControlProfile {
 struct Sample { double tension,rate,acceleration; };
 static Sample evaluate(double time,double maximum,double ramp,double release,double end,bool c2){
  if(!std::isfinite(time)||!std::isfinite(maximum)||!std::isfinite(ramp)||!std::isfinite(release)||!std::isfinite(end)||maximum<0||maximum>.1||ramp<=0||release<ramp||end<=release)throw std::invalid_argument("bounded finite research tension schedule");
  if(!c2){
   // Preserve original floating-point evaluation order for legacy force values.
   double value=maximum*std::clamp(time/ramp,0.,1.)*(time<=release?1.:std::clamp((end-time)/(end-release),0.,1.));
   double rate=(time>0&&time<ramp)?maximum/ramp:(time>release&&time<end)?-maximum/(end-release):0;
   return {value,rate,0}; // derivative at legacy knots is not unique
  }
  if(time<=0||time>=end)return {0,0,0};
  if(time>=ramp&&time<=release)return {maximum,0,0};
  bool closing=time<ramp;double duration=closing?ramp:end-release;
  double x=closing?time/ramp:(time-release)/duration;
  double s=x*x*x*(10+x*(-15+6*x));
  double ds=30*x*x*(1-x)*(1-x),dds=60*x*(1-x)*(1-2*x);
  return {maximum*(closing?s:1-s),(closing?1:-1)*maximum*ds/duration,(closing?1:-1)*maximum*dds/(duration*duration)};
 }
};
}
