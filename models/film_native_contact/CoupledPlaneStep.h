#pragma once
#include "../film_rail_tendon/Kernel.h"
#include <Eigen/Dense>
namespace regrip_film_native {
using namespace regrip_film_rail;
// Independent single-active-plane backward-Euler minimization. This preserves
// the frozen native contact plane; it is NOT general collision detection or friction.
struct CoupledPlaneStep {
 Assembly model;std::vector<double>mass;double h,damping,T,target;
 std::vector<Point>previous,previousVelocity,J;
 std::vector<int>index;std::vector<double>weight;unsigned freeSize=0;
 CoupledPlaneStep(Assembly m,std::vector<double>mm,double dt,double c,double tension,
  std::vector<Point>q0,std::vector<Point>v0,std::vector<Point>j,double b):model(std::move(m)),mass(std::move(mm)),h(dt),damping(c),T(tension),target(b),previous(std::move(q0)),previousVelocity(std::move(v0)),J(std::move(j)){
  unsigned n=model.size();if(!std::isfinite(h+damping+T+target)||h<=0||damping<0||T<0||mass.size()!=n||previous.size()!=n||previousVelocity.size()!=n||J.size()!=n)throw std::invalid_argument("coupled plane inputs");index.assign(3*n,-1);weight.assign(3*n,1);
  for(unsigned part=0;part<3;++part)for(unsigned i=1;i<model.nx;++i)for(unsigned j=0;j<model.parts[part].ny;++j)for(unsigned d=0;d<3;++d)if(i!=1||d!=2)index[3*model.id(part,i,j)+d]=freeSize++;
  for(auto p:model.parts)for(unsigned j=0;j<p.ny;++j){unsigned slave=3*(p.offset+p.ny+j)+2;index[slave]=index[slave+3*p.ny];weight[slave]=.25;}
 }
 Eigen::VectorXd pack(const std::vector<Point>&v)const{Eigen::VectorXd y=Eigen::VectorXd::Zero(freeSize);for(unsigned i=0;i<3*model.size();++i)if(index[i]>=0&&weight[i]==1)y(index[i])=v[i/3][i%3];return y;}
 std::vector<Point>expand(const Eigen::VectorXd&y)const{std::vector<Point>v(model.size());for(unsigned i=0;i<3*model.size();++i)if(index[i]>=0)v[i/3][i%3]=weight[i]*y(index[i]);return v;}
 struct Evaluation{double phi=0,gap=0;Eigen::VectorXd gradient;Eigen::MatrixXd tangent;};
 Evaluation evaluate(const Eigen::VectorXd&y)const{Evaluation e;e.gradient=Eigen::VectorXd::Zero(freeSize);e.tangent=Eigen::MatrixXd::Zero(freeSize,freeSize);auto v=expand(y),q=previous;auto rest=model.rest();e.gap=-target;
  for(unsigned i=0;i<model.size();++i)for(unsigned d=0;d<3;++d){q[i][d]+=h*v[i][d];e.gap+=J[i][d]*(rest[i][d]+q[i][d]);double dv=v[i][d]-previousVelocity[i][d];e.phi+=.5*mass[i]*(dv*dv+h*damping*v[i][d]*v[i][d]);unsigned a=3*i+d;if(index[a]>=0){e.gradient(index[a])+=weight[a]*mass[i]*(dv+h*damping*v[i][d]);e.tangent(index[a],index[a])+=weight[a]*weight[a]*mass[i]*(1+h*damping);}}
  model.elements(q,T,[&](const Element&el){e.phi+=el.energy.v;for(unsigned a=0;a<3*el.ids.size();++a){unsigned ia=3*el.ids[a/3]+a%3;int i=index[ia];if(i<0)continue;e.gradient(i)+=h*weight[ia]*el.energy.g[a];for(unsigned b=0;b<3*el.ids.size();++b){unsigned ib=3*el.ids[b/3]+b%3;int j=index[ib];if(j>=0)e.tangent(i,j)+=h*h*weight[ia]*weight[ib]*el.energy.h[N*a+b];}}});return e;
 }
 struct Result{std::vector<Point>velocity,displacement;double lambda=0,residual=0,gap=0;unsigned iterations=0;};
 Result solve(const std::vector<Point>&initial,double lambda0,std::ostream*trace=nullptr)const{auto y=pack(initial);Eigen::VectorXd c=Eigen::VectorXd::Zero(freeSize);for(unsigned a=0;a<3*model.size();++a)if(index[a]>=0)c(index[a])+=weight[a]*J[a/3][a%3];double lambda=lambda0,initialResidual=-1;
  for(unsigned iteration=0;iteration<30;++iteration){auto e=evaluate(y);double residual=(e.gradient-c*lambda).norm();if(initialResidual<0)initialResidual=residual;if(trace)*trace<<"iteration "<<iteration<<" residual "<<residual<<" initial "<<initialResidual<<" gap "<<e.gap<<" phi "<<e.phi<<" lambda "<<lambda<<'\n';
   if(residual<=std::max(1e-15,initialResidual*1e-7)&&std::abs(e.gap)<=1e-10){Result result;result.velocity=expand(y);result.displacement=previous;for(unsigned i=0;i<model.size();++i)for(unsigned d=0;d<3;++d)result.displacement[i][d]+=h*result.velocity[i][d];result.lambda=lambda;result.residual=residual;result.gap=e.gap;result.iterations=iteration;return result;}
   Eigen::LDLT<Eigen::MatrixXd>ldlt(e.tangent);if(ldlt.info()!=Eigen::Success||ldlt.vectorD().minCoeff()<=0)throw std::runtime_error("nonpositive coupled algorithmic Hessian;no regularization applied");Eigen::VectorXd inverseC=ldlt.solve(c),inverseG=ldlt.solve(e.gradient);double denominator=c.dot(inverseC);if(!std::isfinite(denominator)||denominator<=0)throw std::runtime_error("degenerate contact Schur complement");double nextLambda=(-e.gap/h+c.dot(inverseG))/denominator;if(nextLambda<0)throw std::runtime_error("single-plane reference unloads;requires general active set");Eigen::VectorXd increment=-inverseG+inverseC*nextLambda;
   double alpha=1;bool accepted=false;for(unsigned trial=0;trial<16;++trial){auto candidate=evaluate(y+alpha*increment);if(trace)*trace<<"trial "<<trial<<" alpha "<<alpha<<" phi "<<candidate.phi<<" armijo_target "<<e.phi+1e-4*alpha*e.gradient.dot(increment)<<" residual "<<(candidate.gradient-c*(lambda+alpha*(nextLambda-lambda))).norm()<<'\n';double candidateResidual=(candidate.gradient-c*(lambda+alpha*(nextLambda-lambda))).norm();bool feasible=std::abs(candidate.gap)<=std::max(std::abs(e.gap),1e-10);bool improvesResidual=candidateResidual<=(1-1e-4*alpha)*residual;bool improvesFeasibility=std::abs(e.gap)>1e-10&&std::abs(candidate.gap)<=(1-1e-4*alpha)*std::abs(e.gap);if(feasible&&(improvesResidual||improvesFeasibility)){y+=alpha*increment;lambda+=alpha*(nextLambda-lambda);accepted=true;break;}alpha*=.5;}if(!accepted)throw std::runtime_error("coupled plane line search failed");
  }throw std::runtime_error("coupled plane Newton limit");
 }
};
}
