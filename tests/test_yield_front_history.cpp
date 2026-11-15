#include "../models/yield_front_history/ScalarField.h"
#include "../models/contact_energy/SlipBandReference.h"
#include <iostream>
#include <iomanip>
using namespace regrip_yield_front;
void require(bool b,const char*why){if(!b)throw std::runtime_error(why);}
int main(){try{
 constexpr Real a=.3192L,C=3e-6L,k=.001L;Real maxEnergy=0,maxReference=0,maxDerivative=0;std::size_t largest=0;
 for(Real d:{1e-4L,1e-6L,1e-8L}){Field f(a,k);auto t=f.evaluate({d,0,0},C);auto ref=regrip_slip_band::reference(a,C,k,d);Real error=std::abs(t.measures.dissipation-ref.plastic)/ref.plastic;maxReference=std::max(maxReference,error);require(error<1e-8L,"stateful exact virgin slip-band reference");require(f.epoch()==0&&f.pieces()==1,"trial query changed history");}
 Field field(a,k);Real accumulated=0;
 for(int step=0;step<120;++step){Poly du{2e-5L*std::sin(.17L*step),1e-5L*std::cos(.13L*step),3e-6L*std::sin(.11L*step)};Real cap=step>=70&&step<80?.4L*C:C;
  auto trial=field.evaluate(du,cap),again=field.evaluate(du,cap);require(trial.measures.energy==again.measures.energy&&trial.measures.dissipation==again.measures.dissipation,"repeated pure history query");
  auto&m=trial.measures;Real residual=m.energy-m.oldEnergy-m.inputWork+m.dissipation+m.endpointProjection;maxEnergy=std::max(maxEnergy,std::abs(residual));require(m.dissipation>=0&&m.endpointProjection>=0,"negative dissipation/projection");require(std::abs(residual)<1e-24L,"exact endpoint integrated energy identity");
  if(step%9==0){Real eps=1e-9L;auto left=du,right=du;left[0]-=eps;right[0]+=eps;auto u=field.evaluate(left,cap),v=field.evaluate(right,cap);Real derivative=((v.measures.energy+v.measures.dissipation)-(u.measures.energy+u.measures.dissipation))/(2*eps);Real error=std::abs(derivative-m.traction)/std::max(1e-12L,std::abs(m.traction));maxDerivative=std::max(maxDerivative,error);require(error<1e-6L,"incremental potential derivative not traction");Real tangent=(v.measures.traction-u.measures.traction)/(2*eps);require(std::abs(tangent-m.tangent)<1e-8L,"yield-front integrated tangent mismatch");}
  field.commit(trial);bool rejected=false;try{field.commit(trial);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"double Commit accepted");
  for(int i=0;i<=300;++i){Real x=-1+2.L*i/300;require(std::abs(k*field.elasticAt(x))<=cap*(1-x*x)+1e-22L,"material Coulomb bound violated");}
  largest=std::max(largest,field.pieces());accumulated+=m.dissipation;
 }
 auto off=field.evaluate({0,0,0},0);require(off.measures.energy==0&&off.measures.dissipation==0,"zero capacity has nonzero traction/heat");require(std::abs(off.measures.oldEnergy-off.measures.endpointProjection)<1e-24L,"zero-capacity stored-energy release not accounted separately");
 std::cout<<std::setprecision(17)<<"YIELD_FRONT {\"steps\":120,\"max_pieces\":"<<largest<<",\"virgin_loss_relative_error\":"<<double(maxReference)<<",\"max_endpoint_energy_residual\":"<<double(maxEnergy)<<",\"max_potential_derivative_relative_error\":"<<double(maxDerivative)<<",\"accumulated_loss\":"<<double(accumulated)<<"}\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
