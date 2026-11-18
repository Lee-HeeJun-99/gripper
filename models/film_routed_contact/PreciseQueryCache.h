#pragma once
#include "../film_three_finger/PreciseDistanceOrder.h"
#include <vector>
namespace regrip_three_finger {
// One immutable geometry QUERY only. No cross-state cache/tolerance/key.
// Same Q/H values and subtraction order as preciseOrder;unresolved signs use
// the caller's ORIGINAL fallback/exception policy. Derivatives are untouched.
class PreciseQueryCache {
 using Q=boost::multiprecision::cpp_bin_float_quad;
 using H=boost::multiprecision::cpp_bin_float_100;
 const std::vector<TriangleCoordinates>&coordinates;
 std::vector<Q>low;std::vector<H>high;std::vector<unsigned char>ready;
 void fill(unsigned i){if(i>=ready.size())throw std::out_of_range("precise query index");if(!ready[i]){low[i]=preciseSquaredDistance<Q>(coordinates[i]);high[i]=preciseSquaredDistance<H>(coordinates[i]);ready[i]=1;++evaluations;}}
public:
 unsigned evaluations=0;
 explicit PreciseQueryCache(const std::vector<TriangleCoordinates>&x):coordinates(x),low(x.size()),high(x.size()),ready(x.size(),0){}
 template<class F>int compare(unsigned a,unsigned b,F&&originalFallback){
  fill(a);fill(b);Q l=low[a]-low[b];H h=high[a]-high[b];auto sign=[](const auto&x){return x>0?1:x<0?-1:0;};int ls=sign(l),hs=sign(h);
  if(ls!=hs)return originalFallback();return hs;
 }
};
}
