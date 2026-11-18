#include "../models/film_transmission/Gauss.h"
#include <iostream>
#include <iomanip>
using namespace regrip_transmission;
int main(){
 Eigen::MatrixXd M=1e-6*Eigen::MatrixXd::Identity(1,1);auto force=[](const Eigen::VectorXd&q,double){Parts p;p.force=-9e-6*q;p.stiffness=9e-6*Eigen::MatrixXd::Identity(1,1);return p;};double previous=0;std::vector<double>errors;for(unsigned n:{10u,20u,40u}){Eigen::VectorXd q(1),v(1);q<<1;v<<0;double h=.4/n,time=0,tangent=0;for(unsigned i=0;i<n;++i){auto s=gauss(M,q,v,time,h,force,i==0);q=s.q;v=s.v;time+=h;tangent=std::max(tangent,s.tangentError);}double w=std::sqrt(8.),exact=std::exp(-.4)*(std::cos(w*.4)+std::sin(w*.4)/w),error=std::abs(q(0)-exact);if(previous&&previous/error<15.5)throw std::runtime_error("Gauss fourth-order convergence fails");if(tangent>1e-8)throw std::runtime_error("linear tangent fails");previous=error;errors.push_back(error);}
 // Nonlinear stage chain rule,not only a constant linear Hessian.
 auto cubic=[](const Eigen::VectorXd&q,double t){Parts p;p.force=1e-6*(-9*q-q.array().cube().matrix()+Eigen::VectorXd::Constant(1,.2*t));p.stiffness=Eigen::MatrixXd::Constant(1,1,1e-6*(9+3*q(0)*q(0)));return p;};Eigen::VectorXd q(1),v(1);q<<.3;v<<-.1;auto s=gauss(M,q,v,.2,.001,cubic,true);
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"analytic_errors\":["<<errors[0]<<','<<errors[1]<<','<<errors[2]<<"],\"nonlinear_tangent_relative\":"<<s.tangentError<<"}\n";
}
