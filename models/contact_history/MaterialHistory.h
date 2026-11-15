#pragma once
#include "../stabilization/ContactKernel.h"
namespace regrip_history {
using namespace regrip_integrated;
using First=regrip_contact::First;
inline First sqrtAD(const First&a){return regrip_contact::root(a);}
inline Jet sqrtAD(const Jet&a){return regrip_integrated::root(a);}
inline First invAD(const First&a){return regrip_contact::inverse(a);}
inline Jet invAD(const Jet&a){return regrip_contact::inverse(a);}
template<class T> Vec<T> constantV(const V&v){return {T(v[0]),T(v[1]),T(v[2])};}
template<class T> Vec<T> scale(const Vec<T>&v,const T&s){return {v[0]*s,v[1]*s,v[2]*s};}
template<class T> struct Geometry{T distance;Vec<T>normal;};
// Independent shapes: sphere, FINITE cylinder(local y), box. Seams are
// nonsmooth; differentiation tests deliberately stay inside a smooth branch.
template<class T> Geometry<T> geometry(const Vec<T>&x,unsigned shape,double radius,double halfHeight){
 Geometry<T>g{};
 if(shape==0){auto norm=sqrtAD(dot(x,x));g.distance=norm-T(radius);g.normal=scale(x,invAD(norm));}
 else if(shape==1){T radialSquared=x[0]*x[0]+x[2]*x[2];T q1=T(x[1].v<0?-1:1)*x[1]-T(halfHeight);
  if(radialSquared.v<=1e-20){if(q1.v<=-radius)throw std::invalid_argument("cylinder medial-axis normal not unique");g.distance=q1;g.normal={T(0),T(x[1].v<0?-1:1),T(0)};return g;}
  auto radial=sqrtAD(radialSquared);T q0=radial-T(radius);
  T a=q0.v>0?q0:T(0),b=q1.v>0?q1:T(0);Vec<T>nr{x[0]*invAD(radial),T(0),x[2]*invAD(radial)};
  Vec<T>ny{T(0),T(x[1].v<0?-1:1),T(0)};
  if(a.v>0||b.v>0){auto norm=sqrtAD(a*a+b*b);g.distance=norm;g.normal=add(scale(nr,a*invAD(norm)),scale(ny,b*invAD(norm)));}
  else if(q0.v>=q1.v){g.distance=q0;g.normal=nr;}else{g.distance=q1;g.normal=ny;}
 }else if(shape==2){Vec<T>q{},positive{};T squared;unsigned nearest=0;
  for(unsigned j=0;j<3;++j){q[j]=T(x[j].v<0?-1:1)*x[j]-T(radius);if(q[j].v>q[nearest].v)nearest=j;if(q[j].v>0){positive[j]=q[j];squared=squared+q[j]*q[j];}}
  if(squared.v>0){auto norm=sqrtAD(squared);g.distance=norm;for(unsigned j=0;j<3;++j)g.normal[j]=T(x[j].v<0?-1:1)*positive[j]*invAD(norm);}
  else{g.distance=q[nearest];g.normal[nearest]=T(x[nearest].v<0?-1:1);}
 }else throw std::invalid_argument("shape outside 0..2");
 return g;
}
struct History{bool active=false,sliding=false;V local{},normal{},elastic{};};
struct ContactResult{Result wrench;History next;double normalForce=0,elasticEnergy=0,plasticDissipation=0,releaseDissipation=0,capacity=0;};
// All state is in the object's material frame. Minimal normal transport is
// objective, with a guarded antipodal singularity rather than arbitrary axes.
inline ContactResult evaluateContact(const Pose&p,const Pose&o,const History&old,unsigned shape,double radius,double halfHeight,double skin,double kn,double kt,double mu,bool referenceNormal=false,bool tangentOnly=false){
 validate(p);validate(o);for(double a:{radius,halfHeight,skin,kn,kt,mu})if(!std::isfinite(a)||a<0)throw std::invalid_argument("contact scalar");
 if(radius==0||halfHeight==0||kt==0)throw std::invalid_argument("positive radius/halfHeight/kt required");
 for(const auto&v:{old.local,old.normal,old.elastic})for(double a:v)if(!std::isfinite(a))throw std::invalid_argument("nonfinite contact history");
 if(old.active&&std::abs(dot(old.normal,old.normal)-1)>1e-8)throw std::invalid_argument("history normal must be unit");
 Vec<First>d{},axes[3],local{};
 for(int j=0;j<3;++j)d[j]=First(p.p[j]-o.p[j])+First::variable(j)-First::variable(j+6);
 for(int j=0;j<3;++j){V axis{};axis[j]=1;auto v=rotate(o.q,axis);auto a=constantV<First>(v);Vec<First>w{First::variable(9),First::variable(10),First::variable(11)};axes[j]=add(a,cross(w,a));local[j]=dot(axes[j],d);}
 auto geo=geometry(local,shape,radius,halfHeight);ContactResult result;
 if(geo.distance.v>=skin){result.releaseDissipation=.5*kt*dot(old.elastic,old.elastic);return result;}
 result.normalForce=kn*(skin-geo.distance.v);result.capacity=mu*result.normalForce;
 auto n=geo.normal;Vec<First>elastic{};
 if(old.active){auto before=constantV<First>(old.normal);auto rotationAxis=cross(before,n);auto cosine=dot(before,n);
  if(cosine.v<-1+1e-8)throw std::invalid_argument("antipodal normal transport; refine timestep");
  auto previous=constantV<First>(old.elastic);elastic=add(previous,add(cross(rotationAxis,previous),scale(cross(rotationAxis,cross(rotationAxis,previous)),invAD(First(1)+cosine))));
  auto delta=sub(local,constantV<First>(old.local));auto a=sub(delta,scale(before,dot(before,delta)));
  auto transported=add(a,add(cross(rotationAxis,a),scale(cross(rotationAxis,cross(rotationAxis,a)),invAD(First(1)+cosine))));
  elastic=add(elastic,scale(add(transported,sub(delta,scale(n,dot(n,delta)))),First(.5)));
 }
 auto trial=elastic;double trialNorm=std::sqrt(dot(elastic,elastic).v);bool sliding=kt*trialNorm>result.capacity;
 if(result.capacity==0)elastic={First(0),First(0),First(0)};
 else if(sliding&&trialNorm>0){auto cap=First(mu*kn)*(First(skin)-geo.distance);auto squared=dot(elastic,elastic);First norm(std::sqrt(squared.v));for(int j=0;j<12;++j)norm.g[j]=.5*squared.g[j]/norm.v;elastic=scale(elastic,cap*invAD(First(kt)*norm));}
 // Normal energy differentiated independently with AD2, physical wrench
 // differentiated with AD1. Do not mistake this spatial Jacobian for Hessian.
 if(tangentOnly){result.wrench.energy=0;}else if(referenceNormal){
  Vec<Jet>dj{},lj{};for(int j=0;j<3;++j)dj[j]=Jet(p.p[j]-o.p[j])+Jet::variable(j)-Jet::variable(j+6);
  for(int j=0;j<3;++j){V a{};a[j]=1;lj[j]=dot(lifted(rotate(o.q,a),9),dj);}
  auto gap=geometry(lj,shape,radius,halfHeight).distance-Jet(skin);result.wrench=energy_result(Jet(.5*kn)*gap*gap);
 }else{
  // Equivalent physical normal wrench differentiated once, rather than a
  //12x12 energy Hessian followed by a rotational connection conversion.
  Vec<First>normal{};for(int j=0;j<3;++j)for(int k=0;k<3;++k)normal[k]=normal[k]+axes[j][k]*n[j];
  auto f=scale(normal,First(kn)*(First(skin)-geo.distance));auto torque=cross(d,f);std::array<First,12>w{};
  for(int j=0;j<3;++j){w[j]=f[j];w[j+6]=First(-1)*f[j];w[j+9]=First(-1)*torque[j];}
  for(int i=0;i<12;++i){result.wrench.force[i]=w[i].v;for(int j=0;j<12;++j)result.wrench.jacobian[12*i+j]=w[i].g[j];}
  result.wrench.energy=.5*kn*(geo.distance.v-skin)*(geo.distance.v-skin);
 }
 Vec<First>force{};for(int j=0;j<3;++j)for(int k=0;k<3;++k)force[k]=force[k]-First(kt)*axes[j][k]*elastic[j];
 auto torque=cross(d,force);std::array<First,12>wrench{};for(int j=0;j<3;++j){wrench[j]=force[j];wrench[j+6]=First(-1)*force[j];wrench[j+9]=First(-1)*torque[j];}
 for(int i=0;i<12;++i){result.wrench.force[i]+=wrench[i].v;for(int j=0;j<12;++j)result.wrench.jacobian[12*i+j]+=wrench[i].g[j];}
 result.next.active=true;result.next.sliding=sliding;
 V plastic{};for(int j=0;j<3;++j){result.next.local[j]=local[j].v;result.next.normal[j]=n[j].v;result.next.elastic[j]=elastic[j].v;plastic[j]=trial[j].v-elastic[j].v;}
 result.elasticEnergy=.5*kt*dot(result.next.elastic,result.next.elastic);result.plasticDissipation=result.capacity*std::sqrt(dot(plastic,plastic));result.wrench.energy+=result.elasticEnergy;
 for(double a:result.wrench.force)if(!std::isfinite(a))throw std::overflow_error("contact force");
 for(double a:result.wrench.jacobian)if(!std::isfinite(a))throw std::overflow_error("contact tangent");
 return result;
}
}

