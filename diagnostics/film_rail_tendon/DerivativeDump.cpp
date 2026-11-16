#include "../../models/film_rail_tendon/Kernel.h"
#include <fstream>
#include <random>
#include <iostream>
using namespace regrip_film_rail;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("exclusive output");std::ifstream old(argv[1]);if(old)throw std::runtime_error("existing dump");std::ofstream out(argv[1],std::ios::binary);std::mt19937 random(42);std::uniform_real_distribution<double>noise(-.001,.001);unsigned count=0;
 for(unsigned nx:{5u,21u})for(double T:{0.,.0001,.001}){Assembly m(nx);auto rest=m.rest();std::vector<Point>u(m.size());for(unsigned i=0;i<u.size();++i)u[i]={noise(random),noise(random),.001*rest[i][0]*rest[i][0]+noise(random)};m.elements(u,T,[&](const Element&e){out.write(reinterpret_cast<const char*>(&e.energy.v),8);out.write(reinterpret_cast<const char*>(e.energy.g.data()),8*N);out.write(reinterpret_cast<const char*>(e.energy.h.data()),8*N*N);++count;});}
 if(!out)throw std::runtime_error("dump write");std::cout<<"PASS assembly derivative dump elements="<<count<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
