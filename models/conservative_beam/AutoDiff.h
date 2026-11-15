#pragma once
// Same exact12-dimensional Taylor algebra, constant propagation only.
// No derivative threshold, finite-difference force or dropped Hessian entry.
#include "../finite_rotation/Kernel.h"
namespace regrip_beam {
struct Jet:regrip3d::Jet{
 bool constant=true;
 Jet(double x=0):regrip3d::Jet(x){}
 static Jet variable(int i){Jet r;r.constant=false;r.g[i]=1;return r;}
};
inline Jet operator+(const Jet&a,const Jet&b){if(a.constant){Jet r=b;r.v+=a.v;return r;}if(b.constant){Jet r=a;r.v+=b.v;return r;}Jet r(a.v+b.v);r.constant=false;for(int i=0;i<12;++i)r.g[i]=a.g[i]+b.g[i];for(int i=0;i<144;++i)r.h[i]=a.h[i]+b.h[i];return r;}
inline Jet operator*(const Jet&a,const Jet&b){if(a.constant||b.constant){const Jet&c=a.constant?a:b;const Jet&x=a.constant?b:a;if(c.v==0)return Jet(0);Jet r=x;r.v*=c.v;for(double&v:r.g)v*=c.v;for(double&v:r.h)v*=c.v;return r;}Jet r(a.v*b.v);r.constant=false;for(int i=0;i<12;++i){r.g[i]=a.g[i]*b.v+a.v*b.g[i];for(int j=0;j<12;++j)r.h[12*i+j]=a.h[12*i+j]*b.v+a.v*b.h[12*i+j]+a.g[i]*b.g[j]+b.g[i]*a.g[j];}return r;}
inline Jet operator-(const Jet&a,const Jet&b){if(b.constant){Jet r=a;r.v-=b.v;return r;}return a+Jet(-1)*b;}
}
