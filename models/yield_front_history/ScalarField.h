#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <vector>

// EXPERIMENTAL independent1D fixed-normal/fixed-contact-domain reference.
// Not a3D contact ForceField,not birth/death/normal-transport integration.
// x=s/a in[-1,1],cap=C(1-x*x),increment polynomial of degree<=2.
// History is a piecewise quadratic FUNCTION,not interpolated returned samples.
namespace regrip_yield_front {
using Real=long double;
using Poly=std::array<Real,3>;
inline Real value(const Poly&p,Real x){return p[0]+x*(p[1]+x*p[2]);}
inline bool finite(const Poly&p){return std::all_of(p.begin(),p.end(),[](Real x){return std::isfinite(x);});}
struct Segment{Real lo=-1,hi=1;Poly elastic{};};
struct Measures{
 Real oldEnergy=0,energy=0,traction=0,dissipation=0,endpointProjection=0,inputWork=0,tangent=0,cappedLength=0;
 Poly generalizedTraction{};std::array<Real,9>tangentMatrix{};bool tangentIsUnique=true;
 const std::array<Real,9>&classicalTangent()const{if(!tangentIsUnique)throw std::domain_error("whole-interval yield event needs directional/semismooth treatment");return tangentMatrix;}
};
struct Trial{std::uint64_t epoch=0;std::vector<Segment>next;Measures measures;};
inline std::vector<Real> roots(Poly p){
 if(!finite(p))throw std::overflow_error("nonfinite yield polynomial");
 if(p[2]==0){if(p[1]==0)return {};return {-p[0]/p[1]};}
 Real d=p[1]*p[1]-4*p[2]*p[0];if(!std::isfinite(d))throw std::overflow_error("yield discriminant overflow");if(d<0)return {};
 Real q=-.5L*(p[1]+std::copysign(std::sqrt(d),p[1]));if(q==0)return {0};
 return {q/p[2],p[0]/q};
}
class Field {
 Real halfLength,stiffness;std::uint64_t epoch_=0;std::vector<Segment>state{{-1,1,{0,0,0}}};
public:
 Field(Real a,Real k):halfLength(a),stiffness(k){if(!std::isfinite(a)||!std::isfinite(k)||a<=0||k<=0)throw std::invalid_argument("positive finite material length/stiffness required");}
 std::uint64_t epoch()const{return epoch_;}
 std::size_t pieces()const{return state.size();}
 Real elasticAt(Real x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("material coordinate");
  for(const auto&s:state)if(x<=s.hi)return value(s.elastic,x);
  throw std::logic_error("material history gap");
 }
 Trial evaluate(Poly increment,Real capacity)const{
  if(!finite(increment)||!std::isfinite(capacity)||capacity<0)throw std::invalid_argument("finite increment/nonnegative capacity required");
  Trial out;out.epoch=epoch_;Poly cap{capacity,0,-capacity};Real node=std::sqrt(3.L/5);Real nodes[3]={-node,0,node},weights[3]={5.L/9,8.L/9,5.L/9};
  for(const auto&old:state){
   Poly trial;for(unsigned j=0;j<3;++j)trial[j]=old.elastic[j]+increment[j];if(!finite(trial))throw std::overflow_error("elastic trial overflow");
   std::vector<Real>knots{old.lo,old.hi};
   for(int sign:{-1,1}){Poly yield;for(unsigned j=0;j<3;++j)yield[j]=stiffness*trial[j]-sign*cap[j];if(capacity>0&&yield==Poly{0,0,0})out.measures.tangentIsUnique=false;for(Real r:roots(yield))if(std::isfinite(r)&&r>old.lo&&r<old.hi)knots.push_back(r);}
   std::sort(knots.begin(),knots.end());knots.erase(std::unique(knots.begin(),knots.end()),knots.end());
   for(unsigned i=1;i<knots.size();++i){Real lo=knots[i-1],hi=knots[i];if(hi==lo)continue;Real mid=(lo+hi)/2,load=stiffness*value(trial,mid),limit=value(cap,mid);int sign=load>limit?1:load< -limit?-1:0;
    // At C==0 the return operator is IDENTICALLY zero,including at rest.
    // Its derivative is0,not the stick-side derivative used at a positive
    // Coulomb limit. No epsilon capacity or arbitrary force regularization.
    bool limited=sign!=0||capacity==0;
    Poly next=trial;if(limited)for(unsigned j=0;j<3;++j)next[j]=sign*cap[j]/stiffness;if(!finite(next))throw std::overflow_error("returned elastic field overflow");
    if(!out.next.empty()&&out.next.back().elastic==next&&out.next.back().hi==lo)out.next.back().hi=hi;else out.next.push_back({lo,hi,next});
    if(out.next.size()>8192)throw std::length_error("bounded exact scalar history pieces");
    if(limited)out.measures.cappedLength+=halfLength*(hi-lo);else out.measures.tangent+=halfLength*(hi-lo)*stiffness;
    for(unsigned q=0;q<3;++q){Real x=mid+(hi-lo)*nodes[q]/2,w=halfLength*(hi-lo)*weights[q]/2,e0=value(old.elastic,x),e=value(next,x),du=value(increment,x),plastic=limited?value(trial,x)-e:0,C=value(cap,x);
     out.measures.oldEnergy+=w*.5L*stiffness*e0*e0;out.measures.energy+=w*.5L*stiffness*e*e;out.measures.traction+=w*stiffness*e;
     out.measures.dissipation+=w*C*std::abs(plastic);out.measures.endpointProjection+=w*.5L*stiffness*(e-e0)*(e-e0);out.measures.inputWork+=w*stiffness*e*du;
     Real basis[3]={1,x,x*x};for(unsigned row=0;row<3;++row){out.measures.generalizedTraction[row]+=w*stiffness*e*basis[row];if(!limited)for(unsigned col=row;col<3;++col)out.measures.tangentMatrix[3*row+col]+=w*stiffness*basis[row]*basis[col];}
    }
   }
  }
  for(unsigned row=0;row<3;++row)for(unsigned col=0;col<row;++col)out.measures.tangentMatrix[3*row+col]=out.measures.tangentMatrix[3*col+row];
  if(out.next.empty()||out.next.front().lo!= -1||out.next.back().hi!=1)throw std::logic_error("incomplete material partition");
  for(Real x:{out.measures.energy,out.measures.traction,out.measures.dissipation,out.measures.endpointProjection,out.measures.inputWork})if(!std::isfinite(x))throw std::overflow_error("integrated material quantity overflow");
  return out;
 }
 void commit(const Trial&t){
  if(t.epoch!=epoch_)throw std::invalid_argument("stale/double material Commit");
  if(t.next.empty()||t.next.size()>8192||t.next.front().lo!= -1||t.next.back().hi!=1)throw std::invalid_argument("invalid committed material partition");
  Real previous=-1;for(const auto&s:t.next){if(!finite(s.elastic)||!std::isfinite(s.lo)||!std::isfinite(s.hi)||s.lo!=previous||s.hi<=s.lo)throw std::invalid_argument("invalid committed material segment");previous=s.hi;}
  state=t.next;++epoch_;
 }
};
}
