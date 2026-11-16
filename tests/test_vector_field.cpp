#include "../models/yield_front_history/VectorField.h"
#include "../models/contact_energy/SlipBandReference.h"
#include "../models/yield_front_history/ScalarField.h"
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int main(){try{
 constexpr R a=.3192L,k=.001L,C=3e-6L;
 VectorField field(a,k);R D=0,energyError=0;std::size_t evaluations=0;
 std::vector<Step>steps;
 for(int i=0;i<12;++i){Step s;
  s.increment={V{.0012L*std::cos(.9L*i),.0009L*std::sin(.7L*i),0},V{.0001L, -.00013L,0},V{.00003L, .00002L,0}};
  s.capacity=i>=7&&i<9?.4L*C:C;steps.push_back(s);
  auto t=field.evaluate(s,1e-6L,1e-25L);auto again=field.evaluate(s,1e-6L,1e-25L);
  require(t.integral.v==again.integral.v&&field.epoch()==unsigned(i),"query purity");
  auto v=t.integral.v;energyError=std::max(energyError,std::abs(v[1]-v[0]-v[4]+v[2]+v[3]));
  D+=v[2];evaluations+=t.integral.evaluations;field.commit(t);
  bool rejected=false;try{field.commit(t);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"once-only Commit");
 }
 // Independently implemented dense plastic-vector slider: stores plastic
 // displacement z and accumulated displacement u,not returned elastic e.
 R first=0,last=0;
 for(unsigned n:{1024u,4096u,16384u,65536u}){
  std::vector<V>u(n),z(n);R denseD=0;
  for(auto s:steps)for(unsigned j=0;j<n;++j){R x=-1+2*(R(j)+.5L)/n;
   u[j]=add(u[j],value(s.increment,x));V trial=add(u[j],scale(z[j],-1));R length=norm(trial),limit=s.capacity*(1-x*x)/k;
   if(length>limit){V next=add(u[j],scale(trial,-limit/length));denseD+=2*a/n*s.capacity*(1-x*x)*norm(add(next,scale(z[j],-1)));z[j]=next;}
  }
  R error=std::abs(denseD-D)/D;if(n==1024)first=error;last=error;
  std::cout<<std::setprecision(18)<<"DENSE "<<n<<' '<<denseD<<' '<<error<<'\n';
 }
 require(last<first&&last<1e-5L,"independent vector dense reference convergence");
 require(energyError<1e-24L,"integrated endpoint energy identity");
 // Collinear loading is an exact reduction to the independently implemented
 // piecewise-polynomial scalar history,including reversal and pressure steps.
 VectorField collinear(a,k);regrip_yield_front::Field scalar(a,k);R scalarError=0;
 for(int i=0;i<20;++i){regrip_yield_front::Poly p{.0008L*std::cos(.7L*i),.00012L,.00003L*std::sin(.4L*i)};
  Step s;for(int j=0;j<3;++j)s.increment[j]={p[j],0,0};s.capacity=i>12?.4L*C:C;
  auto v=collinear.evaluate(s,1e-7L,1e-27L);auto q=scalar.evaluate(p,s.capacity);
  scalarError=std::max(scalarError,std::abs(v.integral.v[2]-q.measures.dissipation));
  require(std::abs(v.integral.v[2]-q.measures.dissipation)<1e-16L,"exact scalar branch reference");
  collinear.commit(v);scalar.commit(q);
 }
 // Integrated fixed-history tangent/potential derivatives,not a spatial SO3 J.
 Step probe=steps.back();probe.increment[0]={.0003L,-.0004L,0};auto base=field.evaluate(probe,1e-8L,1e-27L);
 R fieldFD=0;
 for(int j=0;j<2;++j){R h=1e-6L;Step p=probe,m=probe;p.increment[0][j]+=h;m.increment[0][j]-=h;
  auto plus=field.evaluate(p,1e-8L,1e-27L),minus=field.evaluate(m,1e-8L,1e-27L);
  for(int i=0;i<2;++i)fieldFD=std::max(fieldFD,std::abs((plus.integral.v[5+i]-minus.integral.v[5+i])/(2*h)-base.integral.v[8+3*i+j]));
  require(std::abs((plus.integral.v[1]+plus.integral.v[2]-minus.integral.v[1]-minus.integral.v[2])/(2*h)-base.integral.v[5+j])<1e-11L,"field incremental potential gradient");
 }
 require(fieldFD<1e-8L,"field tangent FD");
 Step unchanged;unchanged.capacity=steps.back().capacity;auto restQuery=field.evaluate(unchanged,1e-7L,1e-30L);
 require(restQuery.integral.v[2]==0&&restQuery.integral.v[3]==0&&restQuery.integral.v[4]==0&&restQuery.integral.v[0]==restQuery.integral.v[1],"exact rest query must not rereturn/produce loss");
 require(restQuery.integral.nonuniqueSamples>0,"rest generalized tangent must be explicit,not classical certification");
 auto beforeRest=field.elasticAt(.314159L);auto depth=field.expressionDepth();auto beforeEpoch=field.epoch();field.commit(restQuery);
 require(field.elasticAt(.314159L)==beforeRest&&field.expressionDepth()==depth&&field.epoch()==beforeEpoch+1,"identity Commit must not reround state or revive tokens");
 VectorField off(a,k);Step capOff;auto offStep=off.evaluate(capOff);off.commit(offStep);auto offAgain=off.evaluate(capOff);
 for(int j=8;j<17;++j)require(offAgain.integral.v[j]==0,"repeated friction-OFF query has zero tangent");
 require(off.expressionDepth()==0&&off.epoch()==1,"exact zero-state expression pruning");
 // A circular return at positive yield is directionally,not classically,
 // differentiable. Check its integrated loading/unloading derivative against
 // independent ONE-SIDED force queries;never use a centered FD at this event.
 VectorField sided(a,k);Step preload;preload.capacity=C;preload.increment[0]={.002L,.001L,0};auto pre=sided.evaluate(preload);sided.commit(pre);
 R sidedFD=0;
 for(R sign:{-1.L,1.L}){V direction{sign*.2L,sign*.1L,0};Step rest;rest.capacity=C;
  auto directional=sided.evaluate(rest,1e-8L,1e-30L,500000,direction);
  Step shifted=rest;R h=1e-7L;shifted.increment[0]=scale(direction,h);auto perturbed=sided.evaluate(shifted,1e-8L,1e-30L);
  for(int i=0;i<2;++i){R tangent=0;for(int j=0;j<2;++j)tangent+=directional.integral.v[8+3*i+j]*direction[j];sidedFD=std::max(sidedFD,std::abs((perturbed.integral.v[5+i]-directional.integral.v[5+i])/h-tangent));}
 }
 require(sidedFD<1e-8L,"direction-sided yield linearization");
 std::cout<<std::setprecision(18)<<"DIRECTIONAL_FD "<<sidedFD<<'\n';
 VectorField foreign(a,k);auto owned=foreign.evaluate(probe);bool foreignRejected=false;
 try{field.commit(owned);}catch(const std::invalid_argument&){foreignRejected=true;}require(foreignRejected,"cross-field Commit");
 // Virgin boundary slip band so thin that fixed midpoint grids miss it.
 VectorField thin(a,k);Step tiny;tiny.capacity=C;tiny.increment[0]={1e-12L,2e-12L,0};
 auto t=thin.evaluate(tiny,1e-7L,1e-46L);
 require(t.integral.v[2]>0,"adaptive yield search missed tiny loss");
 R tinyReference=regrip_slip_band::reference(a,C,k,norm(tiny.increment[0])).plastic;
 R tinyRelative=std::abs(t.integral.v[2]-tinyReference)/tinyReference;
 std::cout<<std::setprecision(18)<<"TINY_REFERENCE "<<tinyReference<<" relative="<<tinyRelative<<'\n';
 require(tinyRelative<.01L,"tiny newly resolved loss must meet unchanged 1 percent reference criterion");
 std::cout<<std::setprecision(18)<<"VECTOR_FIELD {\"steps\":12,\"loss\":"<<D<<",\"dense_relative\":"<<last<<",\"energy_residual\":"<<energyError<<",\"evaluations\":"<<evaluations<<",\"tiny_loss\":"<<t.integral.v[2]<<",\"tiny_hidden_bound\":"<<t.integral.hiddenLossUpperBound<<",\"scalar_loss_absolute\":"<<scalarError<<",\"field_tangent_fd\":"<<fieldFD<<"}\n";
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
