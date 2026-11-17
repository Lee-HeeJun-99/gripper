#pragma once
#include "../film_sphere_contact/ClosestPrimitive.h"
#include <optional>
namespace regrip_film_impact {
// Continuous geometry on an explicitly affine nodal trajectory. It is NOT
// claimed to be the continuous solution of the film ODE or a BDF dense output.
struct PrimitiveBirth {
 double fraction,gap,pathDerivative;unsigned feature,evaluations;
};
inline std::optional<PrimitiveBirth> primitiveBirth(
 const std::vector<regrip_film_rail::Point>&start,
 const std::vector<regrip_film_rail::Point>&increment,
 regrip_film_rail::Point center,double radius,double gapTolerance=1e-10){
 using namespace regrip_film_rail;using regrip_film_sphere::ClosestPrimitive;
 if(start.size()!=increment.size()||start.empty()||start.size()>3||
    !std::isfinite(radius)||radius<=0||!std::isfinite(gapTolerance)||gapTolerance<=0)
  throw std::invalid_argument("affine primitive path input");
 double speed=0;for(unsigned i=0;i<start.size();++i){for(unsigned d=0;d<3;++d)
  if(!std::isfinite(start[i][d])||!std::isfinite(increment[i][d])||!std::isfinite(center[d]))throw std::invalid_argument("nonfinite primitive path");
  speed=std::max(speed,std::sqrt(dot(increment[i],increment[i])));}
 unsigned count=0;
 auto evaluate=[&](double alpha){auto p=start;for(unsigned i=0;i<p.size();++i)p[i]=add(p[i],scale(increment[i],alpha));++count;return ClosestPrimitive::evaluate(p,center,radius);};
 auto derivative=[&](const ClosestPrimitive::Evaluation&e){double rate=0;for(unsigned a=0;a<3*start.size();++a)rate+=e.gap.g[a]*increment[a/3][a%3];return rate;};
 double alpha=0;auto current=evaluate(alpha);
 if(current.gap.v<0)throw std::domain_error("initial overlap is not a primitive birth");
 if(speed==0)return std::nullopt;
 // Hausdorff motion of affine convex supports is <= max nodal displacement.
 // g(alpha)/speed is therefore a certified empty interval (up to roundoff).
 for(unsigned iteration=0;iteration<128;++iteration){
  double g=current.gap.v,rate=derivative(current);
  if(g==0){if(rate>=0)throw std::domain_error("initial/tangent/departing event needs separate active-contact handling");return PrimitiveBirth{alpha,g,rate,current.feature,count};}
  if(g/speed>1-alpha)return std::nullopt;
  if(g<=gapTolerance&&rate<0){
   double upper=std::min(1.,alpha+2*g/(-rate));
   if(upper>alpha){auto end=evaluate(upper);
    if(end.gap.v<=0){double lo=alpha,hi=upper;auto right=end;
     for(unsigned j=0;j<64;++j){double mid=(lo+hi)/2;if(mid==lo||mid==hi)break;
      auto value=evaluate(mid);if(value.gap.v>0)lo=mid;else{hi=mid;right=value;}}
     double slope=derivative(right);if(slope>=0)throw std::domain_error("nontransversal primitive root");
     if(std::abs(right.gap.v)>gapTolerance)throw std::runtime_error("primitive root failed gap gate");
     return PrimitiveBirth{hi,right.gap.v,slope,right.feature,count};
    }
   }
  }
  double next=std::min(1.,alpha+g/speed);
  if(next<=alpha)throw std::runtime_error("unresolved grazing/roundoff event;no denominator regularization");
  alpha=next;current=evaluate(alpha);
 }
 throw std::runtime_error("primitive event search budget128;not OS exhaustion");
}
}
