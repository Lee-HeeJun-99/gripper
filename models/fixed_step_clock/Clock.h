#pragma once
#include <cmath>
#include <limits>
#include <stdexcept>
#include <algorithm>
namespace regrip_clock {
inline double timeAt(double origin,double h,unsigned step){
 if(!std::isfinite(origin)||!std::isfinite(h)||h<=0||step>240000)throw std::invalid_argument("bounded fixed-step clock");
 return static_cast<double>(static_cast<long double>(origin)+static_cast<long double>(step)*h);
}
inline double accumulationBound(double origin,double h,unsigned step){
 double u=std::numeric_limits<double>::epsilon(),gamma=step*u/(1-step*u),target=timeAt(origin,h,step);
 return 4*gamma*std::abs(target-origin)+8*u*std::max(1.,std::max(std::abs(origin),std::abs(target)));
}
}
