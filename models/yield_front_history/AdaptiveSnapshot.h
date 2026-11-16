#pragma once
#include "VectorReturn.h"
#include "PolynomialFronts.h"
#include <algorithm>
#include <functional>
#include <vector>

namespace regrip_vector_history {
// Independent compression experiment,NOT a production replacement. A snapshot
// is a material-coordinate function,not moving quadrature samples. Cubic vector
// interpolation is followed by ONE coupled circular projection,never component
// clipping. Representation-energy changes must be audited separately,not heat.
class AdaptiveSnapshot {
public:
 struct Cell {R lo,hi;std::array<V,4>values;};
 std::vector<Cell>cells;
 R k,C,maxObservedStateError=0;
 std::size_t sourceQueries=0;
 static V polynomial(const Cell&cell,R x){
  R u=(x-cell.lo)/(cell.hi-cell.lo);V v{};
  for(int i=0;i<4;++i){R w=1;for(int j=0;j<4;++j)if(i!=j)w*=(3*u-j)/R(i-j);v=add(v,scale(cell.values[i],w));}
  return v;
 }
 V admissible(const Cell&cell,R x)const{
  V v=polynomial(cell,x);R length=norm(v),limit=C*(1-x*x)/k;
  if(length>limit)v=scale(v,limit/length);
  return v;
 }
 V at(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("snapshot coordinate");
  auto cell=std::lower_bound(cells.begin(),cells.end(),x,[](const Cell&c,R p){return c.hi<p;});
  if(cell==cells.end())throw std::logic_error("snapshot partition");
  return admissible(*cell,x);
 }
 bool onYield(R x)const{
  auto cell=std::lower_bound(cells.begin(),cells.end(),x,[](const Cell&c,R p){return c.hi<p;});
  if(cell==cells.end()||x< -1||!std::isfinite(x))throw std::invalid_argument("snapshot yield coordinate");
  R cap=C*(1-x*x);return cap>0&&k*norm(polynomial(*cell,x))>=cap;
 }
 R cellLipschitz(const Cell&c)const{
   V p1{},p2{},p3{};R b1[4]={-5.5L,9,-4.5L,1},b2[4]={9,-22.5L,18,-4.5L},b3[4]={-4.5L,13.5L,-13.5L,4.5L};
   for(int j=0;j<4;++j){p1=add(p1,scale(c.values[j],b1[j]));p2=add(p2,scale(c.values[j],b2[j]));p3=add(p3,scale(c.values[j],b3[j]));}
   return (norm(p1)+2*norm(p2)+3*norm(p3))/(c.hi-c.lo)+2*C/k;
 }
 R lipschitzBound()const{
  R maximum=0;for(const auto&c:cells)maximum=std::max(maximum,cellLipschitz(c));return maximum;
 }
 R localBound(R lo,R hi)const{
  R maximum=0;for(const auto&c:cells)if(c.hi>lo&&c.lo<hi)maximum=std::max(maximum,cellLipschitz(c));return maximum;
 }
 std::vector<R>knots()const{
  std::vector<R>v{-1};for(const auto&c:cells)v.push_back(c.hi);return v;
 }
 std::vector<R>yieldKnots(V increment)const{
  // Restricted exact-algebra candidate:constant vector increment,unchanged
  // parabolic capacity,fixed normal. NOT pressure-change/birth/3DCCD roots.
  // Inside an unprojected cubic cell yield is degree6. In a projected cell,
  // squaring 2*c*(p.d)/|p|+k*|d|²=0 gives degree10;reject its opposite-sign
  // roots. All values below are CELL-LOCAL to avoid global-x cancellation.
  finite(increment);using P=std::vector<R>;
  auto multiply=[](const P&a,const P&b){P r(a.size()+b.size()-1);for(std::size_t i=0;i<a.size();++i)for(std::size_t j=0;j<b.size();++j)r[i+j]+=a[i]*b[j];return r;};
  auto combine=[](P a,const P&b,R factor){a.resize(std::max(a.size(),b.size()));for(std::size_t j=0;j<b.size();++j)a[j]+=factor*b[j];return a;};
  std::vector<R>result{-1};R du2=dot(increment,increment);
  for(const auto&c:cells){
   std::array<V,4>p{c.values[0],V{},V{},V{}};R b1[4]={-5.5L,9,-4.5L,1},b2[4]={9,-22.5L,18,-4.5L},b3[4]={-4.5L,13.5L,-13.5L,4.5L};
   for(int j=0;j<4;++j){p[1]=add(p[1],scale(c.values[j],b1[j]));p[2]=add(p[2],scale(c.values[j],b2[j]));p[3]=add(p[3],scale(c.values[j],b3[j]));}
   R width=c.hi-c.lo;P cap{C*(1-c.lo*c.lo),-2*C*c.lo*width,-C*width*width};P cap2=multiply(cap,cap),norm2(7),pd(4);
   for(int i=0;i<4;++i){pd[i]=dot(p[i],increment);for(int j=0;j<4;++j)norm2[i+j]+=dot(p[i],p[j]);}
   P mask=cap2;for(auto&v:mask)v=-v;mask=combine(mask,norm2,k*k);
   auto oldFronts=polynomialFronts(mask,0,1);std::vector<R>oldKnots{0};oldKnots.insert(oldKnots.end(),oldFronts.begin(),oldFronts.end());oldKnots.push_back(1);
   P unprojected=mask;unprojected=combine(unprojected,pd,2*k*k);unprojected[0]+=k*k*du2;
   P projected=multiply(cap2,multiply(pd,pd));for(auto&v:projected)v*=4;projected=combine(projected,norm2,-k*k*du2*du2);
   for(std::size_t j=1;j<oldKnots.size();++j){R lo=oldKnots[j-1],hi=oldKnots[j],mid=(lo+hi)/2;
    bool capped=regrip_vector_history::polynomial(mask,mid)>0;auto fronts=polynomialFronts(capped?projected:unprojected,lo,hi);
    for(R u:fronts)if(!capped||regrip_vector_history::polynomial(pd,u)<0)result.push_back(c.lo+width*u);
    result.push_back(c.lo+width*hi);
   }
  }
  result.back()=1;std::sort(result.begin(),result.end());result.erase(std::unique(result.begin(),result.end()),result.end());return result;
 }
 AdaptiveSnapshot(const std::function<V(R)>&source,R stiffness,R capacity,R stateAbsolute,
                  const std::vector<V>&futureProbes,R probeLossDensityAbsolute,std::size_t maxCells=8192):k(stiffness),C(capacity){
  radialReturn({}, {},{0,0,1},k,C);
  if(stateAbsolute<=0||!std::isfinite(stateAbsolute)||probeLossDensityAbsolute<=0||!std::isfinite(probeLossDensityAbsolute)||maxCells==0)throw std::invalid_argument("snapshot error budgets");
  auto query=[&](R x){if(++sourceQueries>1000000)throw std::length_error("snapshot source-query budget");V v=source(x);finite(v);return v;};
  auto build=[&](auto&&self,R lo,R hi,unsigned depth)->void{
   Cell cell;cell.lo=lo;cell.hi=hi;for(int j=0;j<4;++j)cell.values[j]=query(lo+(hi-lo)*j/3);
   bool accept=true;R maximum=0;
   // Withheld points are distinct from the interpolation nodes. Prospective
   // return loss is tested separately from force/state error,so a visually
   // accurate field cannot silently approve a poorly represented slip front.
   for(int j=0;j<13;++j){R x=lo+(hi-lo)*(R(j)+.5L)/13;V exact=query(x),fit=admissible(cell,x);
    R error=norm(add(fit,scale(exact,-1)));maximum=std::max(maximum,error);
    // The first independent dense test exceeded the sampled target by4.6%.
    // Tighten the ESTIMATOR by2,not the unchanged withheld state/loss gates.
    // This safety margin is not a continuous-norm error certificate.
    if(error>stateAbsolute/2)accept=false;
    for(V du:futureProbes){auto a=radialReturn(exact,du,{0,0,1},k,C*(1-x*x)),b=radialReturn(fit,du,{0,0,1},k,C*(1-x*x));if(std::abs(a.loss-b.loss)>probeLossDensityAbsolute)accept=false;}
   }
   if(accept){if(cells.size()>=maxCells)throw std::length_error("snapshot cell budget");cells.push_back(cell);maxObservedStateError=std::max(maxObservedStateError,maximum);return;}
   R mid=(lo+hi)/2;if(depth>=40||mid==lo||mid==hi)throw std::runtime_error("snapshot unresolved front");
   self(self,lo,mid,depth+1);self(self,mid,hi,depth+1);
  };
  build(build,-1,1,0);
 }
};
}
