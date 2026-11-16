#pragma once
#include <array>
#include <cmath>
#include <stdexcept>
namespace regrip_film {
inline std::array<double,3>bdf2Coefficients(double h,double previous){
 if(!std::isfinite(h+previous)||h<=0||previous<=0)throw std::invalid_argument("positive finite BDF2 steps");
 double r=h/previous;
 if(r>=1+std::sqrt(2.))throw std::invalid_argument("BDF2 step growth exceeds zero-stability ratio bound");
 return {r*r/(1+r),-(1+r),(1+2*r)/(1+r)};
}
}
