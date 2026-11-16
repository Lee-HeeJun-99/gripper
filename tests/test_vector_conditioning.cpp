#include "../models/yield_front_history/VectorField.h"
#include "../models/yield_front_history/AdaptiveSnapshot.h"
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <boost/version.hpp>
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
using H=boost::multiprecision::cpp_dec_float_50;using HV=std::array<H,3>;
H normH(const HV&v){H r=0;for(const auto&x:v)r+=x*x;return sqrt(r);}
int main(){try{
 constexpr R k=.001L,C=3e-6L,a=.3192L;VectorField exact(a,k);
 for(int i=0;i<24;++i){Step s;s.capacity=C;s.increment={V{.0012L*std::cos(.9L*i),.0009L*std::sin(.7L*i),0},V{.0001L,-.00013L,0},V{.00003L,.00002L,0}};auto t=exact.evaluate(s,1e-6L,1e-25L);exact.commit(t);}
 std::vector<V>probes{{1e-8L,0,0},{0,1e-8L,0},{-1e-8L,0,0},{0,-1e-8L,0},{1e-5L,-2e-5L,0}};
 AdaptiveSnapshot snapshot([&](R x){return exact.elasticAt(x);},k,C,1e-9L,probes,3e-18L);
 auto knots=snapshot.yieldKnots(probes[0]);std::size_t mismatches=0,lossFailures=0,total=0;
 R maxAbsoluteLoss=0;H maxRelativeLoss=0;
 std::cout<<std::setprecision(30)<<"BOOST "<<BOOST_LIB_VERSION<<"\nx,gap_long_double,gap_decimal50,loss_long_double,loss_decimal50\n";
 for(R center:knots)if(center>.963L&&center<.964L)for(R stride:{1e-7L,1e-9L,1e-11L,1e-13L})for(int j=-4;j<=4;++j){
  R x=center+j*stride;auto cell=std::lower_bound(snapshot.cells.begin(),snapshot.cells.end(),x,[](const auto&c,R p){return c.hi<p;});
  H u=(H(x)-H(cell->lo))/(H(cell->hi)-H(cell->lo));HV old{};
  for(int i=0;i<4;++i){H w=1;for(int q=0;q<4;++q)if(i!=q)w*=(3*u-q)/H(i-q);for(int axis=0;axis<3;++axis)old[axis]+=w*H(cell->values[i][axis]);}
  H cap=H(C)*(1-H(x)*H(x)),length=normH(old);
  if(H(k)*length>cap)for(auto&v:old)v*=cap/(H(k)*length);
  HV trial=old;for(int axis=0;axis<3;++axis)trial[axis]+=H(probes[0][axis]);
  H trialLength=normH(trial),gap=H(k)*trialLength-cap;HV returned=trial;
  if(gap>0)for(auto&v:returned)v*=cap/(H(k)*trialLength);
  HV plastic;for(int axis=0;axis<3;++axis)plastic[axis]=trial[axis]-returned[axis];H loss=cap*normH(plastic);
  auto r=radialReturn(snapshot.at(x),probes[0],{0,0,1},k,C*(1-x*x));R rgap=r.trialLoad-C*(1-x*x);
  if((rgap>0)!=(gap>0))++mismatches;
  H absolute=abs(H(r.loss)-loss);maxAbsoluteLoss=std::max(maxAbsoluteLoss,absolute.convert_to<R>());
  if(loss!=0){H error=absolute/loss;if(error>maxRelativeLoss)maxRelativeLoss=error;if(error>H("0.01"))++lossFailures;}
  else if(r.loss!=0)++lossFailures;
  ++total;std::cout<<x<<','<<rgap<<','<<gap<<','<<r.loss<<','<<loss<<'\n';
 }
 if(!total)throw std::runtime_error("conditioning roots absent");
 std::cout<<"CONDITIONING {\"samples\":"<<total<<",\"branch_disagreements\":"<<mismatches<<",\"loss_1percent_failures\":"<<lossFailures<<",\"max_absolute_loss_error\":"<<maxAbsoluteLoss<<",\"max_relative_loss_error\":"<<maxRelativeLoss<<"}\n";
 if(mismatches||lossFailures)return 1;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
