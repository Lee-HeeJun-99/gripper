#include "../../models/film_rail_tendon/Kernel.h"
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cstdint>
using namespace regrip_film_rail;
struct State{double time=0,T=0,U=0,K=0,length=200;std::vector<Point>u,v,gradient,tendon;};
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("binary synchronized state path");std::ifstream input(argv[1],std::ios::binary);std::uint64_t n=0,count=0;input.read(reinterpret_cast<char*>(&n),8);input.read(reinterpret_cast<char*>(&count),8);if(n%11||n>891||count>2001)throw std::invalid_argument("bounded energy input");Assembly model(n/11);auto masses=model.masses();State previous;bool first=true;
 std::cout<<std::setprecision(17)<<"time,U,K,delta_energy,tendon_path_work,tendon_force_work,elastic_quadrature_defect,damping_trapezoid,damping_discrete,damping_quadrature_defect,identity_residual\n";
 for(unsigned step=0;step<count;++step){State current;input.read(reinterpret_cast<char*>(&current.time),8);input.read(reinterpret_cast<char*>(&current.T),8);current.u.resize(n);current.v.resize(n);for(unsigned i=0;i<n;++i){input.read(reinterpret_cast<char*>(current.u[i].data()),24);input.read(reinterpret_cast<char*>(current.v[i].data()),24);}if(!input)throw std::runtime_error("truncated energy input");current.gradient.resize(n);current.tendon.resize(n);
  model.elements(current.u,current.T,[&](const Element&e){if(e.kind!=2)current.U+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){unsigned i=e.ids[a/3],j=a%3;if(e.kind==2)current.tendon[i][j]-=e.energy.g[a];else current.gradient[i][j]+=e.energy.g[a];}});
  for(unsigned i=0;i<n;++i)current.K+=.5*masses[i]*dot(current.v[i],current.v[i]);current.length=model.cableLength(current.u);
  if(first){previous=current;first=false;continue;}double h=current.time-previous.time;if(h<=0)throw std::runtime_error("ordered time");double elasticWork=0,tendonWork=0,D=0,Ddiscrete=0,Ddefect=0;
  for(unsigned i=0;i<n;++i){auto du=sub(current.u[i],previous.u[i]),dv=sub(current.v[i],previous.v[i]);elasticWork+=.5*dot(add(current.gradient[i],previous.gradient[i]),du);tendonWork+=.5*dot(add(current.tendon[i],previous.tendon[i]),du);D+=h*masses[i]*(dot(current.v[i],current.v[i])+dot(previous.v[i],previous.v[i]));Ddiscrete+=2*masses[i]*dot(du,du)/h;Ddefect+=.5*h*masses[i]*dot(dv,dv);}
  double delta=current.U+current.K-previous.U-previous.K,pathWork=-.5*(current.T+previous.T)*(current.length-previous.length),elasticDefect=elasticWork-(current.U-previous.U);
  double predicted=pathWork-D+(tendonWork-pathWork)-elasticDefect+Ddefect;
  std::cout<<current.time<<','<<current.U<<','<<current.K<<','<<delta<<','<<pathWork<<','<<tendonWork<<','<<elasticDefect<<','<<D<<','<<Ddiscrete<<','<<Ddefect<<','<<delta-predicted<<'\n';previous=std::move(current);
 }return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
