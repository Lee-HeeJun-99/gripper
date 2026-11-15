#pragma once
#include "BirthIncrement.h"
#include "../closure/Quadrature.h"
namespace regrip_birthfast {
using namespace regrip_history;
inline double root(const V&a,const V&b,unsigned shape,double radius,double height,double skin){
 if(regrip_closure::sdf(a,shape,radius,height)<skin||regrip_closure::sdf(b,shape,radius,height)>=skin)throw std::invalid_argument("birth root outside-to-inside required");
 if(shape==0){auto d=sub(b,a);double norm=std::sqrt(dot(a,a)),A=dot(d,d),B=dot(a,d),gap=(norm-radius)-skin,C=gap*(norm+radius+skin),D=B*B-A*C;if(A==0)throw std::invalid_argument("zero-displacement sphere birth");if(D>0){double alpha=C/(-B+std::sqrt(D));if(alpha>=0&&alpha<=1)return alpha;}
  // In a near-ULP crossing the algebraic root can fall outside the bracket.
  // Solve the SAME signed-distance bracket instead of clamping alpha.
 }
 double l=0,u=1;for(int i=0;i<60;++i){double alpha=(l+u)/2;auto x=add(scale(a,1-alpha),scale(b,alpha));if(regrip_closure::sdf(x,shape,radius,height)>=skin)l=alpha;else u=alpha;}return (l+u)/2;
}
inline V normal(const V&v,unsigned shape,double radius,double height){auto g=geometry(constantV<First>(v),shape,radius,height);V n;for(int j=0;j<3;++j)n[j]=g.normal[j].v;return n;}
inline regrip_birth::Increment increment(const V&before,const Vec<First>&after,unsigned shape,double radius,double height,double skin){
 V b;for(int j=0;j<3;++j)b[j]=after[j].v;double a=root(before,b,shape,radius,height,skin);auto boundaryValue=add(scale(before,1-a),scale(b,a));auto n=normal(boundaryValue,shape,radius,height);auto displacement=sub(b,before);double denominator=dot(n,displacement),length=std::sqrt(dot(displacement,displacement));if(length==0||std::abs(denominator)<=1e-10*length)throw std::invalid_argument("grazing birth derivative (relative normal incidence)");
 First alpha(a);for(int k=0;k<12;++k){double numerator=0;for(int j=0;j<3;++j)numerator+=n[j]*after[j].g[k];alpha.g[k]=-a*numerator/denominator;}
 auto boundary=add(constantV<First>(before),scale(sub(after,constantV<First>(before)),alpha));auto n0=geometry(boundary,shape,radius,height).normal,n1=geometry(after,shape,radius,height).normal;auto delta=sub(after,boundary),v=cross(n0,n1);auto c=dot(n0,n1);if(c.v<-1+1e-8)throw std::invalid_argument("antipodal birth normals");auto tangent=sub(delta,scale(n0,dot(n0,delta)));auto transported=add(tangent,add(cross(v,tangent),scale(cross(v,cross(v,tangent)),invAD(First(1)+c))));return {a,scale(add(transported,sub(delta,scale(n1,dot(n1,delta)))),First(.5))};
}
inline V incrementValue(const V&before,const V&after,unsigned shape,double radius,double height,double skin){double a=root(before,after,shape,radius,height,skin);auto boundary=add(scale(before,1-a),scale(after,a));auto n0=normal(boundary,shape,radius,height),n1=normal(after,shape,radius,height),d=sub(after,boundary);return scale(add(transport(sub(d,scale(n0,dot(n0,d))),n0,n1),sub(d,scale(n1,dot(n1,d)))),.5);}
}
