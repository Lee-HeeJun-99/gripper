#pragma once
#include "VectorReturn.h"
#include "PolynomialFronts.h"
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
 R a,k;V normal;std::vector<Step>past;R spatialLipschitz=0;std::uint64_t epoch_=0;
public:
 struct Integral {
  std::array<R,17> v{};std::size_t evaluations=0,leaves=0;
  R embeddedError=0,hiddenLossUpperBound=0;
  std::size_t nonuniqueSamples=0;
  // v: Uold,Unew,D,Pendpoint,Wendpoint,F[3],J[9].
 };
 struct Trial {
  friend class VectorField;
 private:
  const VectorField*owner=nullptr;std::uint64_t epoch=0;Step step;
 public:
  Integral integral;
 };
 VectorField(R halfLength,R stiffness,V n={0,0,1}):a(halfLength),k(stiffness),normal(n){
  if(!std::isfinite(a)||a<=0)throw std::invalid_argument("material domain");
  radialReturn({}, {},normal,k,0);
 }
 std::uint64_t epoch()const{return epoch_;}
 std::size_t expressionDepth()const{return past.size();}
 struct MaterialValue {V elastic{};bool onYield=false;};
 MaterialValue materialAt(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("material coordinate");
  MaterialValue state;for(const auto&s:past){R cap=s.capacity*(1-x*x);auto r=radialReturn(state.elastic,value(s.increment,x),normal,k,cap);state.elastic=r.elastic;state.onYield=cap>0&&(r.slip||!r.unique);}
  return state;
 }
 V elasticAt(R x)const{return materialAt(x).elastic;}
 Return point(const Step&s,R x,V direction={})const{
  auto stored=materialAt(x);V old=stored.elastic;
  if(s.capacity*(1-x*x)>0&&s.increment==VP{}&&!past.empty()&&s.capacity>=past.back().capacity){
   // Exact operator identity P_c(e)=e for previously admissible e and a
   // nondecreasing capacity. Do NOT repeatedly renormalize a stored return
   // because its floating norm differs from c/k by one ULP. At equal
   // capacity the elastic matrix is a SELECTED generalized derivative,
   // not a unique classical derivative on already-yielded material.
   Return r;r.before=old;r.elastic=old;r.traction=scale(old,k);r.oldEnergy=r.energy=.5L*k*dot(old,old);
   r.trialLoad=k*norm(old);r.unique=s.capacity>past.back().capacity||!stored.onYield;
   for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.tangent[3*i+j]=k*((i==j?1.L:0.L)-normal[i]*normal[j]);
   if(!r.unique&&dot(old,direction)>0){
    // Velocity-directed member of the B-subdifferential: loading uses the
    // circular-slip side,unloading the elastic side. This is a ONE-SIDED
    // directional linearization,never a unique classical Jacobian.
    V u=scale(old,1/norm(old));for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.tangent[3*i+j]-=k*u[i]*u[j];
   }
   return r;
  }
  return radialReturn(old,value(s.increment,x),normal,k,s.capacity*(1-x*x));
 }
