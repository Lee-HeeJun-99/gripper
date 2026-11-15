#pragma once
// Objective two-node, midpoint/reduced-integration Simo-Reissner research rod.
// Spatial chart: x'=x+u, Q'=Exp(w)Q. Exact derivatives through order two.
#include "../finite_rotation/Kernel.h"
#include <algorithm>
namespace regrip_beam {
using namespace regrip3d;
inline Jet unary(const Jet&a,double f,double d,double dd){Jet r(f);for(int i=0;i<N;++i){r.g[i]=d*a.g[i];for(int j=0;j<N;++j)r.h[N*i+j]=d*a.h[N*i+j]+dd*a.g[i]*a.g[j];}return r;}
inline Jet inverse(const Jet&a){if(a.v<=0)throw std::domain_error("positive inverse required");return unary(a,1/a.v,-1/(a.v*a.v),2/(a.v*a.v*a.v));}
inline Jet root(const Jet&a){if(a.v<=0)throw std::domain_error("positive sqrt required");double s=std::sqrt(a.v);return unary(a,s,.5/s,-.25/(a.v*s));}
inline Jet arcsin(const Jet&a){if(std::abs(a.v)>=1)throw std::domain_error("asin branch");double d=1/std::sqrt(1-a.v*a.v);return unary(a,std::asin(a.v),d,a.v*d*d*d);}
using JQ=std::array<Jet,4>;
inline JQ product(const JQ&a,const JQ&b){Vec<Jet> av{a[0],a[1],a[2]},bv{b[0],b[1],b[2]};auto c=cross(av,bv);return {a[3]*b[0]+b[3]*a[0]+c[0],a[3]*b[1]+b[3]*a[1]+c[1],a[3]*b[2]+b[3]*a[2]+c[2],a[3]*b[3]-dot(av,bv)};}
inline JQ liftedQuaternion(const Q&q,int offset){Vec<Jet>w{Jet::variable(offset),Jet::variable(offset+1),Jet::variable(offset+2)};JQ dq{Jet(.5)*w[0],Jet(.5)*w[1],Jet(.5)*w[2],Jet(1)-Jet(.125)*dot(w,w)},base{q[0],q[1],q[2],q[3]};return product(dq,base);}
inline Vec<Jet> rotation(const JQ&q,const Vec<Jet>&v){Vec<Jet>a{q[0],q[1],q[2]};auto c=cross(a,v),cc=cross(a,c);Vec<Jet>r;for(int j=0;j<3;++j)r[j]=v[j]+Jet(2)*(q[3]*c[j]+cc[j]);return r;}
inline JQ conjugate(JQ q){for(int j=0;j<3;++j)q[j]=Jet(0)-q[j];return q;}
struct Strain{Vec<Jet> gamma,kappa;};
inline Strain strains(const Pose&a,const Pose&b,double L,bool lifted){
 validate(a);validate(b);if(!std::isfinite(L)||L<=1e-10)throw std::invalid_argument("beam reference length");
 JQ qa,qb;if(lifted){qa=liftedQuaternion(a.q,3);qb=liftedQuaternion(b.q,9);}else for(int j=0;j<4;++j){qa[j]=a.q[j];qb[j]=b.q[j];}
 double d=0;for(int j=0;j<4;++j)d+=a.q[j]*b.q[j];if(std::abs(d)<std::cos(1.4))throw std::domain_error("relative element rotation exceeds2.8rad branch");
 if(d<0)for(auto&v:qb)v=Jet(0)-v;
 JQ mid;Jet norm;for(int j=0;j<4;++j){mid[j]=qa[j]+qb[j];norm=norm+mid[j]*mid[j];}auto scale=inverse(root(norm));for(auto&v:mid)v=v*scale;
 Vec<Jet>dx;for(int j=0;j<3;++j){dx[j]=Jet(b.p[j]-a.p[j]);if(lifted)dx[j]=dx[j]+Jet::variable(6+j)-Jet::variable(j);dx[j]=dx[j]*Jet(1/L);}
 auto qr=product(conjugate(qa),qb);Vec<Jet>vec{qr[0],qr[1],qr[2]};Jet t=dot(vec,vec),factor;
 if(t.v<1e-6)factor=Jet(2)+t*(Jet(1./3)+t*(Jet(3./20)+t*(Jet(5./56)+t*Jet(35./576))));
 else {auto s=root(t);factor=Jet(2)*arcsin(s)*inverse(s);}
 Strain r;r.gamma=rotation(conjugate(mid),dx);for(int j=0;j<3;++j)r.kappa[j]=factor*vec[j]*Jet(1/L);return r;
}
struct Properties{double EA=1,GAy=1,GAz=1,GJ=1,EIy=1,EIz=1;std::array<double,6> values()const{return {EA,GAy,GAz,GJ,EIy,EIz};}void validate()const{for(double v:values())if(!std::isfinite(v)||v<=0)throw std::invalid_argument("positive finite beam stiffness required");}};
inline Result evaluate(const Pose&a,const Pose&b,const Pose&a0,const Pose&b0,const Properties&material){
 material.validate();auto dp=sub(b0.p,a0.p);double L=std::sqrt(dot(dp,dp));auto rest=strains(a0,b0,L,false),current=strains(a,b,L,true);auto c=material.values();Jet e;
 for(int j=0;j<3;++j){auto g=current.gamma[j]-Jet(rest.gamma[j].v),k=current.kappa[j]-Jet(rest.kappa[j].v);e=e+Jet(.5*L*c[j])*g*g+Jet(.5*L*c[j+3])*k*k;}
 Result r;r.energy=e.v;r.chart_hessian=e.h;
 for(int i=0;i<N;++i){r.force[i]=-e.g[i];for(int j=0;j<N;++j)r.jacobian[N*i+j]=-e.h[N*i+j];}
 // Spatial torque derivative is not the symmetric local chart Hessian.
 for(int o:{3,9}){double x=r.force[o],y=r.force[o+1],z=r.force[o+2],s[9]={0,-z,y,z,0,-x,-y,x,0};for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.jacobian[N*(o+i)+o+j]-=.5*s[3*i+j];}
 if(!std::isfinite(r.energy))throw std::overflow_error("beam energy overflow");
 for(double v:r.force)if(!std::isfinite(v))throw std::overflow_error("beam force overflow");
 for(double v:r.jacobian)if(!std::isfinite(v))throw std::overflow_error("beam tangent overflow");
 return r;
}
}
