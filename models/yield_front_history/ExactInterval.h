#pragma once
#include "AdaptiveSnapshot.h"
#include <boost/multiprecision/cpp_int.hpp>
#include <limits>
#include <cfenv>
#include <map>
#include <memory>
namespace regrip_vector_history {
using Q=boost::multiprecision::cpp_rational;
using QP=std::vector<Q>;
inline Q binaryRational(R x){
 if(!std::isfinite(x))throw std::invalid_argument("finite rational input");
 if(x==0)return 0;
 int exponent=0;R fraction=std::frexp(x,&exponent);constexpr int bits=std::numeric_limits<R>::digits;
 boost::multiprecision::cpp_int mantissa(std::ldexp(fraction,bits));Q q(mantissa);int shift=exponent-bits;
 if(shift>=0)q*=boost::multiprecision::cpp_int(1)<<shift;
 else q/=boost::multiprecision::cpp_int(1)<<(-shift);
 return q;
}
inline unsigned long long choose(unsigned n,unsigned k){unsigned long long c=1;for(unsigned j=1;j<=k;++j)c=c*(n-j+1)/j;return c;}
inline QP product(const QP&a,const QP&b){QP p(a.size()+b.size()-1);for(unsigned i=0;i<a.size();++i)for(unsigned j=0;j<b.size();++j)p[i+j]+=a[i]*b[j];return p;}
inline QP sum(QP a,const QP&b,const Q&factor){a.resize(std::max(a.size(),b.size()));for(unsigned j=0;j<b.size();++j)a[j]+=factor*b[j];return a;}
enum class PolynomialSign {Zero,Nonnegative,Nonpositive,Mixed};
inline PolynomialSign bernsteinSign(const QP&p,Q lo,Q hi){
 if(hi<=lo)throw std::invalid_argument("positive rational interval");
 unsigned n=unsigned(p.size()-1);QP power(n+1),lowPowers(n+1,1),widthPowers(n+1,1);
 for(unsigned j=1;j<=n;++j){lowPowers[j]=lowPowers[j-1]*lo;widthPowers[j]=widthPowers[j-1]*(hi-lo);}
 for(unsigned j=0;j<=n;++j)for(unsigned i=j;i<=n;++i)power[j]+=p[i]*choose(i,j)*lowPowers[i-j]*widthPowers[j];
 bool positive=false,negative=false;
 for(unsigned i=0;i<=n;++i){Q b=0;for(unsigned j=0;j<=i;++j)b+=power[j]*choose(i,j)/choose(n,j);positive=positive||b>0;negative=negative||b<0;}
 if(!positive&&!negative)return PolynomialSign::Zero;
 if(!negative)return PolynomialSign::Nonnegative;
 if(!positive)return PolynomialSign::Nonpositive;
 return PolynomialSign::Mixed;
}
enum class CellRegime {StickOrBoundary,SlipOrBoundary,WholeYieldEquality,Unknown};
class IdealYieldState {
 std::shared_ptr<const AdaptiveSnapshot>snapshot;
 mutable std::map<R,bool>memo;
 mutable std::vector<R>projectionPartition;
 struct CertainRange {R lo,hi;bool yielded;};
 mutable std::vector<CertainRange>certainRanges;
 static void isolate(const QP&p,const Q&lo,const Q&hi,const Q&origin,const Q&width,std::vector<R>&out,std::size_t&nodes,std::vector<CertainRange>*ranges=nullptr){
  if(++nodes>200000)throw std::length_error("bounded exact projection-front isolation");
  auto sign=bernsteinSign(p,lo,hi);
  if(sign!=PolynomialSign::Mixed){
   if(ranges){Q xl=origin+width*lo,xh=origin+width*hi;R l=xl.convert_to<R>(),r=xh.convert_to<R>();
    // INWARD bounds:only open interior points inherit the exact sign.
    // Boundary/uncertain points always fall back to exact point evaluation.
    if(binaryRational(l)<xl)l=std::nextafter(l,std::numeric_limits<R>::infinity());
    if(binaryRational(r)>xh)r=std::nextafter(r,-std::numeric_limits<R>::infinity());
    if(l<r)ranges->push_back({l,r,sign!=PolynomialSign::Nonpositive});
   }
   return;
  }
  Q xl=origin+width*lo,xh=origin+width*hi;
  if(xh-xl<=binaryRational(1e-12L)){
   R l=xl.convert_to<R>(),r=xh.convert_to<R>();
   if(binaryRational(l)>xl)l=std::nextafter(l,-std::numeric_limits<R>::infinity());
   if(binaryRational(r)<xh)r=std::nextafter(r,std::numeric_limits<R>::infinity());
   out.push_back(l);out.push_back(r);return;
  }
  Q mid=(lo+hi)/2;isolate(p,lo,mid,origin,width,out,nodes,ranges);isolate(p,mid,hi,origin,width,out,nodes,ranges);
 }
public:
 explicit IdealYieldState(std::shared_ptr<const AdaptiveSnapshot>s):snapshot(std::move(s)){}
 bool uncachedAt(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("ideal yield coordinate");
  auto cell=std::lower_bound(snapshot->cells.begin(),snapshot->cells.end(),x,[](const auto&c,R p){return c.hi<p;});
  Q qx=binaryRational(x),u=(qx-binaryRational(cell->lo))/(binaryRational(cell->hi)-binaryRational(cell->lo));
  std::array<Q,3>p{};for(int i=0;i<4;++i){Q w=1;for(int j=0;j<4;++j)if(i!=j)w*=(3*u-j)/Q(i-j);for(int axis=0;axis<3;++axis)p[axis]+=w*binaryRational(cell->values[i][axis]);}
  Q norm2=0;for(auto v:p)norm2+=v*v;Q cap=binaryRational(snapshot->C)*(1-qx*qx),k=binaryRational(snapshot->k);
  bool yielded=cap>0&&k*k*norm2>=cap*cap;
  return yielded;
 }
 bool at(R x)const{
  if(!std::isfinite(x)||x< -1||x>1)throw std::invalid_argument("ideal yield coordinate");
  auto found=memo.find(x);if(found!=memo.end())return found->second;
  auto range=std::lower_bound(certainRanges.begin(),certainRanges.end(),x,[](const auto&r,R p){return r.hi<=p;});
  bool yielded=(range!=certainRanges.end()&&x>range->lo&&x<range->hi)?range->yielded:uncachedAt(x);
  if(memo.size()<131072)memo.emplace(x,yielded);
  return yielded;
 }
 std::vector<R>tangentKnots(V direction)const{
  if(norm(direction)==0)return snapshot->knots();
  std::vector<R>result=snapshot->knots();std::size_t nodes=0;
  for(const auto&cell:snapshot->cells){
   std::array<std::array<Q,3>,4>p{};Q b1[4]={Q(-11)/2,9,Q(-9)/2,1},b2[4]={9,Q(-45)/2,18,Q(-9)/2},b3[4]={Q(-9)/2,Q(27)/2,Q(-27)/2,Q(9)/2};
   for(int axis=0;axis<3;++axis){p[0][axis]=binaryRational(cell.values[0][axis]);for(int j=0;j<4;++j){Q v=binaryRational(cell.values[j][axis]);p[1][axis]+=b1[j]*v;p[2][axis]+=b2[j]*v;p[3][axis]+=b3[j]*v;}}
   Q origin=binaryRational(cell.lo),width=binaryRational(cell.hi)-origin,k=binaryRational(snapshot->k),C=binaryRational(snapshot->C);
   QP cap{C*(1-origin*origin),-2*C*origin*width,-C*width*width},norm2(7),dotDirection(4);
   for(int axis=0;axis<3;++axis)for(int i=0;i<4;++i){dotDirection[i]+=p[i][axis]*binaryRational(direction[axis]);for(int j=0;j<4;++j)norm2[i+j]+=p[i][axis]*p[j][axis];}
   if(projectionPartition.empty()){
    QP mask=product(cap,cap);for(auto&v:mask)v=-v;mask=sum(mask,norm2,k*k);
    isolate(mask,0,1,origin,width,result,nodes,&certainRanges);
   }
   isolate(dotDirection,0,1,origin,width,result,nodes);
  }
  if(projectionPartition.empty())projectionPartition=result;
  else result.insert(result.end(),projectionPartition.begin(),projectionPartition.end());
  std::sort(result.begin(),result.end());result.erase(std::unique(result.begin(),result.end()),result.end());return result;
 }
};
// EXACT sign certificate for the IDEAL cubic/radial-projection function with
// its finite binary input data. It does NOT certify rounding in the existing
// long-double evaluator. Never inject it as a zero-loss override in SOFA.
inline CellRegime certifyIdealCell(const AdaptiveSnapshot::Cell&cell,R stiffness,R capacity,V increment,R lo,R hi){
 if(lo<cell.lo||hi>cell.hi||hi<=lo||capacity<=0||stiffness<=0)throw std::invalid_argument("single positive-capacity cubic cell");
 Q k=binaryRational(stiffness),C=binaryRational(capacity),origin=binaryRational(cell.lo),width=binaryRational(cell.hi)-origin;
 std::array<std::array<Q,3>,4>p{};Q b1[4]={Q(-11)/2,9,Q(-9)/2,1},b2[4]={9,Q(-45)/2,18,Q(-9)/2},b3[4]={Q(-9)/2,Q(27)/2,Q(-27)/2,Q(9)/2};
 for(int axis=0;axis<3;++axis){p[0][axis]=binaryRational(cell.values[0][axis]);for(int j=0;j<4;++j){Q v=binaryRational(cell.values[j][axis]);p[1][axis]+=b1[j]*v;p[2][axis]+=b2[j]*v;p[3][axis]+=b3[j]*v;}}
 QP cap{C*(1-origin*origin),-2*C*origin*width,-C*width*width};QP norm2(7),pd(4);Q du2=0;
 for(int axis=0;axis<3;++axis){Q d=binaryRational(increment[axis]);du2+=d*d;for(int i=0;i<4;++i){pd[i]+=p[i][axis]*d;for(int j=0;j<4;++j)norm2[i+j]+=p[i][axis]*p[j][axis];}}
 if(du2==0)return CellRegime::StickOrBoundary;
 QP cap2=product(cap,cap),mask=cap2;for(auto&x:mask)x=-x;mask=sum(mask,norm2,k*k);
 Q left=(binaryRational(lo)-origin)/width,right=(binaryRational(hi)-origin)/width;
 auto old=bernsteinSign(mask,left,right);
 if(old==PolynomialSign::Mixed)return CellRegime::Unknown;
 if(old==PolynomialSign::Nonpositive||old==PolynomialSign::Zero){
  QP yield=sum(mask,pd,2*k*k);yield[0]+=k*k*du2;
  auto sign=bernsteinSign(yield,left,right);
  if(sign==PolynomialSign::Zero)return CellRegime::WholeYieldEquality;
  if(sign==PolynomialSign::Nonpositive)return CellRegime::StickOrBoundary;
  if(sign==PolynomialSign::Nonnegative)return CellRegime::SlipOrBoundary;
  return CellRegime::Unknown;
 }
 auto direction=bernsteinSign(pd,left,right);
 if(direction==PolynomialSign::Nonnegative||direction==PolynomialSign::Zero)return CellRegime::SlipOrBoundary;
 if(direction==PolynomialSign::Mixed)return CellRegime::Unknown;
 QP squared=product(cap2,product(pd,pd));for(auto&x:squared)x*=4;squared=sum(squared,norm2,-k*k*du2*du2);
 auto sign=bernsteinSign(squared,left,right);
 if(sign==PolynomialSign::Zero)return CellRegime::WholeYieldEquality;
 if(sign==PolynomialSign::Nonnegative)return CellRegime::StickOrBoundary;
 if(sign==PolynomialSign::Nonpositive)return CellRegime::SlipOrBoundary;
 return CellRegime::Unknown;
}
inline R certifiedStickDensityError(const AdaptiveSnapshot&snapshot,V increment,R lo,R hi){
 // Restricted fixed-normal reference implementation,round-to-nearest,normal
 // arithmetic only. Unknown regimes return -1,never an invented zero loss.
 if(std::fegetround()!=FE_TONEAREST||!std::numeric_limits<R>::is_iec559)return -1;
 auto cell=std::lower_bound(snapshot.cells.begin(),snapshot.cells.end(),lo,[](const auto&c,R p){return c.hi<p;});
 if(cell==snapshot.cells.end()||hi>cell->hi||hi<=lo)return -1;
 if(lo<=-1||hi>=1)return -1; // zero-capacity endpoint needs its own analysis
 R M=0;for(V v:cell->values)M=std::max(M,norm(v));
 R magnitude=M+norm(increment)+snapshot.C/snapshot.k;
 if(magnitude<1e-100L||magnitude>1e100L||snapshot.k<1e-100L||snapshot.k>1e100L||snapshot.C<1e-100L||snapshot.C>1e100L||cell->hi-cell->lo<1e-100L)return -1;
 auto regime=certifyIdealCell(*cell,snapshot.k,snapshot.C,increment,lo,hi);
 if(regime!=CellRegime::StickOrBoundary&&regime!=CellRegime::WholeYieldEquality)return -1;
 // Error path expansion for the IMPLEMENTED four-node cubic evaluation:
 // |factor|<=3;three-factor weight abs error<=gamma1024;four products/sums
 // give vector interpolation error<=gamma16384*M. Nonexpansive ball return,
 // radius evaluation,norm/division/scaling and final plastic subtraction
 // are covered by gamma65536*(M+|d|+C/k). See the separate derivation note.
 // This is a rounding-density inventory,NOT Coulomb heat or an absolute
 // cutoff. It is summed into the SAME requested integral error budget.
 R epsilon=std::numeric_limits<R>::epsilon();
 R gamma=65536*epsilon/(1-65536*epsilon),capError=64*epsilon/(1-64*epsilon)*snapshot.C;
 return (snapshot.C+capError)*gamma*magnitude;
}
}
