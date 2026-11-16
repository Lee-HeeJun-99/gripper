#include "../../models/film_shell/Kernel.h"
#include <fstream>
#include <random>
#include <iostream>
using namespace regrip_film;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("exclusive binary dump path");std::ifstream previous(argv[1]);if(previous)throw std::runtime_error("dump exists");std::ofstream out(argv[1],std::ios::binary);
 std::mt19937 generator(42);std::uniform_real_distribution<double>random(-.02,.02);unsigned count=0;
 for(unsigned nx:{5u,11u,21u})for(bool displacement:{false,true})for(bool compact:{false,true}){
  Film f(nx,5,100,24,{250,.3,.0610194155});auto x=f.rest();for(auto&p:x)for(auto&v:p)v+=random(generator);
  if(displacement){auto rest=f.rest();for(unsigned i=0;i<x.size();++i)x[i]=sub(x[i],rest[i]);}
  f.elements(x,[&](const auto&,const AD&e,bool){out.write(reinterpret_cast<const char*>(&e.v),sizeof(double));out.write(reinterpret_cast<const char*>(e.g.data()),sizeof(double)*N);out.write(reinterpret_cast<const char*>(e.h.data()),sizeof(double)*N*N);++count;},displacement,compact);
 }
 if(!out)throw std::runtime_error("dump write");std::cout<<"PASS derivative dump elements="<<count<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
