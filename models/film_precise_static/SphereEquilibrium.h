#pragma once
#include "Potential.h"
#include "../film_precise_tendon/Force.h"
#include "../film_native_contact/CoupledContactStep.h"
#include "../film_sphere_contact/ClosestPrimitive.h"
namespace regrip_precise_static {
using namespace regrip_transmission;
struct Linearized {Eigen::VectorXd increment,lambda;Eigen::MatrixXd compliance;};
inline Linearized linearized(const Eigen::MatrixXd&H,const Eigen::VectorXd&gradient,const Eigen::MatrixXd&C,const Eigen::VectorXd&gap,const Eigen::VectorXd&lambda){
 Eigen::LDLT<Eigen::MatrixXd>factor(H);if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("nonpositive TRUE static Lagrangian tangent;no regularization");
 Eigen::VectorXd inverseG=factor.solve(gradient);Eigen::MatrixXd inverseC=factor.solve(C),W=C.transpose()*inverseC;Eigen::VectorXd d=gap-C.transpose()*inverseG;
 auto next=regrip_film_native::CoupledContactStep::dual(W,d,lambda);return {-inverseG+inverseC*next,next,W};
}
// Independent fixed-sphere STATIC model: no fictitious mass/dt/inertia/damping.
// Multipliers are forces [N], never impulses. Every surface triangle is owned
// by its topology ID; no native predictor row identity is borrowed.
struct SphereEquilibrium {
 const CoupledPlaneStep&map;Point center;double radius;
 using Force=std::function<Parts(const CoupledPlaneStep&,const std::vector<Point>&,double)>;
 using Potential=std::function<double(const Assembly&,const std::vector<Point>&,double)>;
 Force mechanical;Potential externalPotential;
 std::vector<std::array<unsigned,3>>triangles;
 std::vector<double> rowOffsets;
 double rowRadius(unsigned row)const{return radius+(rowOffsets.empty()?0:rowOffsets.at(row));}
 void setThicknessEnvelope(){
  rowOffsets.clear();
  for(unsigned part=0;part<3;++part){double t=map.model.parts[part].thickness;
   if(!(std::isfinite(t)&&t>0))throw std::invalid_argument("positive finite part thickness required");
   for(unsigned i=0;i+1<map.model.nx;++i)for(unsigned j=0;j+1<map.model.parts[part].ny;++j){rowOffsets.push_back(t/2);rowOffsets.push_back(t/2);}}
  if(rowOffsets.size()!=triangles.size())throw std::runtime_error("thickness topology mismatch");
 }
 explicit SphereEquilibrium(const CoupledPlaneStep&m,Point c,double r,Force f={},Potential p={}):map(m),center(c),radius(r),mechanical(std::move(f)),externalPotential(std::move(p)){
  if(!mechanical)mechanical=[](const CoupledPlaneStep&m,const std::vector<Point>&q,double T){return regrip_precise_tendon::parts(m,q,T,6.);};
  if(!externalPotential)externalPotential=[](const Assembly&m,const std::vector<Point>&q,double T){return tendonPotential(m,q,T,6.);};
  if(!(r>0))throw std::invalid_argument("positive fixed sphere radius");const auto&model=map.model;
  for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);triangles.push_back({a,b,c});triangles.push_back({b,d,c});}
 }
 struct Geometry{Eigen::VectorXd gap;Eigen::MatrixXd C,H;};
 Geometry geometry(const Eigen::VectorXd&x,const Eigen::VectorXd&lambda,bool hessian=true)const{
  auto q=map.expand(x),rest=map.model.rest();for(unsigned i=0;i<q.size();++i)rest[i]=add(rest[i],q[i]);Geometry out{Eigen::VectorXd(triangles.size()),Eigen::MatrixXd::Zero(x.size(),triangles.size()),Eigen::MatrixXd::Zero(x.size(),x.size())};
  for(unsigned row=0;row<triangles.size();++row){auto tri=triangles[row];auto e=regrip_film_sphere::ClosestPrimitive::evaluate({rest[tri[0]],rest[tri[1]],rest[tri[2]]},center,rowRadius(row));out.gap(row)=e.gap.v;
   for(unsigned a=0;a<9;++a){unsigned ga=3*tri[a/3]+a%3;int i=map.index[ga];if(i<0)continue;out.C(i,row)+=map.weight[ga]*e.gap.g[a];if(hessian&&lambda(row)!=0)for(unsigned b=0;b<9;++b){unsigned gb=3*tri[b/3]+b%3;int j=map.index[gb];if(j>=0)out.H(i,j)+=lambda(row)*map.weight[ga]*map.weight[gb]*e.gap.h[regrip_film::N*a+b];}}
  }return out;
 }
 double potential(const Eigen::VectorXd&x,double T,const Parts&e)const{return e.skin+e.rails+e.bond+externalPotential(map.model,map.expand(x),T);}
 struct Result{Eigen::VectorXd q,lambda;double forceResidual,gapError;unsigned iterations;};
 Result solve(Eigen::VectorXd x,Eigen::VectorXd lambda,double T,std::ostream&trace)const{
  if(lambda.size()!=int(triangles.size())||lambda.minCoeff()<0)throw std::invalid_argument("owned nonnegative static force rows required");
  for(unsigned iteration=0;iteration<30;++iteration){auto e=mechanical(map,map.expand(x),T);auto g=geometry(x,lambda);Eigen::VectorXd gradient=-e.force;double residual=(gradient-g.C*lambda).norm(),gap=regrip_film_native::CoupledContactStep::gapError(g.gap,lambda);trace<<iteration<<','<<T<<','<<residual<<','<<gap<<','<<g.gap.minCoeff()<<','<<lambda.maxCoeff()<<'\n';trace.flush();
   if(residual<=1e-12&&gap<=1e-10)return {x,lambda,residual,gap,iteration};
   auto step=linearized(e.stiffness-g.H,gradient,g.C,g.gap,lambda);auto merit=[&](const Eigen::VectorXd&grad,const Geometry&geo,const Eigen::VectorXd&l){long double sum=(grad-geo.C*l).squaredNorm();for(int i=0;i<l.size();++i){if(!(step.compliance(i,i)>0)){if(geo.gap(i)<-1e-10)throw std::runtime_error("fixed infeasible static row");continue;}double v=std::min(l(i),geo.gap(i)/step.compliance(i,i));sum+=static_cast<long double>(v)*v;}return std::sqrt(sum);};
   double oldMerit=double(merit(gradient,g,lambda)),phi=potential(x,T,e),rho=2*std::max(lambda.maxCoeff(),step.lambda.maxCoeff()),penalty=0,slope=gradient.dot(step.increment);Eigen::VectorXd dg=g.C.transpose()*step.increment;
   for(int i=0;i<g.gap.size();++i){penalty+=std::max(-g.gap(i),0.);if(g.gap(i)<0)slope-=rho*dg(i);else if(g.gap(i)==0)slope+=rho*std::max(-dg(i),0.);}
   bool accepted=false;for(unsigned cut=0;cut<16;++cut){double alpha=std::ldexp(1.,-int(cut));Eigen::VectorXd trial=x+alpha*step.increment,l=lambda+alpha*(step.lambda-lambda);auto next=mechanical(map,map.expand(trial),T);auto geo=geometry(trial,l,false);double p=0;for(double value:geo.gap)p+=std::max(-value,0.);bool decrease=double(merit(-next.force,geo,l))<=(1-1e-4*alpha)*oldMerit;bool sqp=slope<0&&potential(trial,T,next)+rho*p<=phi+rho*penalty+1e-4*alpha*slope;
    if(decrease||sqp){x=std::move(trial);lambda=std::move(l);accepted=true;break;}}
   if(!accepted)throw std::runtime_error("static sphere merit line search failed;no position/force correction");
  }throw std::runtime_error("static sphere Newton30 budget;no equilibrium certificate");
 }
};
}
