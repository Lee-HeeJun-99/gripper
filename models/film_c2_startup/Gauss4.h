#pragma once
#include <Eigen/Dense>
#include <Eigen/SparseLU>
#include <array>
#include <cmath>
#include <stdexcept>
namespace regrip_c2_startup {
// Independent four-stage Gauss-Legendre(order8) candidate. Coefficients are
// integrated Lagrange polynomials at100 decimal digits in1663/1667,rounded
// ONCE to double. No old Gauss2 kernel or physical force law is replaced.
inline constexpr double a[4][4]={
 {0.086963711284363462,-0.026604180084998794,0.012627462689404725,-0.0035551496857956833},
 {0.18811811749986806,0.16303628871563652,-0.027880428602470895,0.0067355005945381559},
 {0.16719192197418878,0.35395300603374397,0.16303628871563652,-0.014190694931141144},
 {0.1774825722545226,0.31344511474186837,0.35267675751627187,0.086963711284363462}};
inline constexpr double b[4]={0.17392742256872692,0.32607257743127305,0.32607257743127305,0.17392742256872692};
inline constexpr double c[4]={0.069431844202973714,0.33000947820757187,0.66999052179242813,0.93056815579702634};
struct Result{Eigen::VectorXd q,v,finalStageResidual;std::array<Eigen::VectorXd,4>stageQ,stageV,internalForce;double residual=0,tangentError=0,nonlinearResidual=0;unsigned evaluations=0,iterations=0;};
template<class Force>
Result gauss4(const Eigen::MatrixXd&M,const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h,const Force&force,bool check=false,double tolerance=1e-18){
 const int n=q.size();if(n<=0||n>2000||v.size()!=n||M.rows()!=n||M.cols()!=n||!(h>0)||!std::isfinite(time+h)||!q.allFinite()||!v.allFinite()||!M.allFinite()||!(tolerance>0&&tolerance<=1e-18))throw std::invalid_argument("bounded Gauss4 dimensions/finite state;tolerance may TIGHTEN only");
 Eigen::LDLT<Eigen::MatrixXd>mass(M);if(mass.info()!=Eigen::Success||mass.vectorD().minCoeff()<=0)throw std::runtime_error("actual projected mass must be SPD");
 struct Evaluation{Eigen::VectorXd residual;Eigen::MatrixXd tangent;std::array<Eigen::VectorXd,4>q,v,total,internal;};
 Result out;unsigned calls=0;Eigen::VectorXd x(4*n);for(unsigned j=0;j<4;++j)x.segment(j*n,n)=v;
 auto evaluate=[&](const Eigen::VectorXd&trial){
  Evaluation e;e.residual=Eigen::VectorXd::Zero(4*n);e.tangent=Eigen::MatrixXd::Zero(4*n,4*n);std::array<Eigen::MatrixXd,4>K;
  for(unsigned j=0;j<4;++j){e.v[j]=trial.segment(j*n,n);e.q[j].resize(n);for(int i=0;i<n;++i){long double value=q(i);for(unsigned k=0;k<4;++k)value+=static_cast<long double>(h)*a[j][k]*trial(k*n+i);e.q[j](i)=double(value);}auto f=force(e.q[j],time+c[j]*h);++calls;if(f.force.size()!=n||f.stiffness.rows()!=n||f.stiffness.cols()!=n||!f.force.allFinite()||!f.stiffness.allFinite())throw std::runtime_error("finite same-law force/Hessian required");e.internal[j]=f.force;e.total[j]=f.force-2*M*e.v[j];K[j]=std::move(f.stiffness);}
  for(unsigned i=0;i<4;++i){Eigen::VectorXd base=M*(e.v[i]-v);for(int row=0;row<n;++row){long double value=base(row);for(unsigned j=0;j<4;++j)value-=static_cast<long double>(h)*a[i][j]*e.total[j](row);e.residual(i*n+row)=double(value);}for(unsigned k=0;k<4;++k){Eigen::MatrixXd block=2*h*a[i][k]*M;if(i==k)block+=M;for(unsigned j=0;j<4;++j)block+=h*h*a[i][j]*a[j][k]*K[j];e.tangent.block(i*n,k*n,n,n)=block;}}
  if(!e.residual.allFinite()||!e.tangent.allFinite())throw std::runtime_error("nonfinite Gauss4 trial");return e;
 };
 auto e=evaluate(x);
 if(check){for(unsigned k=0;k<3;++k){Eigen::VectorXd direction(4*n);for(int i=0;i<4*n;++i)direction(i)=std::sin((i+1)*(k+1)*.71);direction.normalize();double eps=1e-5;Eigen::VectorXd fd=(evaluate(x+eps*direction).residual-evaluate(x-eps*direction).residual)/(2*eps),exact=e.tangent*direction;out.tangentError=std::max(out.tangentError,(fd-exact).norm()/exact.norm());}if(out.tangentError>1e-8)throw std::runtime_error("Gauss4 stage tangent FD fails existing1e-8 gate");}
 unsigned iteration=0;for(;iteration<20;++iteration){double norm=e.residual.norm();if(norm<=tolerance)break;Eigen::SparseMatrix<double>matrix=e.tangent.sparseView(0.,0.);Eigen::SparseLU<Eigen::SparseMatrix<double>>lu;lu.compute(matrix);if(lu.info()!=Eigen::Success)throw std::runtime_error("unmodified Gauss4 tangent singular");Eigen::VectorXd delta=lu.solve(-e.residual);if(lu.info()!=Eigen::Success||!delta.allFinite())throw std::runtime_error("Gauss4 correction invalid");bool accepted=false;for(unsigned cut=0;cut<16;++cut){double alpha=std::ldexp(1.,-int(cut));Eigen::VectorXd trial=x+alpha*delta;auto next=evaluate(trial);if(next.residual.norm()<=(1-1e-4*alpha)*norm||next.residual.norm()<=tolerance){x=std::move(trial);e=std::move(next);accepted=true;break;}}if(!accepted)throw std::runtime_error("Gauss4 residual line search failed");}if(iteration==20)throw std::runtime_error("Gauss4 Newton20 budget");
 out.nonlinearResidual=e.residual.norm();out.finalStageResidual=e.residual;out.iterations=iteration;
 Eigen::VectorXd impulse(n);out.q.resize(n);for(int i=0;i<n;++i){long double position=q(i),value=0;for(unsigned j=0;j<4;++j){position+=static_cast<long double>(h)*b[j]*e.v[j](i);value+=static_cast<long double>(h)*b[j]*e.total[j](i);}out.q(i)=double(position);impulse(i)=double(value);}out.v=v+mass.solve(impulse);out.residual=(M*(out.v-v)-impulse).norm();out.stageQ=e.q;out.stageV=e.v;out.internalForce=e.internal;out.evaluations=calls;if(out.residual>1e-17||!out.q.allFinite()||!out.v.allFinite())throw std::runtime_error("Gauss4 momentum/finite gate fails");return out;
}
}
