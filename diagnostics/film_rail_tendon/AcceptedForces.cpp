#include "../../models/film_rail_tendon/Kernel.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_film_rail;
int main(int argc,char**argv){try{if(argc!=3)throw std::invalid_argument("input exclusive_output");std::ifstream input(argv[1]),old(argv[2]);if(!input||old)throw std::runtime_error("input missing/output exists");std::ofstream out(argv[2]);out<<std::setprecision(17);unsigned nx,intervals,count;double offset,bond;input>>nx>>intervals>>offset>>bond>>count;Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;auto rest=model.rest();
 for(unsigned row=0;row<count;++row){double time,T;input>>time>>T;out<<time;std::vector<Point>state[2],linear(model.size());for(auto&q:state){q.resize(model.size());for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){input>>q[i][d];q[i][d]-=rest[i][d];}}if(!input)throw std::runtime_error("incomplete state");for(unsigned stage=0;stage<2;++stage){std::vector<Point>force(model.size());model.elements(state[stage],T,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){force[e.ids[a/3]][a%3]-=e.energy.g[a];if(stage==0)for(unsigned b=0;b<3*e.ids.size();++b)linear[e.ids[a/3]][a%3]-=e.energy.h[N*a+b]*(state[1][e.ids[b/3]][b%3]-state[0][e.ids[b/3]][b%3]);}});for(const auto&f:force)for(double value:f)out<<' '<<value;}for(const auto&f:linear)for(double value:f)out<<' '<<value;out<<'\n';}
 if(!out)throw std::runtime_error("force export");std::cout<<"PASS independent free/accepted force reconstruction;not momentum qualification\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
