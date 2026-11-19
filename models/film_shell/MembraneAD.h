#pragma once
#include "AD.h"
namespace regrip_film::compact {
// Compile-time nine-coordinate AD2 for a triangle. No runtime derivative
// mode, no gradient-only cache, and no change to the 27-DOF bending kernel.
struct AD9 {
 ADScalar v=0;std::array<ADScalar,9>g{};std::array<ADScalar,81>h{};bool constant=true;
 AD9(ADScalar value=0):v(value){}
 static AD9 variable(double value,int i){AD9 a(value);a.g.at(i)=1;a.constant=false;return a;}
};
inline AD9 operator+(const AD9&a,const AD9&b){AD9 r(a.v+b.v);r.constant=a.constant&&b.constant;if(!r.constant){for(int i=0;i<9;++i)r.g[i]=a.g[i]+b.g[i];for(int i=0;i<81;++i)r.h[i]=a.h[i]+b.h[i];}return r;}
inline AD9 operator-(const AD9&a,const AD9&b){AD9 r(a.v-b.v);r.constant=a.constant&&b.constant;if(!r.constant){for(int i=0;i<9;++i)r.g[i]=a.g[i]-b.g[i];for(int i=0;i<81;++i)r.h[i]=a.h[i]-b.h[i];}return r;}
inline AD9 operator*(const AD9&a,const AD9&b){if(a.constant||b.constant){const auto&c=a.constant?a:b;AD9 r=a.constant?b:a;r.v*=c.v;for(auto&v:r.g)v*=c.v;for(auto&v:r.h)v*=c.v;return r;}AD9 r(a.v*b.v);r.constant=false;for(int i=0;i<9;++i){r.g[i]=a.g[i]*b.v+a.v*b.g[i];for(int j=0;j<9;++j)r.h[9*i+j]=a.h[9*i+j]*b.v+a.v*b.h[9*i+j]+a.g[i]*b.g[j]+b.g[i]*a.g[j];}return r;}
inline AD expand(const AD9&a){AD r(a.v);r.constant=a.constant;for(int i=0;i<9;++i){r.g[i]=a.g[i];for(int j=0;j<9;++j)r.h[N*i+j]=a.h[9*i+j];}return r;}
inline AD triangle(const std::array<Vec<double>,3>&u,double sign,double dx,double dy,double thickness,double lambda,double mu){
 std::array<Vec<AD9>,3>p;for(int i=0;i<3;++i)for(int j=0;j<3;++j)p[i][j]=AD9::variable(u[i][j],3*i+j);
 auto a=scale(sub(p[1],p[0]),AD9(sign/dx)),b=scale(sub(p[2],p[0]),AD9(sign/dy));
 AD9 ex=a[0]+AD9(.5)*dot(a,a),ey=b[1]+AD9(.5)*dot(b,b),g=AD9(.5)*(a[1]+b[0]+dot(a,b)),tr=ex+ey;
 return expand(AD9(.5*dx*dy*thickness)*(AD9(.5*lambda)*tr*tr+AD9(mu)*(ex*ex+ey*ey+AD9(2)*g*g)));
}
}
