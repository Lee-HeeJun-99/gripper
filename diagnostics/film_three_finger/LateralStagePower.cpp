#include "../../models/film_lateral_tendon/Step.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_lateral_tendon;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("public mass,actual stages,output required");auto m=model();auto mass=publicMass(argv[1]);std::ifstream in(argv[2]);unsigned count;in>>count;if(!in||!count||count>3000)throw std::runtime_error("bounded actual stage count");std::ofstream out(argv[3]);out<<std::setprecision(17)<<"macro,time_s,weight_s,T_N,tendon_power_Nmm_s,damping_power_Nmm_s,length_mm\n";
 for(unsigned k=0;k<count;++k){unsigned macro;double t,w,T;in>>macro>>t>>w>>T;std::vector<Point>q(m.size()),v(m.size());for(auto&p:q)for(double&x:p)in>>x;for(auto&p:v)for(double&x:p)in>>x;if(!in||T!=holdControl().sample(t).tension||!(w>0))throw std::runtime_error("actual stage input/control differs");long double power=0,damping=0;
  double L=route(m,q,T,6,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)power-=static_cast<long double>(e.energy.g[a])*v[e.ids[a/3]][a%3];});
  for(unsigned i=0;i<v.size();++i)for(unsigned d=0;d<3;++d)damping+=2*static_cast<long double>(mass[i])*v[i][d]*v[i][d];
  out<<macro<<','<<t<<','<<w<<','<<T<<','<<power<<','<<damping<<','<<L<<'\n';out.flush();
 }std::string extra;if(in>>extra)throw std::runtime_error("unexpected stage payload");std::cout<<"PASS actual-stage geometric tendon power;NOT full system energy\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
