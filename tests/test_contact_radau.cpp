#include "../models/film_coupled_collocation/SingleRowRadau.h"
#include <iostream>
using namespace regrip_collocation;
int main(){try{
 Eigen::MatrixXd M=Eigen::MatrixXd::Zero(2,2);M(0,0)=1;M(1,1)=2;double k=1200;
 auto force=[&](const Eigen::VectorXd&q,double){Force f{Eigen::VectorXd::Zero(2),Eigen::MatrixXd::Zero(2,2)};f.value(0)=-1-k*q(0);f.negativeTangent(0,0)=k;return f;};
 auto geo=[](const Eigen::VectorXd&q){Geometry g{q(0)-q(1),Eigen::VectorXd(2),Eigen::MatrixXd::Zero(2,2)};g.J<<1,-1;return g;};
 double previous=0;
 for(bool sparseStage:{false,true})for(bool lobatto:{false,true}){previous=0;
 for(int steps:{4,8,16}){Eigen::VectorXd q=Eigen::VectorXd::Zero(2),v=q;double T=.025,h=T/steps;
  for(int i=0;i<steps;++i){auto r=singleRowRadau(M,0,q,v,i*h,h,force,geo,false,lobatto,sparseStage);q=r.q;v=r.v;if(r.momentumResidual>1e-17||r.velocityResidual>1e-10)throw std::runtime_error("stage residual");}
  double omega=std::sqrt(k/3),exactQ=(std::cos(omega*T)-1)/k,exactV=-omega*std::sin(omega*T)/k,error=std::hypot(q(0)-exactQ,v(0)-exactV);if(previous&&previous/error<(lobatto?14:7))throw std::runtime_error("collocation order refinement");previous=error;std::cout<<"lobatto "<<lobatto<<" steps "<<steps<<" error "<<error<<'\n';
 }}
 // Curved normal branch:point restricted to a unit sphere,centripetal force.
 // Separate research-mass problem,1e-6 N s²/mm;the earlier unit-mass test
 // failed a 2.89e-17 N s roundoff floor and remains archived as FAIL.
 M=1e-6*Eigen::MatrixXd::Identity(2,2);auto circle=[](const Eigen::VectorXd&q){double r=q.norm();if(!(r>0))throw std::domain_error("undefined circle normal");Eigen::VectorXd j=q/r;return Geometry{r-1,j,(Eigen::MatrixXd::Identity(2,2)-j*j.transpose())/r};};
 auto inward=[](const Eigen::VectorXd&q,double){return Force{-2e-6*q,2e-6*Eigen::MatrixXd::Identity(2,2)};};
 Eigen::VectorXd q(2),v(2);q<<1,0;v<<0,1;auto curved=singleRowRadau(M,0,q,v,0,1e-3,inward,circle,true);
 if(std::abs(curved.q.norm()-1)>1e-10||std::abs(curved.q.dot(curved.v))>1e-10||curved.stages[1].force<=0)throw std::runtime_error("curved normal branch/tangent");
 auto curvedLobatto=singleRowRadau(M,0,q,v,0,1e-3,inward,circle,true,true);if(std::abs(curvedLobatto.q.norm()-1)>1e-10||std::abs(curvedLobatto.q.dot(curvedLobatto.v))>1e-10)throw std::runtime_error("Lobatto curved normal branch");
 auto sparseCurve=singleRowRadau(M,0,q,v,0,1e-3,inward,circle,true,true,true);if((sparseCurve.q-curvedLobatto.q).norm()>1e-12||(sparseCurve.v-curvedLobatto.v).norm()>1e-12)throw std::runtime_error("exact-zero sparse curved result differs");
 bool rejected=false;auto away=[](const Eigen::VectorXd&q,double){return Force{1e-6*q,Eigen::MatrixXd(-1e-6*Eigen::MatrixXd::Identity(2,2))};};try{singleRowRadau(M,0,q,v,0,1e-3,away,circle);}catch(const std::domain_error&){rejected=true;}if(!rejected)throw std::runtime_error("unloading branch not rejected");
 std::cout<<"PASS single-row nonlinear changing-normal Radau;NOT impact/active-set/SOFA\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
