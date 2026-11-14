#pragma once
#include "../integrated/Kernels.h"
namespace regrip_contact {
using namespace regrip_integrated;
// Friction needs only first derivatives of its physical wrench. Avoid computing
// unused12x12 Hessians twice at every contact point. Normal energy still uses AD2.
struct First{
 double v=0;std::array<double,12>g{};First(double x=0):v(x){}
 static First variable(int i){First x;x.g[i]=1;return x;}
};
inline First operator+(const First&a,const First&b){First c(a.v+b.v);for(int i=0;i<12;++i)c.g[i]=a.g[i]+b.g[i];return c;}
inline First operator-(const First&a,const First&b){First c(a.v-b.v);for(int i=0;i<12;++i)c.g[i]=a.g[i]-b.g[i];return c;}
inline First operator*(const First&a,const First&b){First c(a.v*b.v);for(int i=0;i<12;++i)c.g[i]=a.g[i]*b.v+a.v*b.g[i];return c;}
inline First root(const First&a){if(!std::isfinite(a.v)||a.v<=1e-20)throw std::invalid_argument("singular distance");double r=std::sqrt(a.v);First c(r);for(int i=0;i<12;++i)c.g[i]=.5/r*a.g[i];return c;}
inline First inverse(const First&a){if(a.v<=0)throw std::invalid_argument("inverse distance");First c(1/a.v);for(int i=0;i<12;++i)c.g[i]=-1/(a.v*a.v)*a.g[i];return c;}
inline Jet inverse(const Jet&a){if(a.v<=0)throw std::invalid_argument("inverse distance");return compose(a,1/a.v,-1/(a.v*a.v),2/(a.v*a.v*a.v));}
inline Vec<Jet> constant(const V&v){return {Jet(v[0]),Jet(v[1]),Jet(v[2])};}
// Smooth kinetic Coulomb regularization, not a static stick law. Local AD charts
// differentiate physical world wrenches directly (not a symmetric energy Hessian).
inline Result friction(const Pose&p,const Pose&o,const V&vp,const V&vo,const V&omega,int shape,const V&dims,double rp,double kn,double mu,double speed,bool velocityChart=false){
 using Jet=First;
 auto constant=[](const V&v)->Vec<Jet>{return {Jet(v[0]),Jet(v[1]),Jet(v[2])};};
 auto lifted=[&](const V&v,int offset)->Vec<Jet>{auto a=constant(v);Vec<Jet>w{Jet::variable(offset),Jet::variable(offset+1),Jet::variable(offset+2)};return add(a,cross(w,a));};
 if(!std::isfinite(mu)||mu<0||!std::isfinite(speed)||speed<=0)throw std::invalid_argument("friction parameters");
 for(auto v:{vp,vo,omega})for(double a:v)if(!std::isfinite(a))throw std::invalid_argument("nonfinite velocity");
 validate(p);validate(o);if(shape<0||shape>2||!std::isfinite(rp)||rp<0||!std::isfinite(kn)||kn<0)throw std::invalid_argument("normal contact parameters");for(double d:dims)if(!std::isfinite(d)||d<=0)throw std::invalid_argument("normal shape dimensions");
 Vec<Jet>d,axes[3],local;
 for(int j=0;j<3;++j)d[j]=Jet(p.p[j]-o.p[j])+(velocityChart?Jet(0):Jet::variable(j)-Jet::variable(j+6));
 for(int j=0;j<3;++j){V axis{};axis[j]=1;auto v=rotate(o.q,axis);axes[j]=velocityChart?constant(v):lifted(v,9);local[j]=dot(axes[j],d);}
 Vec<Jet>nl{};Jet distance;
 if(shape==0){auto norm=root(dot(local,local));distance=norm-Jet(dims[0]);for(int j=0;j<3;++j)nl[j]=local[j]*inverse(norm);}
 else if(shape==1){auto norm=root(local[0]*local[0]+local[2]*local[2]);distance=norm-Jet(dims[0]);nl[0]=local[0]*inverse(norm);nl[2]=local[2]*inverse(norm);}
 else{Vec<Jet>q{},positive{};Jet squared;int nearest=0;
  for(int j=0;j<3;++j){q[j]=Jet(local[j].v<0?-1:1)*local[j]-Jet(dims[j]);if(q[j].v>q[nearest].v)nearest=j;if(q[j].v>0){positive[j]=q[j];squared=squared+q[j]*q[j];}}
  if(squared.v>0){auto norm=root(squared);distance=norm;for(int j=0;j<3;++j)nl[j]=Jet(local[j].v<0?-1:1)*positive[j]*inverse(norm);}
  else{distance=q[nearest];nl[nearest]=Jet(local[nearest].v<0?-1:1);}
 }
 Result r;if(distance.v>=rp)return r;Vec<Jet>n{},rel{},w{},tangent{},ft{};
 for(int j=0;j<3;++j)for(int k=0;k<3;++k)n[k]=n[k]+axes[j][k]*nl[j];
 for(int j=0;j<3;++j){rel[j]=Jet(vp[j]-vo[j])+(velocityChart?Jet::variable(j)-Jet::variable(j+6):Jet(0));w[j]=Jet(omega[j])+(velocityChart?Jet::variable(j+9):Jet(0));}
 rel=sub(rel,cross(w,d));auto vn=dot(n,rel);
 for(int j=0;j<3;++j)tangent[j]=rel[j]-n[j]*vn;
 auto denominator=root(dot(tangent,tangent)+Jet(speed*speed));auto magnitude=Jet(-mu*kn)*(Jet(rp)-distance)*inverse(denominator);
 for(int j=0;j<3;++j)ft[j]=magnitude*tangent[j];
 auto torque=cross(d,ft);
 std::array<Jet,12>f{};for(int j=0;j<3;++j){f[j]=ft[j];f[j+6]=Jet(-1)*ft[j];f[j+9]=Jet(-1)*torque[j];}
 for(int i=0;i<12;++i){r.force[i]=f[i].v;for(int j=0;j<12;++j)r.jacobian[12*i+j]=f[i].g[j];}
 return r;
}
}
