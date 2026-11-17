#pragma once
#include "../film_sphere_contact/CandidateClosure.h"
namespace regrip_film_impact {
// New constrained midpoint law, not a change to the preserved BE SphereStep.
// Unknown y=v_mid; q1=q0+h*y, v1=2*y-v0.
// G_mid(y)-J(q1)^T lambda=0; physical step impulse is 2*lambda.
// dg/dy=h*J and d(J^T lambda)/dy=h*sum(lambda*Hgap).
inline regrip_film_sphere::CandidateClosure::Result midpointPosition(
 const regrip_film_native::CoupledPlaneStep&m,
 const std::vector<std::array<unsigned,3>>&triangles,
 regrip_film_rail::Point center,double radius,double tension){
 using namespace regrip_film_native;using namespace regrip_film_sphere;
 CoupledPlaneStep stage(m.model,m.mass,m.h/2,m.damping,tension,m.previous,m.previousVelocity,std::vector<Point>(m.previous.size()),0);
 auto rest=m.model.rest();Eigen::VectorXd y=m.pack(m.previousVelocity),lambda(0);std::vector<unsigned>owned;
 struct Geometry{Eigen::VectorXd gap;Eigen::MatrixXd C,H;};
 auto position=[&](const Eigen::VectorXd&trial){auto q=m.previous,v=m.expand(trial);for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)q[i][d]+=m.h*v[i][d];return q;};
 auto geometry=[&](const Eigen::VectorXd&trial,const Eigen::VectorXd&multipliers){Geometry g;g.gap.resize(owned.size());g.C=Eigen::MatrixXd::Zero(m.freeSize,owned.size());g.H=Eigen::MatrixXd::Zero(m.freeSize,m.freeSize);auto q=position(trial);
  for(unsigned k=0;k<owned.size();++k){auto t=triangles[owned[k]];std::vector<Point>p;for(unsigned i:t)p.push_back(add(rest[i],q[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);g.gap(k)=e.gap.v;
   for(unsigned a=0;a<9;++a){unsigned ga=3*t[a/3]+a%3;int ia=m.index[ga];if(ia<0)continue;g.C(ia,k)+=m.weight[ga]*e.gap.g[a];
    for(unsigned b=0;b<9;++b){unsigned gb=3*t[b/3]+b%3;int ib=m.index[gb];if(ib>=0)g.H(ia,ib)+=m.h*multipliers(k)*m.weight[ga]*m.weight[gb]*e.gap.h[N*a+b];}
   }
  }return g;
 };
 double first=-1;regrip_film_sphere::CandidateClosure::Result out;
 for(unsigned sweep=0;sweep<8;++sweep){bool converged=false;
  for(unsigned iteration=0;iteration<30;++iteration){auto e=stage.evaluate(y);auto g=geometry(y,lambda);double residual=(e.gradient-g.C*lambda).norm();if(first<0)first=residual;
   if(residual<=std::max(1e-15,first*1e-7)&&CoupledContactStep::gapError(g.gap,lambda)<=1e-10){converged=true;out.mechanical.residual=2*residual;break;}
   Eigen::LDLT<Eigen::MatrixXd>factor(e.tangent-g.H);
   if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("midpoint TRUE contact tangent not positive;no regularization");
   auto inverseG=factor.solve(e.gradient).eval();auto inverseC=factor.solve(g.C).eval();Eigen::MatrixXd W=m.h*g.C.transpose()*inverseC;Eigen::VectorXd d=g.gap-m.h*g.C.transpose()*inverseG;
   Eigen::VectorXd next=CoupledContactStep::dual(W,d,lambda),dy=-inverseG+inverseC*next;
   auto merit=[&](const auto&gradient,const Geometry&geo,const Eigen::VectorXd&l){double norm=(gradient-geo.C*l).squaredNorm();for(int k=0;k<l.size();++k){if(!(W(k,k)>0))throw std::runtime_error("midpoint degenerate compliance");double c=std::min(l(k),geo.gap(k)/W(k,k));norm+=c*c;}return std::sqrt(norm);};
   double old=merit(e.gradient,g,lambda),alpha=1;bool accepted=false;
   for(unsigned backtrack=0;backtrack<16;++backtrack){Eigen::VectorXd trial=y+alpha*dy,l=lambda+alpha*(next-lambda);auto value=stage.evaluate(trial);auto geo=geometry(trial,l);
    if(merit(value.gradient,geo,l)<=(1-1e-4*alpha)*old){y=std::move(trial);lambda=std::move(l);accepted=true;break;}alpha*=.5;
   }
   if(!accepted)throw std::runtime_error("midpoint contact line search rejected");
  }
  if(!converged)throw std::runtime_error("midpoint contact Newton budget");
  auto q=position(y);unsigned added=0;
  for(unsigned id=0;id<triangles.size();++id){std::vector<Point>p;for(unsigned i:triangles[id])p.push_back(add(rest[i],q[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);
   if(e.gap.v>=-1e-10)continue;
   if(std::find(owned.begin(),owned.end(),id)!=owned.end())throw std::runtime_error("owned midpoint triangle violates gap gate");
   if(owned.size()>=256)throw std::runtime_error("midpoint row budget256;not OS exhaustion");
   owned.push_back(id);++added;
  }
  if(!added){out.mechanical.displacement=q;out.mechanical.velocity=m.expand(2*y-m.pack(m.previousVelocity));out.mechanical.lambda=2*lambda;
   for(unsigned k=0;k<owned.size();++k){auto t=triangles[owned[k]];std::vector<Point>p;for(unsigned i:t)p.push_back(add(rest[i],q[i]));auto e=ClosestPrimitive::evaluate(p,center,radius);std::vector<Point>J(rest.size());for(unsigned a=0;a<9;++a)J[t[a/3]][a%3]+=e.gap.g[a];out.rows.push_back({J,0,2*lambda(k),k,{t[0],t[1],t[2]}});out.triangle.push_back(owned[k]);}
   return out;
  }
  unsigned previous=lambda.size();lambda.conservativeResize(owned.size());lambda.tail(owned.size()-previous).setZero();
 }
 throw std::runtime_error("midpoint candidate closure budget8");
}
}
