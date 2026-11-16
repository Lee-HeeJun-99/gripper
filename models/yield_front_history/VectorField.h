#pragma once
#include "VectorReturn.h"
#include "PolynomialFronts.h"
#include <algorithm>
#include <cstdint>
#include <sstream>
#include <map>
#include <functional>
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
 V lastIncrementAt(R x)const{if(past.empty())throw std::domain_error("endpoint limit needs a nonzero committed increment");return value(past.back().increment,x);}
 bool isZeroState()const{return !hasInitialState();}
 struct MaterialValue {V elastic{};bool onYield=false;bool gapKnown=false;R normalizedGap=0;};
private:
 std::function<MaterialValue(R)>seed;
 std::function<R(R,R)>seedLocalBound;
 std::function<R(const Step&,R,R)>seedStickRoundoffBound;
 std::function<std::vector<R>(V)>seedTangentPartition;
 std::function<int(R,V)>seedDirectionSide;
 std::vector<R>seedKnots;
 R addedLipschitz=0;
 R seedCapacity=0;
 R previousCapacity()const{return past.empty()?seedCapacity:past.back().capacity;}
 bool hasInitialState()const{return bool(seed)||!past.empty();}
public:
 VectorField(R halfLength,R stiffness,V n,std::function<MaterialValue(R)>initial,R admissibleCapacity,R lipschitz,std::vector<R>knots={},std::function<R(R,R)>localBound={},std::function<R(const Step&,R,R)>stickRoundoffBound={},std::function<std::vector<R>(V)>tangentPartition={},std::function<int(R,V)>directionSide={}):VectorField(halfLength,stiffness,n){
  if(!initial||!std::isfinite(admissibleCapacity)||admissibleCapacity<0||!std::isfinite(lipschitz)||lipschitz<0)throw std::invalid_argument("immutable history seed and conservative bounds");
  seed=std::move(initial);seedCapacity=admissibleCapacity;spatialLipschitz=lipschitz;
  if(!knots.empty()){if(knots.front()!= -1||knots.back()!=1)throw std::invalid_argument("seed partition endpoints");for(std::size_t j=1;j<knots.size();++j)if(!std::isfinite(knots[j])||knots[j]<=knots[j-1])throw std::invalid_argument("seed partition order");}
  seedKnots=std::move(knots);seedLocalBound=std::move(localBound);
  seedStickRoundoffBound=std::move(stickRoundoffBound);
  seedTangentPartition=std::move(tangentPartition);
  seedDirectionSide=std::move(directionSide);
 }
 R lipschitzUpperBound()const{return spatialLipschitz;}
 struct PrefixMemo {std::size_t prefix=0;MaterialValue state;};
 mutable std::map<R,PrefixMemo>prefixMemo;
 MaterialValue advance(MaterialValue state,const Step&s,R x)const{
  R cap=s.capacity*(1-x*x);auto r=radialReturn(state.elastic,value(s.increment,x),normal,k,cap);state.elastic=r.elastic;state.onYield=cap>0&&(r.slip||!r.unique);state.gapKnown=cap>0;state.normalizedGap=state.gapKnown?(state.onYield?0:(cap-r.trialLoad)/cap):0;return state;
 }
 MaterialValue uncachedMaterialAt(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("material coordinate");
  MaterialValue state=seed?seed(x):MaterialValue{};for(const auto&s:past)state=advance(state,s,x);
  return state;
 }
 MaterialValue materialAt(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("material coordinate");
  auto found=prefixMemo.find(x);PrefixMemo memo;
  if(found!=prefixMemo.end())memo=found->second;
  else if(seed)memo.state=seed(x);
  if(memo.prefix>past.size())throw std::logic_error("stale reference prefix memo");
  // Replay only NEW committed return operators at exactly the SAME material
  // coordinate. The saved prefix is bitwise the result of the original loop;
  // no history interpolation,projection,operator reassociation or time skip.
  for(std::size_t j=memo.prefix;j<past.size();++j)memo.state=advance(memo.state,past[j],x);
  memo.prefix=past.size();
  if(found!=prefixMemo.end())found->second=memo;
  else if(prefixMemo.size()<131072)prefixMemo.emplace(x,memo);
  // Beyond the finite auxiliary-cache cap use full replay,not a physical
  // history truncation. Tentative trial returns are NEVER inserted here.
  return memo.state;
 }
 V elasticAt(R x)const{return materialAt(x).elastic;}
 Return point(const Step&s,R x,V direction={})const{
  auto stored=materialAt(x);V old=stored.elastic;
  if(s.capacity*(1-x*x)>0&&s.increment==VP{}&&hasInitialState()&&s.capacity>=previousCapacity()){
   // Exact operator identity P_c(e)=e for previously admissible e and a
   // nondecreasing capacity. Do NOT repeatedly renormalize a stored return
   // because its floating norm differs from c/k by one ULP. At equal
   // capacity the elastic matrix is a SELECTED generalized derivative,
   // not a unique classical derivative on already-yielded material.
   Return r;r.before=old;r.elastic=old;r.traction=scale(old,k);r.oldEnergy=r.energy=.5L*k*dot(old,old);
   r.trialLoad=k*norm(old);r.unique=s.capacity>previousCapacity()||!stored.onYield;
   for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.tangent[3*i+j]=k*((i==j?1.L:0.L)-normal[i]*normal[j]);
   bool loading=past.empty()&&seedDirectionSide?seedDirectionSide(x,direction)>0:dot(old,direction)>0;
   if(!r.unique&&loading){
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
 Trial evaluateRaw(Step step,R relative,R absolute,std::size_t budget,V direction,R fixedLossGoal=-1,unsigned retry=0,R localTightening=1)const{
  if(past.size()>=4096)throw std::length_error("bounded reference time history");
  if(!std::isfinite(relative)||relative<=0||!std::isfinite(absolute)||absolute<=0||budget<5)throw std::invalid_argument("integration controls");
  for(V coefficient:step.increment)radialReturn({},coefficient,normal,k,step.capacity);
  radialReturn({},direction,normal,k,0);
  Trial t;t.owner=this;t.epoch=epoch();t.step=step;
  const R Ltrial=spatialLipschitz+norm(step.increment[1])+2*norm(step.increment[2]);
  const R Ly=k*Ltrial+2*step.capacity;
  R Ldu=norm(step.increment[1])+2*norm(step.increment[2]);
  R Umax=norm(step.increment[0])+norm(step.increment[1])+norm(step.increment[2]);
  R Emax=previousCapacity()/k;
  bool zeroReturnLoss=step.capacity==0||(step.increment==VP{}&&step.capacity>=previousCapacity());
  int lastQuantity=-1;R lastError=0,lastAllowed=0,lastLo=0,lastHi=0;
  struct Sample{std::array<R,17>v{};R yield=0,admissibleSquareUpper=0;};
  auto sample=[&](R x){
   if(++t.integral.evaluations>budget){std::ostringstream message;message.precision(18);message<<"vector quadrature evaluation budget="<<budget<<" epoch="<<epoch()<<" seed="<<bool(seed)<<" x="<<x<<" last_quantity="<<lastQuantity<<" last_error="<<lastError<<" last_allowed="<<lastAllowed<<" lo="<<lastLo<<" hi="<<lastHi<<" resolved_loss="<<t.integral.v[2]<<" unresolved_loss="<<t.integral.hiddenLossUpperBound<<" fixed_loss_goal="<<fixedLossGoal;throw std::length_error(message.str());}
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
  if(fixedLossGoal>0)goals[2]=fixedLossGoal;
  auto recurse=[&](auto&&self,R lo,R hi,const Sample&l,const Sample&m,const Sample&r,unsigned depth)->void{
   R mid=(lo+hi)/2,width=hi-lo;
   auto lm=sample((lo+mid)/2),rm=sample((mid+hi)/2);
   for(int i=0;i<17;++i)if(i!=2||fixedLossGoal<=0)goals[i]=std::max(goals[i],absolute+relative*2*a*std::max(std::abs(lm.v[i]),std::abs(rm.v[i])));
   auto coarse=simpson(width,l,m,r),left=simpson(width/2,l,lm,m),right=simpson(width/2,m,rm,r);
   bool accurate=true;R errorMax=0,worstRatio=0;
   for(int i=0;i<17;++i){R fine=left[i]+right[i],err=std::abs(fine-coarse[i])/15;
    errorMax=std::max(errorMax,err);
    // A jump in the return tangent cannot satisfy a relative-per-leaf
    // criterion as its interval shrinks. Allocate GLOBAL integral goals;
    // verify the actual summed embedded estimates again before returning.
    R allowed=goals[i]*localTightening/256;
    if(a*err>allowed){accurate=false;R ratio=a*err/allowed;if(ratio>worstRatio){worstRatio=ratio;lastQuantity=i;lastError=a*err;lastAllowed=allowed;lastLo=lo;lastHi=hi;}}
   }
   // Embedded quadrature alone can report ZERO error while missing a narrow
   // slip band. Projection onto a ball is nonexpansive; varying its radius
   // adds |dc|/k. Ly therefore bounds the trial yield function's slope.
   // If all samples have zero loss but slip is possible, bound its entire
   // unsampled loss, not merely the observed contact-force integration error.
   bool samplesZero=l.v[2]==0&&lm.v[2]==0&&m.v[2]==0&&rm.v[2]==0&&r.v[2]==0;
   R hidden=0;
   if(samplesZero&&!zeroReturnLoss){
    R localOldL=spatialLipschitz;
    if(seedLocalBound){localOldL=seedLocalBound(lo,hi)+addedLipschitz;if(!std::isfinite(localOldL)||localOldL<0)throw std::invalid_argument("nonfinite/negative local material bound");}
    R localLy=k*(localOldL+Ldu)+2*step.capacity;
    R localLH=2*k*k*(localOldL*Umax+Emax*Ldu+Umax*Ldu);
    R ymax=std::max(0.L,m.yield+localLy*width/2);
    hidden=a*width*step.capacity*ymax/k;
    if(step.capacity>=previousCapacity()){
     // Previously admissible history gives k²|e0+d|²-c² <=
     // H=2k² e0.d+k²|d|². This CANCELS the large old-capacity
     // derivative on yielded material. A global |yield|' bound alone
     // forces near-uniform refinement for tiny UNLOADING increments.
     R Hmax=std::max(0.L,m.admissibleSquareUpper+localLH*width/2);
     hidden=std::min(hidden,a*width*step.capacity*std::sqrt(Hmax)/k);
    }
    // Use the SAME absolute+relative INTEGRAL loss budget as measured loss,
    // not absolute-only refinement beside already resolved positive loss.
    // With no resolved loss this remains the strict requested absolute bound.
    // No positive loss is discarded or relabeled as zero.
    R resolvedLower=std::max(0.L,t.integral.v[2]-errorSum[2]);
    R hiddenGoal=absolute+relative*resolvedLower;
    if(fixedLossGoal>0)hiddenGoal=std::min(hiddenGoal,fixedLossGoal);
    R hiddenAllowed=hiddenGoal*localTightening/256;
    if(hidden>hiddenAllowed&&seedStickRoundoffBound&&past.empty()){
     R density=seedStickRoundoffBound(step,lo,hi);
     if(density>=0&&std::isfinite(density))hidden=std::min(hidden,a*width*density);
    }
    if(hidden>hiddenAllowed){accurate=false;R ratio=hidden/hiddenAllowed;if(ratio>worstRatio){lastQuantity=17;lastError=hidden;lastAllowed=hiddenAllowed;lastLo=lo;lastHi=hi;}}
   }
   if(accurate){
    // No Richardson extrapolation across a nonsmooth yield front.
    for(int i=0;i<17;++i){t.integral.v[i]+=a*(left[i]+right[i]);errorSum[i]+=a*std::abs(left[i]+right[i]-coarse[i])/15;}
    t.integral.hiddenLossUpperBound+=hidden;t.integral.embeddedError+=a*errorMax;++t.integral.leaves;return;
   }
   if(depth>=60||mid==lo||mid==hi){std::ostringstream message;message.precision(18);message<<"unresolved vector yield front: epoch="<<epoch()<<" lo="<<lo<<" hi="<<hi<<" hidden="<<hidden<<" yield="<<m.yield<<" Ly="<<Ly;for(int i=0;i<17;++i)if(a*std::abs(left[i]+right[i]-coarse[i])/15>goals[i]/256)message<<" quantity="<<i<<" err="<<a*std::abs(left[i]+right[i]-coarse[i])/15<<" goal="<<goals[i];throw std::runtime_error(message.str());}
   self(self,lo,mid,l,lm,m,depth+1);self(self,mid,hi,m,rm,r,depth+1);
  };
  auto integrationKnots=seedKnots;
  if(seedTangentPartition&&past.empty()&&step.increment==VP{}&&norm(direction)>0)integrationKnots=seedTangentPartition(direction);
  if(!integrationKnots.empty()){
   for(std::size_t j=1;j<integrationKnots.size();++j){R lo=integrationKnots[j-1],hi=integrationKnots[j];auto p=sample(lo),q=sample((lo+hi)/2),s=sample(hi);recurse(recurse,lo,hi,p,q,s,0);}
  }else if(!hasInitialState()&&step.increment[1]==V{}&&step.increment[2]==V{}&&step.capacity>0){
   // A constant-vector virgin trial has EXACT circular-yield roots. The
   // direction is immaterial: |k*d|=C(1-x*x). Align the integration pieces
   // before evaluating even arbitrarily thin edge bands. Tightening a blind
   // embedded quadrature tolerance alone cannot repair missed yield fronts.
   R ratio=k*norm(step.increment[0])/step.capacity;
   if(ratio>0&&ratio<1){R b=std::sqrt(1-ratio);R knots[4]={-1,-b,b,1};
    for(int j=0;j<3;++j){R lo=knots[j],hi=knots[j+1];auto p=sample(lo),q=sample((lo+hi)/2),s=sample(hi);recurse(recurse,lo,hi,p,q,s,0);}
   }else recurse(recurse,-1,1,l,m,r,0);
  }else if(!hasInitialState()&&step.capacity>0){
   // Circular vector yield: k²|quadratic d(x)|²-C²(1-x²)²=0.
   // This is quartic,not component-wise scalar roots.
   std::vector<R>poly(5);for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j)poly[i+j]+=k*k*dot(step.increment[i],step.increment[j]);
   poly[0]-=step.capacity*step.capacity;poly[2]+=2*step.capacity*step.capacity;poly[4]-=step.capacity*step.capacity;
   auto knots=polynomialFronts(poly,-1,1);knots.insert(knots.begin(),-1);knots.push_back(1);
   for(unsigned j=1;j<knots.size();++j){R lo=knots[j-1],hi=knots[j];auto p=sample(lo),q=sample((lo+hi)/2),s=sample(hi);recurse(recurse,lo,hi,p,q,s,0);}
  }else recurse(recurse,-1,1,l,m,r,0);
  R lossTarget=absolute+relative*std::abs(t.integral.v[2]);
  if(t.integral.hiddenLossUpperBound+errorSum[2]>lossTarget){
   // Integral-relative loss accuracy cannot be inferred from the PEAK
   // density at a narrow front. Reintegrate with the observed integral
   // budget;all discarded-pass evaluations count toward the SAME cap.
   if(retry>=3||budget<=t.integral.evaluations+5){std::ostringstream message;message<<"global loss error="<<t.integral.hiddenLossUpperBound+errorSum[2]<<" target="<<lossTarget<<" retries="<<retry;throw std::runtime_error(message.str());}
   R nextGoal=std::min(lossTarget/4,fixedLossGoal>0?fixedLossGoal/4:lossTarget/4);
   auto refined=evaluateRaw(step,relative,absolute,budget-t.integral.evaluations,direction,nextGoal,retry+1,localTightening);
   refined.integral.evaluations+=t.integral.evaluations;return refined;
  }
  for(int i=0;i<17;++i)if(i!=2&&errorSum[i]>goals[i]){
   if(retry<3&&budget>t.integral.evaluations+5){
    // Known seed partitions can have >256accepted leaves. Tighten LOCAL
    // allocation only;the requested GLOBAL F/J/energy tolerance is unchanged.
    R factor=std::min(.5L,.5L*goals[i]/errorSum[i]);
    auto refined=evaluateRaw(step,relative,absolute,budget-t.integral.evaluations,direction,fixedLossGoal,retry+1,localTightening*factor);
    refined.integral.evaluations+=t.integral.evaluations;return refined;
   }
   std::ostringstream message;message<<"global embedded error budget exceeded quantity="<<i<<" error="<<errorSum[i]<<" goal="<<goals[i]<<" epoch="<<epoch();throw std::runtime_error(message.str());
  }
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
  if(t.step.capacity==0){past.clear();prefixMemo.clear();seed={};seedLocalBound={};seedStickRoundoffBound={};seedTangentPartition={};seedDirectionSide={};seedKnots.clear();seedCapacity=0;spatialLipschitz=0;addedLipschitz=0;return;}
  if(t.step.increment==VP{}&&t.step.capacity>=previousCapacity())return;
  past.push_back(t.step);
  // Conservative global bound; no fitted error epsilon or friction change.
  R increase=norm(t.step.increment[1])+2*norm(t.step.increment[2])+2*t.step.capacity/k;
  spatialLipschitz+=increase;addedLipschitz+=increase;
 }
};
}
