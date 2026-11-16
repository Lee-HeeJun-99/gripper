#pragma once
#include "VectorReturn.h"
#include <algorithm>
#include <vector>
namespace regrip_vector_history {
// Recursive derivative isolation for a real polynomial on a closed interval.
// No epsilon capacity,sign smoothing or imaginary-root projection. Repeated
// roots are included only when the evaluated critical value is exactly zero;
// the separate Lipschitz unresolved-loss guard remains necessary. This is not
// a certified interval-arithmetic polynomial solver.
inline R polynomial(const std::vector<R>&p,R x){R v=0;for(auto i=p.rbegin();i!=p.rend();++i)v=v*x+*i;return v;}
inline std::vector<R> polynomialFronts(std::vector<R>p,R lo,R hi){
 for(R c:p)if(!std::isfinite(c))throw std::invalid_argument("yield polynomial coefficient");
 while(p.size()>1&&p.back()==0)p.pop_back();
 if(p.size()<2)return {};
 if(p.size()==2){R x=-p[0]/p[1];return x>lo&&x<hi?std::vector<R>{x}:std::vector<R>{};}
 std::vector<R>d(p.size()-1);for(std::size_t i=1;i<p.size();++i)d[i-1]=i*p[i];
 auto critical=polynomialFronts(d,lo,hi);std::vector<R>knots{lo};knots.insert(knots.end(),critical.begin(),critical.end());knots.push_back(hi);
 std::vector<R>roots;
 for(R x:critical)if(polynomial(p,x)==0)roots.push_back(x);
 for(std::size_t i=1;i<knots.size();++i){R l=knots[i-1],r=knots[i],fl=polynomial(p,l),fr=polynomial(p,r);
  if(fl==0||fr==0||(fl>0)==(fr>0))continue;
  for(unsigned iter=0;iter<160;++iter){R m=(l+r)/2;if(m==l||m==r)break;R fm=polynomial(p,m);if(fm==0){l=r=m;break;}if((fm>0)==(fl>0)){l=m;fl=fm;}else r=m;}
  roots.push_back((l+r)/2);
 }
 std::sort(roots.begin(),roots.end());roots.erase(std::unique(roots.begin(),roots.end()),roots.end());return roots;
}
}
