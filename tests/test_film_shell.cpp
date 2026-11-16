#include "../models/film_shell/Kernel.h"
#include <iostream>
using namespace regrip_film;
int main(){try{
 Film f(5,3,10,4,{250,.3,.1});auto rest=f.rest(),x=rest;for(auto&p:x){p[0]*=1.01;p[2]=.002*p[0]*p[0]+.001*p[0]*p[1];}
 double E=0;std::vector<double>g(x.size()*3),H(g.size()*g.size());f.elements(x,[&](const auto&ids,const AD&e,bool){E+=e.v;for(unsigned i=0;i<3*ids.size();++i){unsigned a=3*ids[i/3]+i%3;g[a]+=e.g[i];for(unsigned j=0;j<3*ids.size();++j)H[a*g.size()+3*ids[j/3]+j%3]+=e.h[N*i+j];}});
 double fd=0,hess=0;for(unsigned j:{0u,13u,25u,43u}){auto p=x,m=x;p[j/3][j%3]+=1e-6;m[j/3][j%3]-=1e-6;fd=std::max(fd,std::abs((f.energy(p)-f.energy(m))/2e-6-g[j]));std::vector<double>gp(g.size()),gm(g.size());auto collect=[](auto&target,const auto&ids,const AD&e){for(unsigned i=0;i<3*ids.size();++i)target[3*ids[i/3]+i%3]+=e.g[i];};f.elements(p,[&](auto&ids,const AD&e,bool){collect(gp,ids,e);});f.elements(m,[&](auto&ids,const AD&e,bool){collect(gm,ids,e);});for(unsigned i=0;i<g.size();++i)hess=std::max(hess,std::abs((gp[i]-gm[i])/2e-6-H[i*g.size()+j]));}
 auto q=x;double angle=.7;for(auto&p:q){double a=p[0],b=p[2];p={std::cos(angle)*a+std::sin(angle)*b+2,p[1]-3,-std::sin(angle)*a+std::cos(angle)*b+1};}
 double obj=std::abs(f.energy(q)-E),force=0,moment=0;Point F{},M{};for(unsigned i=0;i<x.size();++i){Point fi{-g[3*i],-g[3*i+1],-g[3*i+2]};F=add(F,fi);M=add(M,cross(x[i],fi));}for(int j=0;j<3;++j){force=std::max(force,std::abs(F[j]));moment=std::max(moment,std::abs(M[j]));}
 auto membrane=rest;for(auto&p:membrane){p[0]*=1.01;p[1]*=1.01;}double strain=(1.01*1.01-1)/2,reference=250*.1*10*4/(1-.3)*strain*strain;
 if(fd>1e-6||hess>1e-5||obj>1e-12||force>1e-10||moment>1e-10||std::abs(f.energy(membrane)-reference)>1e-12)throw std::runtime_error("film derivative/objectivity/membrane/balance");
 auto u=x;for(unsigned i=0;i<u.size();++i)u[i]=sub(u[i],rest[i]);double displacementEnergy=0;f.elements(u,[&](const auto&,const AD&a,bool){displacementEnergy+=a.v;},true);if(std::abs(E-displacementEnergy)>1e-13)throw std::runtime_error("position/displacement formulation identity");
 for(unsigned i=0;i<u.size();++i)u[i]={1e-12*rest[i][0],0,0};double tiny=0;f.elements(u,[&](const auto&,const AD&a,bool){tiny+=a.v;},true);double tinyReference=.5*250*.1*40/(1-.3*.3)*std::pow(1e-12+.5e-24,2);if(std::abs(tiny-tinyReference)/tinyReference>1e-12)throw std::runtime_error("tiny strain displacement reference");
 std::cout<<"PASS force_fd="<<fd<<" Hessian_fd="<<hess<<" objectivity="<<obj<<" force_sum="<<force<<" moment_sum="<<moment<<" membrane_reference="<<reference<<'\n';
 for(unsigned n:{5u,9u,17u}){Film plate(n,n,10,4,{250,.3,.1});auto p=plate.rest();for(auto&a:p)a[2]=.0001*(a[0]*a[0]+.3*a[1]*a[1]+.2*a[0]*a[1]);double bending=0;plate.elements(p,[&](const auto&,const AD&e,bool bend){if(bend)bending+=e.v;});double exact=.5*plate.material.D()*40*(4e-8+.36e-8+2*.3*1.2e-8+2*.7*.04e-8);std::cout<<"plate n="<<n<<" bending="<<bending<<" linear_KL="<<exact<<" relative="<<std::abs(bending-exact)/exact<<'\n';}
 return 0;}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
