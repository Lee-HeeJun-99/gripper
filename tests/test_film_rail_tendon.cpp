#include "../models/film_rail_tendon/Kernel.h"
#include <iostream>
using namespace regrip_film_rail;
int main(){try{
 Assembly model;std::vector<Point>u(model.size());auto rest=model.rest();double tension=.001;
 if(std::abs(model.volume()-439.3397917746089/3)>1e-12||std::abs(model.energy(u,0))>1e-20)throw std::runtime_error("rest/volume");
 double mass=0;for(auto m:model.masses())mass+=m;if(std::abs(mass-1e-6)>1e-20)throw std::runtime_error("mass");
 for(unsigned i=0;i<u.size();++i){u[i]={.0001*rest[i][0],.00001*rest[i][1],.00001*rest[i][0]*rest[i][0]};}
 const unsigned nd=3*u.size();std::vector<double>g(nd),H(nd*nd);double energy=0;
 model.elements(u,tension,[&](const Element&e){energy+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){unsigned i=3*e.ids[a/3]+a%3;g[i]+=e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b)H[i*nd+3*e.ids[b/3]+b%3]+=e.energy.h[N*a+b];}});
 double forceError=0,hessianError=0;
 for(unsigned j:{3*model.id(0,5,0)+2,3*model.id(1,5,0)+2,3*model.id(2,10,2)}){auto plus=u,minus=u;double h=1e-6;plus[j/3][j%3]+=h;minus[j/3][j%3]-=h;
  forceError=std::max(forceError,std::abs((model.energy(plus,tension)-model.energy(minus,tension))/(2*h)-g[j]));std::vector<double>gp(nd),gm(nd);
  model.elements(plus,tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)gp[3*e.ids[a/3]+a%3]+=e.energy.g[a];});model.elements(minus,tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)gm[3*e.ids[a/3]+a%3]+=e.energy.g[a];});
  for(unsigned i=0;i<nd;++i)hessianError=std::max(hessianError,std::abs((gp[i]-gm[i])/(2*h)-H[i*nd+j]));
 }
 auto transformed=u;double angle=.7;Point F{},M{};for(unsigned i=0;i<u.size();++i){auto x=add(rest[i],u[i]);Point force{-g[3*i],-g[3*i+1],-g[3*i+2]};F=add(F,force);M=add(M,cross(x,force));Point rotated{std::cos(angle)*x[0]+std::sin(angle)*x[2]+2,x[1]-3,-std::sin(angle)*x[0]+std::cos(angle)*x[2]+1};transformed[i]=sub(rotated,rest[i]);}
 double objective=std::abs(model.energy(transformed,tension)-energy);
 if(forceError>1e-8||hessianError>1e-5||objective>1e-10||std::sqrt(dot(F,F))>1e-10||std::sqrt(dot(M,M))>1e-9)throw std::runtime_error("assembly FD/objectivity/wrench");
 std::cout<<"PASS independent shell/rail/attachment/eccentric-tendon kernel;forceFD="<<forceError<<" HessianFD="<<hessianError<<" objectivity="<<objective<<" volume="<<model.volume()<<" railWidth="<<model.railW<<";NOT SOFA/grasp qualification\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
