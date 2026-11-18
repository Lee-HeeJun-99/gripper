#pragma once
#include "Kernel.h"
#include <Eigen/SparseLU>
namespace regrip_transmission {
struct GaussResult{Eigen::VectorXd q,v;std::array<Eigen::VectorXd,2>stageQ,stageV;double residual=0,tangentError=0;unsigned evaluations=0;};
// Two-stage Gauss-Legendre order4,NO contacts/constraints other than reduced roots.
// Preserves original physical M,C=2M and the same stage-time force law.
template<class Force>
GaussResult gauss(const Eigen::MatrixXd&M,const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h,const Force&force,bool check=false){
 const int n=q.size();if(n<=0||v.size()!=n||M.rows()!=n||M.cols()!=n||h<=0||!M.allFinite())throw std::invalid_argument("Gauss dimensions");Eigen::LDLT<Eigen::MatrixXd>mass(M);if(mass.info()!=Eigen::Success||mass.vectorD().minCoeff()<=0)throw std::runtime_error("Gauss physical mass not SPD");
 const double r=std::sqrt(3.)/6,A[2][2]={{.25,.25-r},{.25+r,.25}},c[2]={.5-r,.5+r};Eigen::VectorXd x(2*n);x.head(n)=v;x.tail(n)=v;GaussResult out;unsigned calls=0;
 struct Evaluation{Eigen::VectorXd residual;Eigen::MatrixXd tangent;std::array<Eigen::VectorXd,2>q,v,total;};
 auto evaluate=[&](const Eigen::VectorXd&trial){Evaluation e;e.residual=Eigen::VectorXd::Zero(2*n);e.tangent=Eigen::MatrixXd::Zero(2*n,2*n);std::array<Eigen::MatrixXd,2>K;
  for(int j=0;j<2;++j){e.v[j]=trial.segment(j*n,n);e.q[j]=q;for(int k=0;k<2;++k)e.q[j]+=h*A[j][k]*trial.segment(k*n,n);auto f=force(e.q[j],time+c[j]*h);++calls;e.total[j]=f.force-2*M*e.v[j];K[j]=std::move(f.stiffness);}
  for(int i=0;i<2;++i){e.residual.segment(i*n,n)=M*(e.v[i]-v);for(int j=0;j<2;++j)e.residual.segment(i*n,n)-=h*A[i][j]*e.total[j];for(int k=0;k<2;++k){Eigen::MatrixXd B=2*h*A[i][k]*M;if(i==k)B+=M;for(int j=0;j<2;++j)B+=h*h*A[i][j]*A[j][k]*K[j];e.tangent.block(i*n,k*n,n,n)=B;}}
  if(!e.residual.allFinite()||!e.tangent.allFinite())throw std::runtime_error("nonfinite Gauss trial");return e;
 };
 auto e=evaluate(x);
 if(check){for(unsigned k=0;k<3;++k){Eigen::VectorXd direction(2*n);for(int i=0;i<2*n;++i)direction(i)=std::sin((i+1)*(k+1)*.71);direction.normalize();double eps=1e-5;Eigen::VectorXd fd=(evaluate(x+eps*direction).residual-evaluate(x-eps*direction).residual)/(2*eps),exact=e.tangent*direction;out.tangentError=std::max(out.tangentError,(fd-exact).norm()/exact.norm());}if(out.tangentError>1e-8)throw std::runtime_error("Gauss stage tangent directional FD fails");}
 unsigned iteration=0;for(;iteration<20;++iteration){double norm=e.residual.norm();if(norm<=1e-18)break;Eigen::SparseMatrix<double>B=e.tangent.sparseView(0.,0.);Eigen::SparseLU<Eigen::SparseMatrix<double>>lu;lu.compute(B);if(lu.info()!=Eigen::Success)throw std::runtime_error("unmodified Gauss tangent singular");Eigen::VectorXd delta=lu.solve(-e.residual);if(lu.info()!=Eigen::Success||!delta.allFinite())throw std::runtime_error("Gauss correction invalid");bool accepted=false;for(unsigned cut=0;cut<16;++cut){double alpha=std::ldexp(1.,-int(cut));Eigen::VectorXd trial=x+alpha*delta;auto next=evaluate(trial);if(next.residual.norm()<=(1-1e-4*alpha)*norm||next.residual.norm()<=1e-18){x=std::move(trial);e=std::move(next);accepted=true;break;}}if(!accepted)throw std::runtime_error("Gauss residual line search failed");}if(iteration==20)throw std::runtime_error("Gauss Newton20 budget");
 out.q=q+h/2*(e.v[0]+e.v[1]);out.v=v+h/2*mass.solve(e.total[0]+e.total[1]);out.residual=(M*(out.v-v)-h/2*(e.total[0]+e.total[1])).norm();out.stageQ=e.q;out.stageV=e.v;out.evaluations=calls;if(out.residual>1e-17||!out.q.allFinite()||!out.v.allFinite())throw std::runtime_error("Gauss momentum/finite gate fails");return out;
}
inline Step stepGauss(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass){
 if(h<=0||h>.001||time<0||time+h>.05000000000001)throw std::invalid_argument("bounded Gauss single coupon");auto map=mechanics(m,q,v,h,0,mass);auto out=gauss(filmMass(map),map.pack(q),map.pack(v),time,h,[&](const Eigen::VectorXd&x,double t){return parts(map,map.expand(x),control().sample(t).tension);},time==0);Step result{map.expand(out.q),map.expand(out.v),out.residual,out.evaluations};result.highOrder=true;for(unsigned i=0;i<2;++i){result.stageQ[i]=map.expand(out.stageQ[i]);result.stageV[i]=map.expand(out.stageV[i]);result.stageTime[i]=time+(.5+(i?1:-1)*std::sqrt(3.)/6)*h;result.stageT[i]=control().sample(result.stageTime[i]).tension;}return result;
}
}
