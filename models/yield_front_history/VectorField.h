#pragma once
#include "VectorReturn.h"
#include <algorithm>
#include <cstdint>
#include <sstream>
#include <vector>

namespace regrip_vector_history {
using VP=std::array<V,3>;
inline V value(const VP&p,R x){return add(p[0],scale(add(p[1],scale(p[2],x)),x));}
struct Step {VP increment{};R capacity=0;};
// Exact FUNCTION-valued discrete material history: a bounded composition of
// radial return operators, evaluated at arbitrary x. No interpolation of
// previously returned samples. Storage grows with time, NOT material nodes.
// This is a reference algorithm, not a production time/space compression.
class VectorField {
 R a,k;V normal;std::vector<Step>past;R spatialLipschitz=0;
public:
 struct Integral {
  std::array<R,17> v{};std::size_t evaluations=0,leaves=0;
  R embeddedError=0,hiddenLossUpperBound=0;
  // v: Uold,Unew,D,Pendpoint,Wendpoint,F[3],J[9].
 };
 struct Trial {std::uint64_t epoch=0;Step step;Integral integral;};
 VectorField(R halfLength,R stiffness,V n={0,0,1}):a(halfLength),k(stiffness),normal(n){
  if(!std::isfinite(a)||a<=0)throw std::invalid_argument("material domain");
  radialReturn({}, {},normal,k,0);
 }
 std::size_t epoch()const{return past.size();}
 V elasticAt(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("material coordinate");
  V e{};for(const auto&s:past)e=radialReturn(e,value(s.increment,x),normal,k,s.capacity*(1-x*x)).elastic;
  return e;
 }
 Return point(const Step&s,R x)const{return radialReturn(elasticAt(x),value(s.increment,x),normal,k,s.capacity*(1-x*x));}
 Trial evaluate(Step step,R relative=1e-7L,R absolute=1e-28L,std::size_t budget=500000)const{
  if(past.size()>=4096)throw std::length_error("bounded reference time history");
  if(!std::isfinite(relative)||relative<=0||!std::isfinite(absolute)||absolute<=0||budget<5)throw std::invalid_argument("integration controls");
  for(V coefficient:step.increment)radialReturn({},coefficient,normal,k,step.capacity);
  Trial t;t.epoch=epoch();t.step=step;
  const R Ltrial=spatialLipschitz+norm(step.increment[1])+2*norm(step.increment[2]);
  const R Ly=k*Ltrial+2*step.capacity;
  bool zeroReturnLoss=step.capacity==0||(step.increment==VP{}&&(past.empty()||step.capacity>=past.back().capacity));
  struct Sample{std::array<R,17>v{};R yield=0;};
  auto sample=[&](R x){
   if(++t.integral.evaluations>budget)throw std::length_error("vector quadrature evaluation budget");
   auto r=point(step,x);Sample s;
   s.v[0]=r.oldEnergy;s.v[1]=r.energy;s.v[2]=r.loss;s.v[3]=r.projection;s.v[4]=r.work;
   for(int i=0;i<3;++i)s.v[5+i]=r.traction[i];
   for(int i=0;i<9;++i)s.v[8+i]=r.tangent[i];
   s.yield=k*norm(add(elasticAt(x),value(step.increment,x)))-step.capacity*(1-x*x);
   return s;
  };
  auto simpson=[](R width,const Sample&l,const Sample&m,const Sample&r){std::array<R,17>v{};for(int i=0;i<17;++i)v[i]=width*(l.v[i]+4*m.v[i]+r.v[i])/6;return v;};
  auto l=sample(-1),m=sample(0),r=sample(1);
  std::array<R,17> goals{},errorSum{};
  for(int i=0;i<17;++i)goals[i]=absolute+relative*2*a*std::max({std::abs(l.v[i]),std::abs(m.v[i]),std::abs(r.v[i])});
  auto recurse=[&](auto&&self,R lo,R hi,const Sample&l,const Sample&m,const Sample&r,unsigned depth)->void{
   R mid=(lo+hi)/2,width=hi-lo;
   auto lm=sample((lo+mid)/2),rm=sample((mid+hi)/2);
   for(int i=0;i<17;++i)goals[i]=std::max(goals[i],absolute+relative*2*a*std::max(std::abs(lm.v[i]),std::abs(rm.v[i])));
   auto coarse=simpson(width,l,m,r),left=simpson(width/2,l,lm,m),right=simpson(width/2,m,rm,r);
   bool accurate=true;R errorMax=0;
   for(int i=0;i<17;++i){R fine=left[i]+right[i],err=std::abs(fine-coarse[i])/15;
    errorMax=std::max(errorMax,err);
    // A jump in the return tangent cannot satisfy a relative-per-leaf
    // criterion as its interval shrinks. Allocate GLOBAL integral goals;
    // verify the actual summed embedded estimates again before returning.
    if(a*err>goals[i]/256)accurate=false;
   }
   // Embedded quadrature alone can report ZERO error while missing a narrow
   // slip band. Projection onto a ball is nonexpansive; varying its radius
   // adds |dc|/k. Ly therefore bounds the trial yield function's slope.
   // If all samples have zero loss but slip is possible, bound its entire
   // unsampled loss, not merely the observed contact-force integration error.
   bool samplesZero=l.v[2]==0&&lm.v[2]==0&&m.v[2]==0&&rm.v[2]==0&&r.v[2]==0;
   R hidden=0;
   if(samplesZero&&!zeroReturnLoss){
    R ymax=std::max(0.L,m.yield+Ly*width/2);
    hidden=a*width*step.capacity*ymax/k;
    if(hidden>absolute*width/2)accurate=false;
   }
   if(accurate){
    // No Richardson extrapolation across a nonsmooth yield front.
    for(int i=0;i<17;++i){t.integral.v[i]+=a*(left[i]+right[i]);errorSum[i]+=a*std::abs(left[i]+right[i]-coarse[i])/15;}
    t.integral.hiddenLossUpperBound+=hidden;t.integral.embeddedError+=a*errorMax;++t.integral.leaves;return;
   }
   if(depth>=44||mid==lo||mid==hi){std::ostringstream message;message.precision(18);message<<"unresolved vector yield front: epoch="<<epoch()<<" lo="<<lo<<" hi="<<hi<<" hidden="<<hidden<<" yield="<<m.yield<<" Ly="<<Ly;for(int i=0;i<17;++i)if(a*std::abs(left[i]+right[i]-coarse[i])/15>goals[i]/256)message<<" quantity="<<i<<" err="<<a*std::abs(left[i]+right[i]-coarse[i])/15<<" goal="<<goals[i];throw std::runtime_error(message.str());}
   self(self,lo,mid,l,lm,m,depth+1);self(self,mid,hi,m,rm,r,depth+1);
  };
  if(past.empty()&&step.increment[1]==V{}&&step.increment[2]==V{}&&step.capacity>0){
   // A constant-vector virgin trial has EXACT circular-yield roots. The
   // direction is immaterial: |k*d|=C(1-x*x). Align the integration pieces
   // before evaluating even arbitrarily thin edge bands. Tightening a blind
   // embedded quadrature tolerance alone cannot repair missed yield fronts.
   R ratio=k*norm(step.increment[0])/step.capacity;
   if(ratio>0&&ratio<1){R b=std::sqrt(1-ratio);R knots[4]={-1,-b,b,1};
    for(int j=0;j<3;++j){R lo=knots[j],hi=knots[j+1];auto p=sample(lo),q=sample((lo+hi)/2),s=sample(hi);recurse(recurse,lo,hi,p,q,s,0);}
   }else recurse(recurse,-1,1,l,m,r,0);
  }else recurse(recurse,-1,1,l,m,r,0);
  for(int i=0;i<17;++i)if(errorSum[i]>goals[i])throw std::runtime_error("global embedded error budget exceeded");
  return t;
 }
 void commit(const Trial&t){
  if(t.epoch!=epoch())throw std::invalid_argument("stale/double function-history Commit");
  for(V coefficient:t.step.increment)radialReturn({},coefficient,normal,k,t.step.capacity);
  past.push_back(t.step);
  // Conservative global bound; no fitted error epsilon or friction change.
  spatialLipschitz+=norm(t.step.increment[1])+2*norm(t.step.increment[2])+2*t.step.capacity/k;
 }
};
}
