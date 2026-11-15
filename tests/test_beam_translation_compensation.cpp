#include "../models/stabilization/Compensated.h"
#include <iostream>
#include <cmath>
#include <limits>
int main(){
 double ordinary=100,compensated=100;long double carry=0,increment=1e-15L;unsigned n=100000;
 for(unsigned i=0;i<n;++i){ordinary+=double(increment);double next=compensated+double(increment);compensated=regrip_compensated::update(compensated,next,increment,carry);}
 long double expected=100.L+n*increment;
 double ulp=std::nextafter(compensated,INFINITY)-compensated;
 bool pass=ordinary==100&&std::abs(static_cast<long double>(compensated)-expected)<=.5L*ulp&&std::abs(carry)<=.5L*ulp;
 std::cout<<"arithmetic "<<(pass?"PASS":"FAIL")<<" steps="<<n<<" ordinary_error="<<double(std::abs(ordinary-expected))<<" compensated_error="<<double(std::abs(compensated-expected))<<" carry="<<double(carry)<<'\n';return pass?0:1;
}
