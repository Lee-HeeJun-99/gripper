#pragma once
#include "../contact_history/MaterialHistory.h"
// EXPERIMENTAL first-contact increment, not yet wired into the SOFA field.
// The trajectory is a straight chord in the object's material frame. This is
// an explicit temporal approximation, not an exact finite-rotation trajectory.
namespace regrip_birth {
using namespace regrip_history;
struct Increment{double crossingFraction;Vec<First> elastic;};
inline Increment firstContact(const V&before,const Vec<First>&after,unsigned shape,double radius,double height,double skin){
 auto g0=geometry(constantV<First>(before),shape,radius,height);
 auto g1=geometry(after,shape,radius,height);
 if(g0.distance.v<skin||g1.distance.v>=skin)throw std::invalid_argument("requires outside-to-inside birth");
 V endpoint{};for(int j=0;j<3;++j)endpoint[j]=after[j].v;
 // Expanded sphere/cylinder/box are convex: the chord has one entering root.
 double lo=0,hi=1;for(int i=0;i<60;++i){double a=(lo+hi)/2;auto x=add(scale(before,1-a),scale(endpoint,a));auto g=geometry(constantV<First>(x),shape,radius,height);if(g.distance.v>=skin)lo=a;else hi=a;}
 double a=(lo+hi)/2;auto x=add(scale(before,1-a),scale(endpoint,a));auto gb=geometry(constantV<First>(x),shape,radius,height);V normal{};for(int j=0;j<3;++j)normal[j]=gb.normal[j].v;double denominator=dot(normal,sub(endpoint,before));
 if(std::abs(denominator)<1e-12)throw std::invalid_argument("grazing contact birth derivative singular");
 First alpha(a);for(int k=0;k<12;++k){double numerator=0;for(int j=0;j<3;++j)numerator+=normal[j]*after[j].g[k];alpha.g[k]=-a*numerator/denominator;}
 auto boundary=add(constantV<First>(before),scale(sub(after,constantV<First>(before)),alpha));auto n0=geometry(boundary,shape,radius,height).normal,n1=g1.normal;auto delta=sub(after,boundary),v=cross(n0,n1);auto c=dot(n0,n1);
 if(c.v<-1+1e-8)throw std::invalid_argument("antipodal birth normal transport");
 auto tangent=sub(delta,scale(n0,dot(n0,delta)));auto transported=add(tangent,add(cross(v,tangent),scale(cross(v,cross(v,tangent)),invAD(First(1)+c))));
 return {a,scale(add(transported,sub(delta,scale(n1,dot(n1,delta)))),First(.5))};
}
}
