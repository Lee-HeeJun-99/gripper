#pragma once
#include <array>
#include <cmath>
#include <stdexcept>
namespace regrip_film {
constexpr int N=27;
inline thread_local bool filmHessianEnabled=true;
struct DerivativeOrderGuard {
 bool previous;
 explicit DerivativeOrderGuard(bool hessian):previous(filmHessianEnabled){filmHessianEnabled=hessian;}
 ~DerivativeOrderGuard(){filmHessianEnabled=previous;}
 DerivativeOrderGuard(const DerivativeOrderGuard&)=delete;
};
struct AD {
 double v=0;std::array<double,N>g{};std::array<double,N*N>h{};bool constant=true;
 AD(double value=0):v(value){}
 static AD variable(double value,int i){AD a(value);a.g.at(i)=1;a.constant=false;return a;}
};
inline AD operator+(const AD&a,const AD&b){AD r(a.v+b.v);r.constant=a.constant&&b.constant;if(!r.constant){for(int i=0;i<N;++i)r.g[i]=a.g[i]+b.g[i];if(filmHessianEnabled)for(int i=0;i<N*N;++i)r.h[i]=a.h[i]+b.h[i];}return r;}
inline AD operator-(const AD&a,const AD&b){AD r(a.v-b.v);r.constant=a.constant&&b.constant;if(!r.constant){for(int i=0;i<N;++i)r.g[i]=a.g[i]-b.g[i];if(filmHessianEnabled)for(int i=0;i<N*N;++i)r.h[i]=a.h[i]-b.h[i];}return r;}
inline AD operator*(const AD&a,const AD&b){if(a.constant||b.constant){const auto&c=a.constant?a:b;AD r=a.constant?b:a;r.v*=c.v;for(auto&v:r.g)v*=c.v;if(filmHessianEnabled)for(auto&v:r.h)v*=c.v;return r;}AD r(a.v*b.v);r.constant=false;for(int i=0;i<N;++i){r.g[i]=a.g[i]*b.v+a.v*b.g[i];if(filmHessianEnabled)for(int j=0;j<N;++j)r.h[N*i+j]=a.h[N*i+j]*b.v+a.v*b.h[N*i+j]+a.g[i]*b.g[j]+b.g[i]*a.g[j];}return r;}
inline AD unary(const AD&a,double f,double d,double dd){AD r(f);r.constant=a.constant;if(!a.constant)for(int i=0;i<N;++i){r.g[i]=d*a.g[i];if(filmHessianEnabled)for(int j=0;j<N;++j)r.h[N*i+j]=d*a.h[N*i+j]+dd*a.g[i]*a.g[j];}return r;}
inline AD inverse(const AD&a){if(a.v==0)throw std::domain_error("zero inverse");return unary(a,1/a.v,-1/(a.v*a.v),2/(a.v*a.v*a.v));}
inline AD root(const AD&a){if(a.v<=0)throw std::domain_error("degenerate film normal");double s=std::sqrt(a.v);return unary(a,s,.5/s,-.25/(a.v*s));}
template<class T>using Vec=std::array<T,3>;
template<class T>inline Vec<T>add(const Vec<T>&a,const Vec<T>&b){return {a[0]+b[0],a[1]+b[1],a[2]+b[2]};}
template<class T>inline Vec<T>sub(const Vec<T>&a,const Vec<T>&b){return {a[0]-b[0],a[1]-b[1],a[2]-b[2]};}
template<class T>inline Vec<T>scale(const Vec<T>&a,T c){return {a[0]*c,a[1]*c,a[2]*c};}
template<class T>inline T dot(const Vec<T>&a,const Vec<T>&b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
template<class T>inline Vec<T>cross(const Vec<T>&a,const Vec<T>&b){return {a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};}
}
