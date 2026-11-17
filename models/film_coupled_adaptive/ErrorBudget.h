#pragma once
#include <cmath>
#include <stdexcept>
namespace regrip_coupled_adaptive {
// Defect BOOKKEEPING,not a theorem of nonlinear stability/global accuracy.
// At most M event-bearing intervals share half the total defect budget;
// all smooth intervals share the other half in proportion to physical h/H.
// Sum(tol*h_i/(2H)) + k*tol/(2M) <= tol for k<=M and sum h_i<=H.
// A discrete atom is not repeated H/h times as a distributed truncation term.
inline double defectWeight(double horizon,double h,bool event,unsigned maximumEvents){
 if(!(h>0&&h<=horizon)||!std::isfinite(h+horizon)||maximumEvents==0||maximumEvents>16)throw std::invalid_argument("bounded event/smooth defect allocation");
 return event?2.*maximumEvents:2*horizon/h;
}
}
