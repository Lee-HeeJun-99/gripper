#include "../models/film_shell/Kernel.h"
#include <iostream>
#include <random>
using namespace regrip_film;
int main(){try{
 std::mt19937 generator(42);std::uniform_real_distribution<double>random(-.02,.02);unsigned checked=0;
 for(unsigned nx:{5u,11u,21u})for(bool displacement:{false,true}){
  Film f(nx,5,100,24,{250,.3,.0610194155});auto x=f.rest();for(auto&p:x)for(auto&v:p)v+=random(generator);
  if(displacement){auto r=f.rest();for(unsigned i=0;i<x.size();++i)x[i]=sub(x[i],r[i]);}
  std::vector<AD>reference;f.elements(x,[&](const auto&,const AD&e,bool){reference.push_back(e);},displacement,false);
  unsigned index=0;f.elements(x,[&](const auto&,const AD&e,bool){const auto&r=reference.at(index++);if(e.v!=r.v||e.g!=r.g||e.h!=r.h||e.constant!=r.constant)throw std::runtime_error("compact AD2 not bitwise equivalent");++checked;},displacement,true);
 }
 std::cout<<"PASS bitwise element energy/gradient/Hessian equivalence; elements="<<checked<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
