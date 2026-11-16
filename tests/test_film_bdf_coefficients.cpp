#include "../models/film_shell/BDFCoefficients.h"
#include <iostream>
int main(){try{
 for(double ratio:{.25,.5,1.,2.}){double h=.01,previous=h/ratio,t=.4;auto a=regrip_film::bdf2Coefficients(h,previous);auto derivative=[&](int degree){return (a[0]*std::pow(t-h-previous,degree)+a[1]*std::pow(t-h,degree)+a[2]*std::pow(t,degree))/h;};if(std::abs(derivative(0))>1e-12||std::abs(derivative(1)-1)>1e-12||std::abs(derivative(2)-2*t)>1e-12)throw std::runtime_error("variable BDF2 polynomial exactness");}
 bool rejected=false;try{regrip_film::bdf2Coefficients(.1,.01);}catch(const std::invalid_argument&){rejected=true;}if(!rejected)throw std::runtime_error("unstable growth not rejected");
 std::cout<<"PASS variable BDF2 coefficients;constant/linear/quadratic exactness and growth guard\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
