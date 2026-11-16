#include "../../models/general_vector_history/SphereEventReturn.h"
#include <iostream>
#include <iomanip>
using namespace regrip_history;
int main(int argc,char**argv){try{unsigned subdivisions=argc==2?std::stoul(argv[1]):32;std::cout<<std::setprecision(17)<<"steps,time,plastic,stored\n";
 for(unsigned steps:{20u,40u,80u}){V previous{0,1.021,0},e{};double D=0;
 for(unsigned i=1;i<=steps;++i){double t=.02*i/steps;V point{.2*t,1.021-.2*t,.1*t};
 auto r=regrip_general_history::sphereEventReturn(previous,e,constantV<First>(point),1.02,.001,.0003,subdivisions);
 D+=r.plasticLoss.v;for(int j=0;j<3;++j)e[j]=r.elastic[j].v;previous=point;
 std::cout<<steps<<','<<t<<','<<D<<','<<r.storedEnergy.v<<'\n';}}
 return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
