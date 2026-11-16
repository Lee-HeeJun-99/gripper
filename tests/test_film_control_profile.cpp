#include "../models/film_rail_tendon/ControlProfile.h"
#include <cstring>
#include <iostream>
using regrip_film_rail::ControlProfile;
int main(){try{
 constexpr double T=.001,r=4,b=6,e=8;
 for(double t:{0.,r,b,e}){auto s=ControlProfile::evaluate(t,T,r,b,e,true);if(s.rate!=0||s.acceleration!=0)throw std::runtime_error("C2 endpoint derivatives");}
 for(int i=-100;i<1000;++i){double t=i*.01;auto q=ControlProfile::evaluate(t,T,r,b,e,true);double legacy=T*std::clamp(t/r,0.,1.)*(t<=b?1.:std::clamp((e-t)/(e-b),0.,1.));auto old=ControlProfile::evaluate(t,T,r,b,e,false);if(std::memcmp(&legacy,&old.tension,sizeof(double)))throw std::runtime_error("legacy tension bits changed");if(q.tension<0||q.tension>T)throw std::runtime_error("C2 bounded tension");if(t>0&&t<e&&t!=r&&t!=b){double h=1e-5;auto lo=ControlProfile::evaluate(t-h,T,r,b,e,true),hi=ControlProfile::evaluate(t+h,T,r,b,e,true);if(std::abs((hi.tension-lo.tension)/(2*h)-q.rate)>1e-11||std::abs((hi.rate-lo.rate)/(2*h)-q.acceleration)>1e-10)throw std::runtime_error("C2 analytical derivative FD");}}
 bool reject=false;try{ControlProfile::evaluate(1,T,4,3,8,true);}catch(const std::invalid_argument&){reject=true;}if(!reject)throw std::runtime_error("invalid schedule accepted");
 std::cout<<"PASS C2 knots,bounds,derivative FD,legacy value bit identity;NOT dynamics convergence\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
