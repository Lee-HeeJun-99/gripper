#include "../models/yield_front_history/VectorReturn.h"
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <random>
using namespace regrip_vector_history;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
V rotate(V v){const R a=.73L,c=std::cos(a),s=std::sin(a);return {c*v[0]-s*v[2],v[1],s*v[0]+c*v[2]};}
int main(){try{
 std::mt19937 rng(12951);std::uniform_real_distribution<double>d(-1,1);
 R maxFD=0,maxEnergy=0,maxCov=0,maxCone=0;
 for(int t=0;t<600;++t){
  R k=.7L,cap=t%17==0?0:.003L;V n{0,0,1},old{R(d(rng))*.003L,R(d(rng))*.003L,0},du{R(d(rng))*.01L,R(d(rng))*.01L,0};
  auto r=radialReturn(old,du,n,k,cap);
  maxEnergy=std::max(maxEnergy,std::abs(r.energy-r.oldEnergy-r.work+r.loss+r.projection));
  maxCone=std::max(maxCone,std::max(0.L,norm(r.traction)-cap));
  require(r.loss>=0,"negative plastic loss");
  auto cov=radialReturn(rotate(old),rotate(du),rotate(n),k,cap);
  maxCov=std::max({maxCov,norm(add(cov.traction,scale(rotate(r.traction),-1))),std::abs(cov.loss-r.loss)});
  for(int j=0;j<2;++j){R h=1e-8L;V p=du,m=du;p[j]+=h;m[j]-=h;
   auto rp=radialReturn(old,p,n,k,cap),rm=radialReturn(old,m,n,k,cap);
   for(int i=0;i<3;++i)maxFD=std::max(maxFD,std::abs((rp.traction[i]-rm.traction[i])/(2*h)-r.classicalTangent()[3*i+j]));
   // Incremental potential U(return)+C|plastic|, NOT stored energy alone.
   R grad=(rp.energy+rp.loss-rm.energy-rm.loss)/(2*h);
   require(std::abs(grad-r.traction[j])<2e-11L,"incremental potential gradient");
  }
 }
 auto diag=radialReturn({},V{1,1,0},V{0,0,1},1,1);
 require(std::abs(norm(diag.traction)-1)<1e-18L,"circular cone,not component clipping");
 auto eq=radialReturn({},V{1,0,0},V{0,0,1},1,1);require(!eq.unique,"nonunique yield event");
 bool rejected=false;try{eq.classicalTangent();}catch(const std::domain_error&){rejected=true;}require(rejected,"yield derivative rejection");
 auto zero=radialReturn({},V{},V{0,0,1},1,0);for(R x:zero.tangent)require(x==0,"zero-capacity tangent");
 require(maxFD<1e-8L&&maxEnergy<1e-20L&&maxCov<1e-17L&&maxCone<1e-18L,"vector return tolerance");
 std::cout<<std::setprecision(18)<<"VECTOR_RETURN {\"states\":600,\"fd_absolute\":"<<maxFD<<",\"energy_absolute\":"<<maxEnergy<<",\"covariance_absolute\":"<<maxCov<<",\"cone_excess\":"<<maxCone<<"}\n";
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
