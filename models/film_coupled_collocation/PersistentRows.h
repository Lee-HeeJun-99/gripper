#pragma once
#include "SingleRowRadau.h"
#include <vector>
namespace regrip_collocation {
// Independent extension of the same Lobatto IIIA equations to a FIXED set of
// independent,compressive rows. NOT an active-set/release/impact/CCD solver.
struct RowGeometry {
 Eigen::VectorXd gap;
 Eigen::MatrixXd J;
 std::vector<Eigen::MatrixXd> H;
};
struct RowStage {Eigen::VectorXd q,v,force;RowGeometry geometry;double time=0;};
struct RowsResult {
 Eigen::VectorXd q,v,initialForce;
 std::array<RowStage,2> stages;
 double momentumResidual=0,velocityResidual=0,tangentError=0;
 unsigned iterations=0,evaluations=0;
};
inline RowsResult persistentRows(const Eigen::MatrixXd&M,double damping,
 const Eigen::VectorXd&q0,const Eigen::VectorXd&v0,double time,double h,
 const std::function<Force(const Eigen::VectorXd&,double)>&force,
 const std::function<RowGeometry(const Eigen::VectorXd&)>&geometry,
 bool checkTangent=false,
 const std::function<void(const RowsResult&)>&rejectedEndpointObserver={}){
 const int n=q0.size();if(n==0||v0.size()!=n||M.rows()!=n||M.cols()!=n||!(h>0)||damping<0||!M.allFinite()||!M.isApprox(M.transpose(),1e-14))throw std::invalid_argument("persistent rows input");
 Eigen::LDLT<Eigen::MatrixXd>mass(M);
 if(mass.info()!=Eigen::Success||mass.vectorD().minCoeff()<=0)throw std::domain_error("persistent rows mass not SPD");
 auto initial=geometry(q0);const int m=initial.gap.size();
 auto validate=[&](const RowGeometry&g){
  if(m==0||g.gap.size()!=m||g.J.rows()!=m||g.J.cols()!=n||int(g.H.size())!=m||!g.J.allFinite()||!g.gap.allFinite())throw std::domain_error("persistent row geometry dimensions/finite");
  for(auto&H:g.H)if(H.rows()!=n||H.cols()!=n||!H.allFinite())throw std::domain_error("persistent row Hessian invalid");
 };
 validate(initial);
 if(initial.gap.cwiseAbs().maxCoeff()>1e-10||(initial.J*v0).cwiseAbs().maxCoeff()>1e-10)throw std::domain_error("persistent rows require touching tangent initial state");
 Eigen::MatrixXd miJ=mass.solve(initial.J.transpose()),W=initial.J*miJ;
 Eigen::FullPivLU<Eigen::MatrixXd>compliance(W);
 if(!compliance.isInvertible())throw std::domain_error("dependent contact rows:individual multipliers not unique;no regularization");
 auto f0=force(q0,time);Eigen::VectorXd free=f0.value-damping*M*v0,acc=mass.solve(free),curvature(m);
 for(int k=0;k<m;++k)curvature(k)=v0.dot(initial.H[k]*v0);
 Eigen::VectorXd lambda=compliance.solve(-initial.J*acc-curvature);
 if(lambda.minCoeff()<0)throw std::domain_error("persistent initial row releases");
 Eigen::VectorXd total0=free+initial.J.transpose()*lambda;
 constexpr double A[2][2]={{1./3,-1./24},{2./3,1./6}},known[2]={5./24,1./6},c[2]={.5,1.};
 Eigen::VectorXd x(2*n+2*m);
 for(int i=0;i<2;++i){x.segment(i*n,n)=v0+h*c[i]*(acc+miJ*lambda);x.segment(2*n+i*m,m)=lambda;}
 const double momentumScale=std::max(1e-18,(M*v0).norm()+h*free.norm()),velocityScale=std::max(1.,v0.norm());
 struct Evaluation {Eigen::VectorXd residual;Eigen::MatrixXd tangent;std::array<RowStage,2>s;double momentum,velocity,merit;};
 unsigned evaluations=0;
 auto evaluate=[&](const Eigen::VectorXd&trial){
  ++evaluations;Evaluation e;e.residual=Eigen::VectorXd::Zero(x.size());e.tangent=Eigen::MatrixXd::Zero(x.size(),x.size());
  std::array<Force,2>f;std::array<Eigen::VectorXd,2>total;std::array<Eigen::MatrixXd,2>stiffness;
  for(int j=0;j<2;++j){
   auto&s=e.s[j];s.v=trial.segment(j*n,n);s.force=trial.segment(2*n+j*m,m);s.q=q0+h*known[j]*v0;
   for(int k=0;k<2;++k)s.q+=h*A[j][k]*trial.segment(k*n,n);
   s.geometry=geometry(s.q);validate(s.geometry);s.time=time+c[j]*h;f[j]=force(s.q,s.time);
   total[j]=f[j].value-damping*M*s.v+s.geometry.J.transpose()*s.force;stiffness[j]=f[j].negativeTangent;
   for(int r=0;r<m;++r)stiffness[j]-=s.force(r)*s.geometry.H[r];
  }
  for(int i=0;i<2;++i){
   e.residual.segment(i*n,n)=M*(e.s[i].v-v0)-h*known[i]*total0;
   for(int j=0;j<2;++j)e.residual.segment(i*n,n)-=h*A[i][j]*total[j];
   e.residual.segment(2*n+i*m,m)=e.s[i].geometry.J*e.s[i].v;
   for(int k=0;k<2;++k){
    Eigen::MatrixXd block=h*A[i][k]*damping*M;if(i==k)block+=M;
    for(int j=0;j<2;++j)block+=h*h*A[i][j]*A[j][k]*stiffness[j];
    e.tangent.block(i*n,k*n,n,n)=block;
    e.tangent.block(i*n,2*n+k*m,n,m)=-h*A[i][k]*e.s[k].geometry.J.transpose();
    for(int r=0;r<m;++r){e.tangent.block(2*n+i*m+r,k*n,1,n)=h*A[i][k]*e.s[i].v.transpose()*e.s[i].geometry.H[r];}
    if(i==k)e.tangent.block(2*n+i*m,k*n,m,n)+=e.s[i].geometry.J;
   }
  }
  e.momentum=e.residual.head(2*n).norm();e.velocity=e.residual.tail(2*m).norm();e.merit=std::hypot(e.momentum/momentumScale,e.velocity/velocityScale);
  if(!e.residual.allFinite()||!e.tangent.allFinite())throw std::domain_error("nonfinite persistent rows trial");return e;
 };
 auto e=evaluate(x);double tangentError=0;
 if(checkTangent){Eigen::MatrixXd fd(x.size(),x.size());for(int k=0;k<x.size();++k){double delta=1e-5*std::max(1.,std::abs(x(k)));Eigen::VectorXd plus=x,minus=x;plus(k)+=delta;minus(k)-=delta;fd.col(k)=(evaluate(plus).residual-evaluate(minus).residual)/(2*delta);}tangentError=(fd-e.tangent).norm()/e.tangent.norm();if(tangentError>1e-8)throw std::runtime_error("persistent rows stage tangent FD failed");}
 unsigned iteration=0;
 for(;iteration<20;++iteration){
  if(e.momentum<=1e-17&&e.velocity<=1e-10)break;
  Eigen::SparseMatrix<double>matrix=e.tangent.sparseView(0.,0.);Eigen::SparseLU<Eigen::SparseMatrix<double>>lu;lu.compute(matrix);
  if(lu.info()!=Eigen::Success)throw std::domain_error("persistent rows stage singular;no regularization");
  Eigen::VectorXd correction=lu.solve(-e.residual);if(lu.info()!=Eigen::Success)throw std::runtime_error("persistent rows linear solve failed");
  bool accepted=false;
  for(unsigned back=0;back<16;++back){double alpha=std::ldexp(1.,-int(back));Eigen::VectorXd y=x+alpha*correction;auto next=evaluate(y);if(next.merit<=(1-1e-4*alpha)*e.merit||(next.momentum<=1e-17&&next.velocity<=1e-10)){x=std::move(y);e=std::move(next);accepted=true;break;}}
  if(!accepted)throw std::runtime_error("persistent rows line search rejected");
 }
 if(iteration==20)throw std::runtime_error("persistent rows iteration budget20");
 if(checkTangent){
  Eigen::MatrixXd fd(x.size(),x.size());
  for(int k=0;k<x.size();++k){double delta=1e-5*std::max(1.,std::abs(x(k)));Eigen::VectorXd plus=x,minus=x;plus(k)+=delta;minus(k)-=delta;fd.col(k)=(evaluate(plus).residual-evaluate(minus).residual)/(2*delta);}
  tangentError=std::max(tangentError,(fd-e.tangent).norm()/e.tangent.norm());
  if(tangentError>1e-8)throw std::runtime_error("persistent rows true tangent FD failed");
 }
 for(auto&s:e.s)if(s.force.minCoeff()<0)throw std::domain_error("persistent stage row releases;active-set transition NOT implemented");
 if(e.s[1].geometry.gap.cwiseAbs().maxCoeff()>1e-10){
  if(rejectedEndpointObserver)rejectedEndpointObserver({e.s[1].q,e.s[1].v,lambda,e.s,e.momentum,e.velocity,tangentError,iteration,evaluations});
  throw std::domain_error("persistent rows endpoint drift;no projection");
 }
 return {e.s[1].q,e.s[1].v,lambda,e.s,e.momentum,e.velocity,tangentError,iteration,evaluations};
}
}
