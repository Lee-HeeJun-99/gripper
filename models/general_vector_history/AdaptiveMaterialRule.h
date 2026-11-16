#pragma once
#include "../closure/Quadrature.h"
#include <array>
#include <functional>
#include <sstream>

namespace regrip_general_history {
// Embedded quadrature ESTIMATOR, not a proof that an unsampled isolated patch
// cannot exist. In particular two zero sampled losses are not a yield-front
// certificate. Keep independent dense/front references in the qualification.
inline std::vector<std::pair<double,double>> adaptiveMaterialRule(
    unsigned cells, double length,
    const std::function<std::array<double,11>(double)> &density,
    double relative=1e-5) {
  if(!cells||!std::isfinite(length)||length<=0||relative<=0)
    throw std::invalid_argument("material rule parameters");
  const auto low=regrip_closure::gauss(8),high=regrip_closure::gauss(16);
  std::size_t evaluations=0;
  std::vector<std::pair<double,double>> result;
  auto integral=[&](double a,double b,const auto &rule){
    std::array<double,11> sum{};
    for(auto [x,w]:rule){
      if(++evaluations>200000)throw std::length_error("adaptive material quadrature budget");
      auto y=density((a+b)/2+(b-a)/2*x);
      for(unsigned j=0;j<sum.size();++j){
        if(!std::isfinite(y[j])||y[j]<0)throw std::invalid_argument("nonnegative finite error measures");
        sum[j]+=(b-a)/2*w*y[j];
      }
    }
    return sum;
  };
  // Global measure-scaled budgets, distributed by reference-material width.
  // A cell-local relative test cannot resolve a positive-part root: both its
  // integral and requested tolerance shrink together. No absolute heat floor.
  std::array<double,11> scale{};
  for(unsigned i=0;i<cells;++i){
    auto a=integral(double(i)/cells,double(i+1)/cells,low);
    auto b=integral(double(i)/cells,double(i+1)/cells,high);
    for(unsigned j=0;j<scale.size();++j)scale[j]+=std::max(a[j],b[j]);
  }
  // Force/moment are VECTOR error budgets, not relative errors against each
  // almost-zero coordinate component. Keep energy/loss inventories separate:
  // a tiny positive plastic loss is never replaced by a force-based scale.
  double forceScale=scale[3]+scale[4]+scale[5];
  double momentScale=scale[6]+scale[7]+scale[8];
  for(unsigned j=3;j<6;++j)scale[j]=forceScale;
  for(unsigned j=6;j<9;++j)scale[j]=momentScale;
  auto visit=[&](auto&&self,double a,double b,unsigned depth)->void{
    auto coarse=integral(a,b,low),fine=integral(a,b,high);bool accept=true;unsigned worst=0;
    for(unsigned j=0;j<fine.size();++j)
      if(std::abs(coarse[j]-fine[j])>relative*scale[j]*(b-a)){accept=false;worst=j;}
    if(accept){for(auto [x,w]:high)result.push_back({(a+b)/2+(b-a)/2*x,length*(b-a)/2*w});return;}
    double mid=(a+b)/2;
    if(depth>=24||mid==a||mid==b){std::ostringstream why;why<<"unresolved adaptive material front channel="<<worst<<" interval="<<a<<","<<b<<" difference="<<std::abs(coarse[worst]-fine[worst])<<" budget="<<relative*scale[worst]*(b-a)<<" global_measure="<<scale[worst];throw std::runtime_error(why.str());}
    self(self,a,mid,depth+1);self(self,mid,b,depth+1);
  };
  for(unsigned i=0;i<cells;++i)visit(visit,double(i)/cells,double(i+1)/cells,0);
  return result;
}
} // namespace regrip_general_history
