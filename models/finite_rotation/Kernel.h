#pragma once
// Exact local first/second derivatives, not a finite-difference force law.
// Local chart: p'=p+u, R'=Exp(w)R. Taylor expansion is exact through order two.
#include <array>
#include <cmath>
#include <stdexcept>
namespace regrip3d {
constexpr int N=12;
struct Jet {
 double v=0;std::array<double,N> g{};std::array<double,N*N> h{};
 Jet(double x=0):v(x){}
 static Jet variable(int i){Jet a;a.g[i]=1;return a;}
};
inline Jet operator+(const Jet&a,const Jet&b){Jet c(a.v+b.v);for(int i=0;i<N;++i)c.g[i]=a.g[i]+b.g[i];for(int i=0;i<N*N;++i)c.h[i]=a.h[i]+b.h[i];return c;}
inline Jet operator-(const Jet&a,const Jet&b){Jet c(a.v-b.v);for(int i=0;i<N;++i)c.g[i]=a.g[i]-b.g[i];for(int i=0;i<N*N;++i)c.h[i]=a.h[i]-b.h[i];return c;}
inline Jet operator*(const Jet&a,const Jet&b){Jet c(a.v*b.v);for(int i=0;i<N;++i){c.g[i]=a.g[i]*b.v+a.v*b.g[i];for(int j=0;j<N;++j)c.h[N*i+j]=a.h[N*i+j]*b.v+a.v*b.h[N*i+j]+a.g[i]*b.g[j]+b.g[i]*a.g[j];}return c;}
template<class T> using Vec=std::array<T,3>;
template<class T> Vec<T> add(const Vec<T>&a,const Vec<T>&b){return {a[0]+b[0],a[1]+b[1],a[2]+b[2]};}
template<class T> Vec<T> sub(const Vec<T>&a,const Vec<T>&b){return {a[0]-b[0],a[1]-b[1],a[2]-b[2]};}
template<class T> Vec<T> cross(const Vec<T>&a,const Vec<T>&b){return {a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};}
template<class T> T dot(const Vec<T>&a,const Vec<T>&b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
using V=Vec<double>;using Q=std::array<double,4>;
inline V rotate(const Q&q,const V&v){V a{q[0],q[1],q[2]};auto c=cross(a,v);auto cc=cross(a,c);return {v[0]+2*(q[3]*c[0]+cc[0]),v[1]+2*(q[3]*c[1]+cc[1]),v[2]+2*(q[3]*c[2]+cc[2])};}
inline Q multiply(const Q&a,const Q&b){V av{a[0],a[1],a[2]},bv{b[0],b[1],b[2]};auto c=cross(av,bv);return {a[3]*b[0]+b[3]*a[0]+c[0],a[3]*b[1]+b[3]*a[1]+c[1],a[3]*b[2]+b[3]*a[2]+c[2],a[3]*b[3]-dot(av,bv)};}
inline Q exp(const V&w){double a=std::sqrt(dot(w,w));double s=a<1e-12?.5:std::sin(a/2)/a;return {s*w[0],s*w[1],s*w[2],std::cos(a/2)};}
struct Pose{V p{};Q q{0,0,0,1};};
inline Pose increment(Pose p,int axis,double step){if(axis<3)p.p[axis]+=step;else {V w{};w[axis-3]=step;p.q=multiply(exp(w),p.q);}return p;}
inline void validate(const Pose&p){double n=0;for(double x:p.p)if(!std::isfinite(x))throw std::invalid_argument("nonfinite position");for(double x:p.q){if(!std::isfinite(x))throw std::invalid_argument("nonfinite quaternion");n+=x*x;}if(std::abs(n-1)>1e-8)throw std::invalid_argument("quaternion not unit");}
inline Vec<Jet> lifted(const V&v,int offset){Vec<Jet> a{v[0],v[1],v[2]},w{Jet::variable(offset),Jet::variable(offset+1),Jet::variable(offset+2)};auto c=cross(w,a);auto cc=cross(w,c);for(int i=0;i<3;++i)a[i]=a[i]+c[i]+Jet(.5)*cc[i];return a;}
struct Result{double energy=0,slip=0;std::array<double,N> force{};std::array<double,N*N> chart_hessian{},jacobian{};};
inline Result evaluate(const Pose&l,const Pose&u,double k,double h){
 validate(l);validate(u);if(!std::isfinite(k)||k<0||!std::isfinite(h)||h<=0)throw std::invalid_argument("invalid k/h");
 auto tangent=lifted(rotate(l.q,V{1,0,0}),3);
 auto al=lifted(rotate(l.q,V{0,0,h/2}),3),au=lifted(rotate(u.q,V{0,0,-h/2}),9);
 Vec<Jet> d;for(int i=0;i<3;++i)d[i]=Jet(u.p[i]-l.p[i])+Jet::variable(i+6)-Jet::variable(i);
 Jet s=dot(tangent,add(d,sub(au,al)));Jet e=Jet(.5*k)*s*s;
 Result r;r.energy=e.v;r.slip=s.v;r.chart_hessian=e.h;
 for(int i=0;i<N;++i){r.force[i]=-e.g[i];for(int j=0;j<N;++j)r.jacobian[N*i+j]=-e.h[N*i+j];}
 // Spatial force derivative differs from the symmetric chart Hessian by the
 // rotational connection term: Df=-H-0.5*skew(torque) on each rotation block.
 for(int o:{3,9}){double x=r.force[o],y=r.force[o+1],z=r.force[o+2];
  double skew[9]={0,-z,y,z,0,-x,-y,x,0};
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.jacobian[N*(o+i)+o+j]-=.5*skew[3*i+j];}
 for(double x:r.force)if(!std::isfinite(x))throw std::overflow_error("force overflow");
 for(double x:r.jacobian)if(!std::isfinite(x))throw std::overflow_error("tangent overflow");
 if(!std::isfinite(r.energy))throw std::overflow_error("energy overflow");
 return r;
}
} // namespace regrip3d
