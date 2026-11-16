#pragma once
#include <array>
#include <cmath>
#include <stdexcept>

// Independent fixed-normal material-point reference. Traction below is k*e
// (the energy gradient); the force on the moving body is its negative.
namespace regrip_vector_history {
using R=long double;
using V=std::array<R,3>;
using M=std::array<R,9>;
inline R dot(V a,V b){R s=0;for(int i=0;i<3;++i)s+=a[i]*b[i];return s;}
inline V add(V a,V b){for(int i=0;i<3;++i)a[i]+=b[i];return a;}
inline V scale(V a,R s){for(auto&x:a)x*=s;return a;}
inline R norm(V a){return std::sqrt(dot(a,a));}
inline void finite(V a){for(R x:a)if(!std::isfinite(x))throw std::invalid_argument("nonfinite vector");}
struct Return {
 V elastic{},traction{},plastic{};
 M tangent{};
 R oldEnergy=0,energy=0,loss=0,projection=0,work=0;
 bool slip=false,unique=true;
 const M& classicalTangent()const{
  if(!unique)throw std::domain_error("positive-capacity yield equality: directional derivative required");
  return tangent;
 }
};
inline Return radialReturn(V old,V increment,V normal,R k,R cap){
 finite(old);finite(increment);finite(normal);
 if(!std::isfinite(k)||k<=0||!std::isfinite(cap)||cap<0)throw std::invalid_argument("stiffness/capacity");
 // Reject incompatible history instead of silently projecting away energy.
 constexpr R tol=128*__LDBL_EPSILON__;
 if(std::abs(dot(normal,normal)-1)>tol||std::abs(dot(old,normal))>tol*norm(old)||std::abs(dot(increment,normal))>tol*norm(increment))
  throw std::invalid_argument("unit normal and tangent history/increment required");
 Return r;V trial=add(old,increment);R length=norm(trial),load=k*length;
 if(!std::isfinite(load))throw std::overflow_error("trial load");
 r.oldEnergy=.5L*k*dot(old,old);
 r.slip=load>cap;r.unique=!(cap>0&&load==cap);
 if(cap==0){r.elastic={};r.plastic=trial;}
 else if(r.slip){
  V u=scale(trial,1/length);r.elastic=scale(u,cap/k);r.plastic=add(trial,scale(r.elastic,-1));
  // Spatial tangent in the FIXED tangent plane, not a SO(3) force Jacobian.
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)
   r.tangent[3*i+j]=cap/length*((i==j?1.L:0.L)-normal[i]*normal[j]-u[i]*u[j]);
 }else{
  r.elastic=trial;
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.tangent[3*i+j]=k*((i==j?1.L:0.L)-normal[i]*normal[j]);
 }
 r.traction=scale(r.elastic,k);r.energy=.5L*k*dot(r.elastic,r.elastic);
 r.loss=cap*norm(r.plastic);V change=add(r.elastic,scale(old,-1));
 r.projection=.5L*k*dot(change,change);r.work=dot(r.traction,increment);
 if(!std::isfinite(r.energy)||!std::isfinite(r.loss)||!std::isfinite(r.work))throw std::overflow_error("return measure");
 return r;
}
}
