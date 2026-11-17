#pragma once
#include <boost/multiprecision/cpp_bin_float.hpp>
#include <boost/multiprecision/cpp_int.hpp>
#include <array>
#include <stdexcept>
namespace regrip_three_finger {
using TriangleCoordinates=std::array<std::array<double,3>,3>;
struct UnresolvedDistanceOrder:std::domain_error {
 TriangleCoordinates a,b;
 UnresolvedDistanceOrder(const TriangleCoordinates&left,const TriangleCoordinates&right):std::domain_error("distance ordering unresolved across113/334bits;no arbitrary winner"),a(left),b(right){}
};
// VALUE-ONLY ordering of exact stored binary-double relative coordinates.
// No altered gap/force/tangent/normal or physical contact regularization.
template<class S>S preciseSquaredDistance(const TriangleCoordinates&input){
 using V=std::array<S,3>;std::array<V,3>x;for(unsigned i=0;i<3;++i)for(unsigned d=0;d<3;++d)x[i][d]=S(input[i][d]);
 auto sub=[](const V&a,const V&b){return V{a[0]-b[0],a[1]-b[1],a[2]-b[2]};};
 auto dot=[](const V&a,const V&b)->S{return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];};
 S best=dot(x[0],x[0]);
 for(auto pair:{std::array<unsigned,2>{0,1},{0,2},{1,2}}){V edge=sub(x[pair[1]],x[pair[0]]);S den=dot(edge,edge);if(!(den>0))throw std::domain_error("precise distance collapsed edge");S t=-dot(x[pair[0]],edge)/den;if(t<0)t=0;if(t>1)t=1;V p;for(unsigned d=0;d<3;++d)p[d]=x[pair[0]][d]+t*edge[d];S value=dot(p,p);if(value<best)best=value;}
 V ab=sub(x[1],x[0]),ac=sub(x[2],x[0]),normal{ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]};S nn=dot(normal,normal);if(!(nn>0))throw std::domain_error("precise distance collapsed triangle");S alpha=dot(normal,x[0])/nn;V p;for(unsigned d=0;d<3;++d)p[d]=alpha*normal[d];V ap=sub(p,x[0]);S aa=dot(ab,ab),bb=dot(ab,ac),cc=dot(ac,ac),den=aa*cc-bb*bb;if(!(den>0))throw std::domain_error("precise distance singular face");S u=(cc*dot(ab,ap)-bb*dot(ac,ap))/den,v=(aa*dot(ac,ap)-bb*dot(ab,ap))/den;
 if(u>=0&&v>=0&&u+v<=1){S value=dot(p,p);if(value<best)best=value;}return best;
}
inline int preciseOrder(const TriangleCoordinates&a,const TriangleCoordinates&b){
 using Q=boost::multiprecision::cpp_bin_float_quad;using H=boost::multiprecision::cpp_bin_float_100;
 auto sign=[](const auto&x){return x>0?1:x<0?-1:0;};
 Q low=preciseSquaredDistance<Q>(a)-preciseSquaredDistance<Q>(b);H high=preciseSquaredDistance<H>(a)-preciseSquaredDistance<H>(b);
 int l=sign(low),h=sign(high);if(l!=h)throw UnresolvedDistanceOrder(a,b);return h;
}
// Optional exact fallback,not a larger floating precision or gap perturbation.
// cpp_rational(double) represents the stored binary double exactly.
inline int rationalOrder(const TriangleCoordinates&a,const TriangleCoordinates&b){
 using R=boost::multiprecision::cpp_rational;
 R difference=preciseSquaredDistance<R>(a)-preciseSquaredDistance<R>(b);
 return difference>0?1:difference<0?-1:0;
}
}
