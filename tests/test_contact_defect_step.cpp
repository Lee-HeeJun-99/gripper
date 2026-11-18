#include "../models/film_routed_contact/DefectStep.h"
#include <iostream>
using namespace regrip_defect_step;
int main(int argc,char**argv){
 // Separate explicitly named physical scales;unit-mass failure is NOT erased.
 const double mass=argc==2&&std::string(argv[1])=="gram"?1e-6:1.;
 Eigen::MatrixXd M=mass*Eigen::MatrixXd::Identity(2,2);auto force=[&](const Eigen::VectorXd&q,double){return Force{-2*mass*q,2*mass*Eigen::MatrixXd::Identity(2,2)};};
 auto geometry=[](const Eigen::VectorXd&q){double r=q.norm();if(r==0)throw std::domain_error("undefined circle normal");RowGeometry g;g.gap=Eigen::VectorXd::Constant(1,r-1);g.J=q.transpose()/r;g.H={Eigen::MatrixXd::Identity(2,2)/r-q*q.transpose()/(r*r*r)};return g;};
 auto gap=[](const Eigen::VectorXd&q){return q.norm()-1;};
 Eigen::VectorXd q(2),v(2);q<<1,0;v<<0,1;unsigned rejected=0;double error=0,minimum=0;
 for(unsigned n:{1u,2u,4u}){auto x=q,y=v;double t=0;for(unsigned k=0;k<n;++k){auto r=integrate(M,0,x,y,t,.2/n,force,geometry,gap);for(const auto&leaf:r.leaves){if(leaf.result.momentumResidual>1e-17||leaf.result.velocityResidual>1e-10||leaf.result.initialForce.minCoeff()<0)throw std::runtime_error("physical stage gate");}x=r.q;y=r.v;t+=.2/n;rejected+=r.rejected;minimum=std::min(minimum,r.minimumGap);}Eigen::Vector2d exact(std::cos(.2),std::sin(.2)),ev(-std::sin(.2),std::cos(.2));error=std::max(error,(x-exact).norm()+(y-ev).norm());}
 if(!rejected||minimum< -1e-10||error>.001)throw std::runtime_error("circle analytic/refinement gate");
 std::cout<<"PASS circle analytic q/v,nonnegative reactions,no projection;mass="<<mass<<",error="<<error<<",rejections="<<rejected<<",gap="<<minimum<<'\n';
}