namespace regrip_history {
inline V transport(const V&e,const V&a,const V&b){double c=dot(a,b);if(c<-1+1e-8)throw std::invalid_argument("antipodal material normal");auto v=cross(a,b);return add(e,add(cross(v,e),scale(cross(v,cross(v,e)),1/(1+c))));}
// Value-only return map used by commit; never differentiates or changes history.
inline ContactResult value(const Pose&p,const Pose&o,const History&old,unsigned shape,double radius,double height,double skin,double kn,double kt,double mu){
 V x=rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));V n{};double distance=0;
 if(shape==0){double norm=std::sqrt(dot(x,x));if(norm<1e-14)throw std::invalid_argument("sphere center");n=scale(x,1/norm);distance=norm-radius;}
 else{auto g=geometry(constantV<First>(x),shape,radius,height);distance=g.distance.v;for(int j=0;j<3;++j)n[j]=g.normal[j].v;}
 ContactResult r;if(distance>=skin){r.releaseDissipation=.5*kt*dot(old.elastic,old.elastic);return r;}
 V e{};if(old.active){e=transport(old.elastic,old.normal,n);auto delta=sub(x,old.local);auto a=sub(delta,scale(old.normal,dot(old.normal,delta))),b=sub(delta,scale(n,dot(n,delta)));e=add(e,scale(add(transport(a,old.normal,n),b),.5));}
 r.normalForce=kn*(skin-distance);r.capacity=mu*r.normalForce;double norm=std::sqrt(dot(e,e));r.next.active=true;r.next.sliding=kt*norm>r.capacity;V trial=e;if(r.capacity==0)e={};else if(r.next.sliding)e=scale(e,r.capacity/(kt*norm));r.next.local=x;r.next.normal=n;r.next.elastic=e;auto plastic=sub(trial,e);r.plasticDissipation=r.capacity*std::sqrt(dot(plastic,plastic));r.elasticEnergy=.5*kt*dot(e,e);r.wrench.energy=.5*kn*(skin-distance)*(skin-distance)+r.elasticEnergy;return r;
}
}
