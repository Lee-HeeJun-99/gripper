#pragma once
#include <cmath>
#include <stdexcept>
// Independent 1D virgin scalar interface with a PRESCRIBED parabolic Coulomb
// capacity C(1-(s/a)^2). Not a Sphere geometry law or a SOFA history replacement.
namespace regrip_slip_band {
struct Integral{long double force=0,elastic=0,plastic=0,tangent=0,band=0;};
inline Integral reference(long double a,long double C,long double k,long double displacement){
 if(!std::isfinite(a)||!std::isfinite(C)||!std::isfinite(k)||a<=0||C<0||k<=0||!std::isfinite(displacement))throw std::invalid_argument("slip-band reference parameters");
 Integral r;if(C==0){r.band=displacement==0?0:a;return r;}long double d=std::abs(displacement),ratio=k*d/C;
 if(ratio>=1){r.force=4*a*C/3;r.elastic=8*a*C*C/(15*k);r.plastic=d*r.force-2*r.elastic;r.band=a;return r;}
 long double root=std::sqrt(1-ratio),y=ratio/(1+root),b=a*root;
 long double first=y*y-y*y*y/3,second=4*y*y*y/3-y*y*y*y+y*y*y*y*y/5;
 r.force=2*(k*d*b+C*a*first);r.elastic=(k*k*d*d*b+C*C*a*second)/k;
 r.plastic=2*a*(C*d*first-C*C*second/k);r.tangent=2*k*b;r.band=a*y;
 return r;
}
inline Integral splitGauss3(long double a,long double C,long double k,long double displacement){
 auto exact=reference(a,C,k,displacement);Integral r;r.band=exact.band;r.tangent=exact.tangent;if(C==0)return r;
 long double d=std::abs(displacement),b=a-r.band,q=std::sqrt(3.L/5),nodes[3]={-q,0,q},weights[3]={5.L/9,8.L/9,5.L/9};
 // Integrate each smooth branch. D is quartic here,so Gauss3 is exact in
 // exact arithmetic;no unresolved sub-grid slip band is sampled blindly.
 for(unsigned part=0;part<2;++part){long double lo=part?b:0,hi=part?a:b;if(hi<=lo)continue;
  for(unsigned j=0;j<3;++j){long double s=(lo+hi)/2+(hi-lo)*nodes[j]/2,cap=C*(1-s*s/(a*a)),traction=std::min(k*d,cap),plastic=d-traction/k,w=(hi-lo)*weights[j];r.force+=w*traction;r.elastic+=w*.5*traction*traction/k;r.plastic+=w*cap*plastic;}
 }
 return r;
}
}
