#include "../models/film_impact/ProjectedImpact.h"
#include <iostream>
using namespace regrip_film_impact;
void check(bool b){if(!b)throw std::runtime_error("impact reference mismatch");}
int main(){try{
 Eigen::MatrixXd M=2*Eigen::MatrixXd::Identity(3,3),J(1,3);J<<1,0,0;
 Eigen::VectorXd v(3);v<<-3,4,2;
 for(double e:{0.,.5,1.}){auto r=solve(M,J,v,e,1e-12,1e-12);
  check(std::abs(r.velocity(0)-3*e)<1e-12&&r.velocity(1)==4&&r.velocity(2)==2);
  check(std::abs(r.impulse(0)-6*(1+e))<1e-12&&r.momentumResidual<1e-12);
  check(std::abs(r.energyLoss-9*(1-e*e))<1e-12);}
 // Root slave projection: physical [y, y/4], not the raw first nodal mass.
 Eigen::MatrixXd B(2,1);B<<1,.25;Eigen::VectorXd m(2);m<<2,8;
 auto P=projectedMass(B,m);check(P(0,0)==2.5);
 Eigen::MatrixXd C(1,1);C<<1;Eigen::VectorXd u(1);u<<-2;
 auto p=solve(P,C,u,0,1e-12,1e-12);check(p.impulse(0)==5&&p.velocity(0)==0);
 // Coupled rows and redundant support; only resultant impulse is unique.
 Eigen::MatrixXd K(3,3);K<<1,0,0, 0,1,0, 1,0,0;v<<-3,-2,4;
 auto r=solve(M,K,v,0,1e-12,1e-12);
 check(r.velocity.head(2).norm()<1e-12&&r.velocity(2)==4&&r.momentumResidual<1e-12);
 auto repeat=solve(M,K,v,0,1e-12,1e-12);check(r.impulse==repeat.impulse);
 // Smooth fixed-active-set tangent, central FD with respect to v^-.
 Eigen::MatrixXd tangent=Eigen::MatrixXd::Identity(3,3);tangent(0,0)=0;
 for(int i=0;i<3;++i){auto a=v,b=v;a(i)+=1e-5;b(i)-=1e-5;
  Eigen::VectorXd fd=(solve(M,J,a,0,1e-12,1e-12).velocity-solve(M,J,b,0,1e-12,1e-12).velocity)/2e-5;
  check((fd-tangent.col(i)).norm()<1e-9);}
 // Orthogonal change of spatial frame must preserve impulse and energy.
 Eigen::Matrix3d Q;Q<<0,-1,0,1,0,0,0,0,1;
 auto a=solve(M,J,v,0,1e-12,1e-12),b=solve(Q*M*Q.transpose(),J*Q.transpose(),Q*v,0,1e-12,1e-12);
 check((b.velocity-Q*a.velocity).norm()<1e-12&&b.impulse==a.impulse);
 bool rejected=false;try{solve(-M,J,v,0,1e-12,1e-12);}catch(const std::runtime_error&){rejected=true;}check(rejected);
 std::cout<<"PASS independent projected impact: restitution, oblique, root mass, coupled/redundant rows, tangent, objectivity, rejection\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
