#pragma once
namespace regrip_compensated {
inline double update(double before,double roundedAfter,long double increment,long double&carry){
 carry+=static_cast<long double>(before)-static_cast<long double>(roundedAfter)+increment;
 double result=static_cast<double>(static_cast<long double>(roundedAfter)+carry);
 carry-=static_cast<long double>(result)-static_cast<long double>(roundedAfter);
 return result;
}
}