private:
 Trial evaluateRaw(Step step,R relative,R absolute,std::size_t budget,V direction)const{
  if(past.size()>=4096)throw std::length_error("bounded reference time history");
  if(!std::isfinite(relative)||relative<=0||!std::isfinite(absolute)||absolute<=0||budget<5)throw std::invalid_argument("integration controls");
  for(V coefficient:step.increment)radialReturn({},coefficient,normal,k,step.capacity);
  radialReturn({},direction,normal,k,0);
  Trial t;t.owner=this;t.epoch=epoch();t.step=step;
  const R Ltrial=spatialLipschitz+norm(step.increment[1])+2*norm(step.increment[2]);
  const R Ly=k*Ltrial+2*step.capacity;
  R Ldu=norm(step.increment[1])+2*norm(step.increment[2]);
  R Umax=norm(step.increment[0])+norm(step.increment[1])+norm(step.increment[2]);
  R Emax=past.empty()?0:past.back().capacity/k;
  R LH=2*k*k*(spatialLipschitz*Umax+Emax*Ldu+Umax*Ldu);
  bool zeroReturnLoss=step.capacity==0||(step.increment==VP{}&&(past.empty()||step.capacity>=past.back().capacity));
  struct Sample{std::array<R,17>v{};R yield=0,admissibleSquareUpper=0;};
  auto sample=[&](R x){
   if(++t.integral.evaluations>budget)throw std::length_error("vector quadrature evaluation budget");
   auto r=point(step,x,direction);Sample s;
   if(!r.unique)++t.integral.nonuniqueSamples;
   s.v[0]=r.oldEnergy;s.v[1]=r.energy;s.v[2]=r.loss;s.v[3]=r.projection;s.v[4]=r.work;
   for(int i=0;i<3;++i)s.v[5+i]=r.traction[i];
   for(int i=0;i<9;++i)s.v[8+i]=r.tangent[i];
   s.yield=r.trialLoad-step.capacity*(1-x*x);
   V du=value(step.increment,x);s.admissibleSquareUpper=k*k*(2*dot(r.before,du)+dot(du,du));
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
    if(past.empty()||step.capacity>=past.back().capacity){
     // Previously admissible history gives k²|e0+d|²-c² <=
     // H=2k² e0.d+k²|d|². This CANCELS the large old-capacity
     // derivative on yielded material. A global |yield|' bound alone
     // forces near-uniform refinement for tiny UNLOADING increments.
     R Hmax=std::max(0.L,m.admissibleSquareUpper+LH*width/2);
     hidden=std::min(hidden,a*width*step.capacity*std::sqrt(Hmax)/k);
    }
    if(hidden>absolute/256)accurate=false;
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
  }else if(past.empty()&&step.capacity>0){
   // Circular vector yield: k²|quadratic d(x)|²-C²(1-x²)²=0.
   // This is quartic,not component-wise scalar roots.
   std::vector<R>poly(5);for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j)poly[i+j]+=k*k*dot(step.increment[i],step.increment[j]);
   poly[0]-=step.capacity*step.capacity;poly[2]+=2*step.capacity*step.capacity;poly[4]-=step.capacity*step.capacity;
   auto knots=polynomialFronts(poly,-1,1);knots.insert(knots.begin(),-1);knots.push_back(1);
   for(unsigned j=1;j<knots.size();++j){R lo=knots[j-1],hi=knots[j];auto p=sample(lo),q=sample((lo+hi)/2),s=sample(hi);recurse(recurse,lo,hi,p,q,s,0);}
  }else recurse(recurse,-1,1,l,m,r,0);
  for(int i=0;i<17;++i)if(errorSum[i]>goals[i]){std::ostringstream message;message<<"global embedded error budget exceeded quantity="<<i<<" error="<<errorSum[i]<<" goal="<<goals[i]<<" epoch="<<epoch();throw std::runtime_error(message.str());}
  if(t.integral.hiddenLossUpperBound>absolute)throw std::runtime_error("global unresolved-loss upper bound exceeds requested absolute budget");
  return t;
 }
public:
 Trial evaluate(Step step,R relative=1e-7L,R absolute=1e-28L,std::size_t budget=500000,V direction={})const{
  if(norm(direction)==0)return evaluateRaw(step,relative,absolute,budget,{});
  // Changing a selected generalized tangent must NEVER change force,energy,
  // loss or committed state through an adaptively changed integration mesh.
  // Integrate the sided matrix separately;all physical values come from the
  // identical direction-independent pass. Split the SAME total work budget.
  auto base=evaluateRaw(step,relative,absolute,budget/2,{});
  auto sided=evaluateRaw(step,relative,absolute,budget/2,direction);
  for(int j=8;j<17;++j)base.integral.v[j]=sided.integral.v[j];
  base.integral.evaluations+=sided.integral.evaluations;
  base.integral.embeddedError+=sided.integral.embeddedError;
  base.integral.hiddenLossUpperBound=std::max(base.integral.hiddenLossUpperBound,sided.integral.hiddenLossUpperBound);
  return base;
 }
 void commit(const Trial&t){
  if(t.owner!=this||t.epoch!=epoch())throw std::invalid_argument("foreign/stale/double function-history Commit");
  for(V coefficient:t.step.increment)radialReturn({},coefficient,normal,k,t.step.capacity);
  ++epoch_;
  // Algebraic state identities,not an approximate history projection. The
  // Trial already measured the old/reset energy before this storage pruning.
  // Epoch MUST remain monotone so clearing the expression cannot revive old
  // Commit tokens. Friction OFF is not relabeled as physical contact death.
  if(t.step.capacity==0){past.clear();spatialLipschitz=0;return;}
  if(t.step.increment==VP{}&&(past.empty()||t.step.capacity>=past.back().capacity))return;
  past.push_back(t.step);
  // Conservative global bound; no fitted error epsilon or friction change.
  spatialLipschitz+=norm(t.step.increment[1])+2*norm(t.step.increment[2])+2*t.step.capacity/k;
 }
};
}
