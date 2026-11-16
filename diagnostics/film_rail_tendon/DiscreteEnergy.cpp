#include "../../models/film_rail_tendon/Kernel.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_film_rail;
int main(int argc,char**argv){try{if(argc!=3)throw std::invalid_argument("input exclusive_output");std::ifstream in(argv[1]),old(argv[2]);if(!in||old)throw std::runtime_error("input/output");unsigned nx,intervals,count;double offset,bond;in>>nx>>intervals>>offset>>bond>>count;Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;auto rest=model.rest();std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,U0,U1,L0,L1,stored_gradient_dot_delta_q,tendon_gradient_dot_delta_q\n";
 for(unsigned k=0;k<count;++k){double t,T;in>>t>>T;std::vector<Point>q[2];for(auto&state:q){state.resize(model.size());for(unsigned i=0;i<state.size();++i)for(unsigned d=0;d<3;++d){in>>state[i][d];state[i][d]-=rest[i][d];}}if(!in)throw std::runtime_error("truncated input");double U0=0,U1=0,stored=0,tendon=0;model.elements(q[0],0,[&](const Element&e){if(e.kind<2)U0+=e.energy.v;});model.elements(q[1],T,[&](const Element&e){if(e.kind<2)U1+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){double value=e.energy.g[a]*(q[1][e.ids[a/3]][a%3]-q[0][e.ids[a/3]][a%3]);if(e.kind<2)stored+=value;else if(e.kind==2)tendon+=value;}});out<<t<<','<<U0<<','<<U1<<','<<model.cableLength(q[0])<<','<<model.cableLength(q[1])<<','<<stored<<','<<tendon<<'\n';}
 std::cout<<"PASS independent BE discrete energy terms;not whole physical energy certification\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
