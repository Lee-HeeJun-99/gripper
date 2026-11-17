#include "../models/film_impact/SurfaceEvent.h"
#include <iostream>
using namespace regrip_film_impact;
int main(){try{unsigned recovered=0;double maximum=0;
 for(unsigned k=1;k<=256;++k){double z=1+7e-6*(1+k/257.),v=-2e-5*(1+k/701.),c=-3e-8*(1+k/503.);QuadraticSurfacePath path{{{-2,-2,z},{2,-2,z},{0,2,z}},{{0,0,v},{0,0,v},{0,0,v}},{{0,0,c},{0,0,c},{0,0,c}}};auto event=earliestSurfaceEvent(path,{{0,1,2}},{0,0,0},1);if(!event)throw std::runtime_error("missing monotone face event");long double d=static_cast<long double>(z)-1,lv=v,lc=c;long double reference=2*d/(-lv+std::sqrt(lv*lv-4*lc*d));double error=std::abs(event->fraction-static_cast<double>(reference));maximum=std::max(maximum,error);if(error>1e-10||event->clearUntil>event->fraction||event->rows.empty())throw std::runtime_error("signed bracket/root accuracy");recovered+=event->bracketRecovered;}
 std::cout<<"PASS 256 monotone quadratic face paths;negative-gap bracket recoveries "<<recovered<<" max fraction error "<<maximum<<";adaptive614 provides captured negative-ULP regression\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
