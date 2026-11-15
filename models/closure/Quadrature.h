#pragma once
#include "../grasp/StickSlip.h"
namespace regrip_closure {
using namespace regrip_stick;
struct Interval{double lo=0,hi=0;bool active()const{return hi>lo;}};
inline double sdf(const V&v,unsigned shape,double radius,double height){
 if(shape==0)return std::sqrt(dot(v,v))-radius;
 if(shape==1){double a=std::hypot(v[0],v[2])-radius,b=std::abs(v[1])-height;return std::hypot(std::max(a,0.),std::max(b,0.))+std::min(0.,std::max(a,b));}
 if(shape==2){double outside=0,inside=-1e300;for(double x:v){double a=std::abs(x)-radius;outside+=std::max(a,0.)*std::max(a,0.);inside=std::max(inside,a);}return std::sqrt(outside)+std::min(0.,inside);}
 throw std::invalid_argument("shape");
}
inline V localPoint(const Pose&a,const Pose&b,const Pose&o,double s){return rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(add(scale(a.p,1-s),scale(b.p,s)),o.p));}
inline Interval activeInterval(const V&a,const V&b,unsigned shape,double radius,double height,double skin){
 V d=sub(b,a);double L2=dot(d,d);if(L2<=1e-24)throw std::invalid_argument("degenerate contact segment");
 if(shape==0){double middle=-dot(a,d)/L2;V closest=add(a,scale(d,middle));double delta=(radius+skin)*(radius+skin)-dot(closest,closest);if(delta<=0)return {};double h=std::sqrt(delta/L2);return {std::max(0.,middle-h),std::min(1.,middle+h)};}
 auto gap=[&](double s){return sdf(add(a,scale(d,s)),shape,radius,height)-skin;};
 // Rounded convex body: bracket its line intersection by a bounded minimizer.
 double l=0,r=1;for(int i=0;i<64;++i){double p=(2*l+r)/3,q=(l+2*r)/3;if(gap(p)<gap(q))r=q;else l=p;}
 double middle=(l+r)/2;if(gap(middle)>=0)return {};double left=0,right=1;
 if(gap(0)>0){l=0;r=middle;for(int i=0;i<56;++i){double m=(l+r)/2;if(gap(m)>0)l=m;else r=m;}left=(l+r)/2;}
 if(gap(1)>0){l=middle;r=1;for(int i=0;i<56;++i){double m=(l+r)/2;if(gap(m)>0)r=m;else l=m;}right=(l+r)/2;}
 return {left,right};
}
inline std::vector<std::pair<double,double>> gauss(unsigned n){
 if(n<2||n>32)throw std::invalid_argument("Gauss order2..32");
 std::vector<std::pair<double,double>>v(n);
 for(unsigned i=0;i<(n+1)/2;++i){double z=std::cos(3.14159265358979323846*(i+.75)/(n+.5)),derivative=0;
  for(unsigned j=0;j<32;++j){double p0=1,p1=z;for(unsigned k=2;k<=n;++k){double p=((2*k-1)*z*p1-(k-1)*p0)/k;p0=p1;p1=p;}derivative=n*(z*p1-p0)/(z*z-1);double dz=p1/derivative;z-=dz;if(std::abs(dz)<2e-15)break;if(j==31)throw std::runtime_error("Gauss root convergence");}
  double w=2/((1-z*z)*derivative*derivative);v[i]={-z,w};v[n-1-i]={z,w};
 }return v;
}
}
