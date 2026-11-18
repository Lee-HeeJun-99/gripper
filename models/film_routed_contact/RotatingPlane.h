#pragma once
#include "../yield_front_history/OutwardPolynomial.h"
#include "../film_impact/SurfaceEvent.h"
namespace regrip_routed_contact {
// Time-varying polynomial separating direction. ONLY a geometric exclusion
// witness,never a physical contact normal or modified force/Jacobian.
inline bool rotatingPlaneClear(const regrip_film_impact::QuadraticSurfacePath&p,
 const std::array<unsigned,3>&tri,regrip_film_rail::Point center,double radius,
 double begin,double end,unsigned feature){
 using namespace regrip_vector_history;using P3=std::array<OP,3>;
 if(!Outward::supported())return false;
 auto plus=[](P3 a,const P3&b,R factor){for(unsigned d=0;d<3;++d)a[d]=outwardSum(a[d],b[d],factor);return a;};
 auto dotp=[](const P3&a,const P3&b){OP v{Outward(0)};for(unsigned d=0;d<3;++d)v=outwardSum(v,outwardProduct(a[d],b[d]),1);return v;};
 auto scale=[](P3 a,const OP&k){for(auto&v:a)v=outwardProduct(v,k);return a;};
 auto crossp=[](const P3&a,const P3&b){P3 v;for(unsigned d=0;d<3;++d)v[d]=outwardSum(outwardProduct(a[(d+1)%3],b[(d+2)%3]),outwardProduct(a[(d+2)%3],b[(d+1)%3]),-1);return v;};
 std::array<P3,3>r;for(unsigned i=0;i<3;++i)for(unsigned d=0;d<3;++d)r[i][d]={Outward(p.a0.at(tri[i])[d])-Outward(center[d]),Outward(p.a1.at(tri[i])[d]),Outward(p.a2.at(tri[i])[d])};
 P3 direction;
 if(feature<3)direction=r[feature];
 else if(feature<6){unsigned a=feature==5?1:0,b=feature==3?1:2;auto edge=plus(r[b],r[a],-1);direction=plus(scale(r[a],dotp(edge,edge)),scale(edge,dotp(r[a],edge)),-1);}
 else if(feature==6){direction=crossp(plus(r[1],r[0],-1),plus(r[2],r[0],-1));auto x=p.position((begin+end)/2);auto ab=regrip_film_rail::sub(x[tri[1]],x[tri[0]]),ac=regrip_film_rail::sub(x[tri[2]],x[tri[0]]),normal=regrip_film_rail::cross(ab,ac);if(regrip_film_rail::dot(normal,regrip_film_rail::sub(x[tri[0]],center))<0)direction=scale(direction,OP{Outward(-1)});}
 else return false;
 auto positive=[&](const OP&polynomial){for(auto b:outwardBernstein(polynomial,Outward(begin),Outward(end)))if(!(b.lo>0))return false;return true;};
 auto n2=dotp(direction,direction);if(!positive(n2))return false;auto sphere=outwardProduct(OP{Outward(radius)*Outward(radius)},n2);
 for(const auto&node:r){auto support=dotp(direction,node);if(!positive(support)||!positive(outwardSum(outwardProduct(support,support),sphere,-1)))return false;}
 return true;
}
}
