#pragma once
#include <Eigen/Dense>
#include <Eigen/SparseLU>
#include <functional>
#include <array>
#include <stdexcept>
#include <sstream>
#include <iomanip>
namespace regrip_collocation {
// Experimental persistent ONE BILATERAL branch;not a new impact or active-set
// law. Reject negative reactions and endpoint drift;never project positions.
struct Force {Eigen::VectorXd value;Eigen::MatrixXd negativeTangent;};
struct Geometry {double gap;Eigen::VectorXd J;Eigen::MatrixXd H;};
struct Stage {Eigen::VectorXd q,v;double force=0,time=0;Geometry geometry;};
struct RadauResult {Eigen::VectorXd q,v;std::array<Stage,2>stages;unsigned evaluations=0,iterations=0;double momentumResidual=0,velocityResidual=0,initialForce=0;};
inline RadauResult singleRowRadau(const Eigen::MatrixXd&M,double damping,
 const Eigen::VectorXd&q0,const Eigen::VectorXd&v0,double time,double h,
 const std::function<Force(const Eigen::VectorXd&,double)>&force,
 const std::function<Geometry(const Eigen::VectorXd&)>&geometry,bool checkTangent=false,bool lobatto=false,bool sparseStage=false){
 const int n=v0.size();if(n==0||M.rows()!=n||M.cols()!=n||q0.size()!=n||!(h>0)||damping<0)throw std::invalid_argument("single-row Radau inputs");
 Eigen::LDLT<Eigen::MatrixXd>mf(M);if(mf.info()!=Eigen::Success||mf.vectorD().minCoeff()<=0)throw std::domain_error("Radau mass not SPD");
 auto initial=geometry(q0);if(std::abs(initial.gap)>1e-10||std::abs(initial.J.dot(v0))>1e-10)throw std::domain_error("Radau requires tangent touching initial branch");
 auto f0=force(q0,time);Eigen::VectorXd free=f0.value-damping*M*v0,miJ=mf.solve(initial.J),a0=mf.solve(free);
 double w=initial.J.dot(miJ);if(!(w>0))throw std::domain_error("Radau singular contact compliance");
 double lambda=-(initial.J.dot(a0)+v0.dot(initial.H*v0))/w;if(lambda<0)throw std::domain_error("Radau initial acceleration releases unilateral contact");
 const double A[2][2]={{lobatto?1./3:5./12,lobatto?-1./24:-1./12},{lobatto?2./3:3./4,lobatto?1./6:1./4}},c[2]={lobatto?.5:1./3,1},known[2]={lobatto?5./24:0.,lobatto?1./6:0.};
 Eigen::VectorXd total0=free+initial.J*lambda;
 Eigen::VectorXd x(2*n+2);for(int i=0;i<2;++i){x.segment(i*n,n)=v0+h*c[i]*(a0+miJ*lambda);x(2*n+i)=lambda;}
 const double momentumScale=std::max(1e-18,(M*v0).norm()+h*free.norm()),velocityScale=std::max(1.,v0.norm());
 struct Evaluation {Eigen::VectorXd residual;Eigen::MatrixXd tangent;std::array<Stage,2>s;double momentum=0,velocity=0,merit=0;};
 unsigned count=0;
 auto evaluate=[&](const Eigen::VectorXd&trial){++count;Evaluation e;e.residual=Eigen::VectorXd::Zero(2*n+2);e.tangent=Eigen::MatrixXd::Zero(2*n+2,2*n+2);std::array<Force,2>f;std::array<Eigen::VectorXd,2>total;
  for(int j=0;j<2;++j){auto&s=e.s[j];s.v=trial.segment(j*n,n);s.q=q0+h*known[j]*v0;for(int k=0;k<2;++k)s.q+=h*A[j][k]*trial.segment(k*n,n);s.force=trial(2*n+j);s.time=time+c[j]*h;s.geometry=geometry(s.q);f[j]=force(s.q,s.time);total[j]=f[j].value-damping*M*s.v+s.geometry.J*s.force;}
  for(int i=0;i<2;++i){e.residual.segment(i*n,n)=M*(e.s[i].v-v0)-h*known[i]*total0;for(int j=0;j<2;++j)e.residual.segment(i*n,n)-=h*A[i][j]*total[j];e.residual(2*n+i)=e.s[i].geometry.J.dot(e.s[i].v);
   for(int k=0;k<2;++k){Eigen::MatrixXd block=h*A[i][k]*damping*M;if(i==k)block+=M;for(int j=0;j<2;++j)block+=h*h*A[i][j]*A[j][k]*(f[j].negativeTangent-e.s[j].force*e.s[j].geometry.H);e.tangent.block(i*n,k*n,n,n)=block;e.tangent.block(i*n,2*n+k,n,1)=-h*A[i][k]*e.s[k].geometry.J;
    e.tangent.block(2*n+i,k*n,1,n)=h*A[i][k]*e.s[i].v.transpose()*e.s[i].geometry.H;if(i==k)e.tangent.block(2*n+i,k*n,1,n)+=e.s[i].geometry.J.transpose();}
  }
  e.momentum=e.residual.head(2*n).norm();e.velocity=e.residual.tail(2).norm();e.merit=std::hypot(e.momentum/momentumScale,e.velocity/velocityScale);if(!e.residual.allFinite()||!e.tangent.allFinite())throw std::domain_error("nonfinite Radau trial");return e;
 };
 Evaluation e=evaluate(x);unsigned iteration=0;
 if(checkTangent){Eigen::MatrixXd fd(e.tangent.rows(),e.tangent.cols());for(int k=0;k<x.size();++k){double delta=1e-5*std::max(1.,std::abs(x(k)));Eigen::VectorXd plus=x,minus=x;plus(k)+=delta;minus(k)-=delta;fd.col(k)=(evaluate(plus).residual-evaluate(minus).residual)/(2*delta);}double error=(fd-e.tangent).norm()/e.tangent.norm();if(error>1e-8)throw std::runtime_error("Radau true stage tangent FD failed:"+std::to_string(error));}
 for(;iteration<20;++iteration){if(e.momentum<=1e-17&&e.velocity<=1e-10)break;
  Eigen::VectorXd correction;
  if(sparseStage){
   // Remove EXACT zeros only;no threshold pruning,shift or symmetrization.
   Eigen::SparseMatrix<double>matrix=e.tangent.sparseView(0.,0.);Eigen::SparseLU<Eigen::SparseMatrix<double>,Eigen::COLAMDOrdering<int>>lu;lu.compute(matrix);if(lu.info()!=Eigen::Success)throw std::domain_error("true sparse stage factorization failed;no regularization");correction=lu.solve(-e.residual);if(lu.info()!=Eigen::Success)throw std::runtime_error("true sparse stage solve failed");
  }else{Eigen::FullPivLU<Eigen::MatrixXd>lu(e.tangent);if(!lu.isInvertible())throw std::domain_error("Radau true stage Jacobian singular;no regularization");correction=lu.solve(-e.residual);}
  bool accepted=false;
  for(unsigned back=0;back<16;++back){double alpha=std::ldexp(1.,-int(back));Eigen::VectorXd y=x+alpha*correction;auto next=evaluate(y);if(next.merit<=(1-1e-4*alpha)*e.merit||(next.momentum<=1e-17&&next.velocity<=1e-10)){x=std::move(y);e=std::move(next);accepted=true;break;}}
  if(!accepted){std::ostringstream message;message<<std::setprecision(17)<<"Radau stage line search rejected iteration="<<iteration<<" momentum="<<e.momentum<<" normal_velocity="<<e.velocity<<" merit="<<e.merit;throw std::runtime_error(message.str());}
 }
 if(iteration==20)throw std::runtime_error("Radau stage iteration budget20");
 for(auto&s:e.s)if(s.force<0)throw std::domain_error("Radau stage reaction negative;release needs another branch");
 if(std::abs(e.s[1].geometry.gap)>1e-10)throw std::domain_error("Radau endpoint geometric drift;no hidden position projection");
 return {e.s[1].q,e.s[1].v,e.s,count,iteration,e.momentum,e.velocity,lambda};
}
}
