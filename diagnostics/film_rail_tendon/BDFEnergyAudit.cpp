#include "../../models/film_rail_tendon/Kernel.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cstdint>
using namespace regrip_film_rail;
struct State{double time=0,T=0,U=0,K=0,length=200;std::vector<Point>u,v,g,ft;};
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("uniform-step accepted states");std::ifstream in(argv[1],std::ios::binary);std::uint64_t n=0,count=0;in.read(reinterpret_cast<char*>(&n),8);in.read(reinterpret_cast<char*>(&count),8);if(n!=231||count>6401)throw std::invalid_argument("bounded assembly energy states");Assembly model(n/11);auto mass=model.masses();State previous,older;double oldh=0;
 std::cout<<std::setprecision(17)<<"time,U,K,delta_energy,tendon_path_work,tendon_endpoint_work,elastic_quadrature_defect,damping_endpoint,bdf_difference_loss,g_inventory_change,identity_residual\n";
 for(unsigned step=0;step<count;++step){State current;in.read(reinterpret_cast<char*>(&current.time),8);in.read(reinterpret_cast<char*>(&current.T),8);current.u.resize(n);current.v.resize(n);current.g.resize(n);current.ft.resize(n);for(unsigned i=0;i<n;++i){in.read(reinterpret_cast<char*>(current.u[i].data()),24);in.read(reinterpret_cast<char*>(current.v[i].data()),24);}if(!in)throw std::runtime_error("truncated state");
  model.elements(current.u,current.T,[&](const Element&e){if(e.kind!=2)current.U+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){auto i=e.ids[a/3],j=a%3;if(e.kind==2)current.ft[i][j]-=e.energy.g[a];else current.g[i][j]+=e.energy.g[a];}});current.length=model.cableLength(current.u);for(unsigned i=0;i<n;++i)current.K+=.5*mass[i]*dot(current.v[i],current.v[i]);
  if(!step){previous=current;continue;}double h=current.time-previous.time;if(h<=0||(step>1&&std::abs(h-oldh)>1e-10*h))throw std::runtime_error("uniform positive dt required");oldh=h;double W=0,Q=0,D=0,loss=0,inventory=0;
  for(unsigned i=0;i<n;++i){auto v=current.v[i],p=previous.v[i];W+=h*dot(current.ft[i],v);Q+=h*dot(current.g[i],v);D+=2*h*mass[i]*dot(v,v);
   if(step==1){auto dv=sub(v,p);loss+=.5*mass[i]*dot(dv,dv);}else{auto o=older.v[i],cv=sub(scale(v,2.),p),pv=sub(scale(p,2.),o),dd=add(sub(v,scale(p,2.)),o);loss+=.25*mass[i]*dot(dd,dd);inventory+=.25*mass[i]*(dot(cv,cv)-dot(v,v)-dot(pv,pv)+dot(p,p));}}
  Q-=current.U-previous.U;double path=-.5*(current.T+previous.T)*(current.length-previous.length),delta=current.K+current.U-previous.K-previous.U;double predicted=path-D+(W-path)-Q-loss-inventory;
  std::cout<<current.time<<','<<current.U<<','<<current.K<<','<<delta<<','<<path<<','<<W<<','<<Q<<','<<D<<','<<loss<<','<<inventory<<','<<delta-predicted<<'\n';older=std::move(previous);previous=std::move(current);
 }return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
