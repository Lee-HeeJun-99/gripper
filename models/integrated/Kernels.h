#pragma once
#include "../finite_rotation/Kernel.h"
#include <algorithm>
#include <vector>
namespace regrip_integrated {
using namespace regrip3d;
inline Jet compose(const Jet&a,double v,double first,double second){Jet r(v);for(int i=0;i<N;++i){r.g[i]=first*a.g[i];for(int j=0;j<N;++j)r.h[N*i+j]=first*a.h[N*i+j]+second*a.g[i]*a.g[j];}return r;}
inline Jet root(const Jet&a){if(a.v<=1e-20)throw std::invalid_argument("singular distance");double r=std::sqrt(a.v);return compose(a,r,.5/r,-.25/(a.v*r));}
inline Vec<Jet> displacement(const Pose&a,const Pose&b){Vec<Jet>d;for(int i=0;i<3;++i)d[i]=Jet(b.p[i]-a.p[i])+Jet::variable(i+6)-Jet::variable(i);return d;}
inline Jet cable_segment(const Pose&a,const Pose&b,const V&offset){
 validate(a);validate(b);auto d=displacement(a,b);d=add(d,sub(lifted(rotate(b.q,offset),9),lifted(rotate(a.q,offset),3)));return root(dot(d,d));}
inline Jet contact_energy(const Pose&point,const Pose&object,int shape,const V&dimensions,const V&attachment,double pointRadius,double stiffness){
 validate(point);validate(object);if(shape<0||shape>2||stiffness<0||pointRadius<0||!std::isfinite(stiffness))throw std::invalid_argument("contact parameters");
 for(double d:dimensions)if(!std::isfinite(d)||d<=0)throw std::invalid_argument("shape dimensions");
 // Point-first local chart, object-second; body orientation axes are convected.
 Vec<Jet> delta;for(int i=0;i<3;++i)delta[i]=Jet(point.p[i]-object.p[i])+Jet::variable(i)-Jet::variable(i+6);
 delta=add(delta,lifted(rotate(point.q,attachment),3));Vec<Jet> local;
 for(int c=0;c<3;++c){V axis{};axis[c]=1;local[c]=dot(lifted(rotate(object.q,axis),9),delta);}
 Jet distance;
 if(shape==0)distance=root(dot(local,local))-Jet(dimensions[0]);
 else if(shape==1)distance=root(local[0]*local[0]+local[2]*local[2])-Jet(dimensions[0]);
 else{
  Vec<Jet> q;Jet outside;int nearest=0;
  for(int i=0;i<3;++i){q[i]=Jet(local[i].v<0?-1:1)*local[i]-Jet(dimensions[i]);if(q[i].v>q[nearest].v)nearest=i;if(q[i].v>0)outside=outside+q[i]*q[i];}
  distance=outside.v>0?root(outside):q[nearest];
 }
 distance=distance-Jet(pointRadius);return distance.v<0?Jet(.5*stiffness)*distance*distance:Jet(0);
}
inline Result energy_result(const Jet&e){
 Result r;r.energy=e.v;r.chart_hessian=e.h;
 for(int i=0;i<N;++i){r.force[i]=-e.g[i];for(int j=0;j<N;++j)r.jacobian[N*i+j]=-e.h[N*i+j];}
 for(int o:{3,9}){double x=r.force[o],y=r.force[o+1],z=r.force[o+2],a[9]={0,-z,y,z,0,-x,-y,x,0};for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.jacobian[N*(o+i)+o+j]-=.5*a[3*i+j];}
 if(!std::isfinite(r.energy))throw std::overflow_error("energy overflow");
 for(double v:r.force)if(!std::isfinite(v))throw std::overflow_error("force overflow");
 for(double v:r.jacobian)if(!std::isfinite(v))throw std::overflow_error("Jacobian overflow");
 return r;
}
struct Slider{double traction=0,tangent=0,plastic=0,energy=0,dissipation=0;};
inline Slider slider(double s,double old,double k,double cap){
 if(!std::isfinite(s)||!std::isfinite(old)||!std::isfinite(k)||!std::isfinite(cap)||k<=0||cap<0)throw std::invalid_argument("slider parameters");
 double trial=k*(s-old),t=std::clamp(trial,-cap,cap),z=s-t/k;return {t,std::abs(trial)<cap?k:0,z,.5*t*t/k,cap*std::abs(z-old)};
}
} // namespace
