#include "../models/film_coupled_collocation/EndpointControlledRows.h"
#include <iostream>
#include <iomanip>
using namespace regrip_collocation;
int main(){try{
 // 1g expressed in N*s^2/mm,not a unit-mass rescaling of acceptance gates.
 Eigen::MatrixXd M=1e-6*Eigen::MatrixXd::Identity(2,2);Eigen::VectorXd q(2),v(2);q<<1,0;v<<0,1;
 auto geometry=[](const Eigen::VectorXd&x){double r=x.norm();if(!(r>0))throw std::domain_error("undefined sphere normal");RowGeometry g{Eigen::VectorXd(1),x.transpose()/r,{Eigen::MatrixXd::Identity(2,2)/r-x*x.transpose()/(r*r*r)}};g.gap<<r-1;return g;};
 auto force=[](const Eigen::VectorXd&x,double){double r=x.norm();Force f{-4e-6*x/r,4e-6*(Eigen::MatrixXd::Identity(2,2)/r-x*x.transpose()/(r*r*r))};return f;};
 auto gap=[](const Eigen::VectorXd&x){return x.norm()-1;};
 auto result=endpointControlledRows(M,0,q,v,0,.1,force,geometry,gap);
 double minimum=0,maximum=0,impulse=0;for(const auto&step:result.accepted)for(const auto&s:step.stages){minimum=std::min(minimum,gap(s.q));maximum=std::max(maximum,std::abs(gap(s.q)));impulse=std::max(impulse,s.force.minCoeff());if(s.force.minCoeff()<0)throw std::runtime_error("negative unilateral force");}
 Eigen::VectorXd reference(2);reference<<std::cos(.1),std::sin(.1);double error=(result.q-reference).norm();
 std::cerr<<std::setprecision(17)<<"circle attempts="<<result.attempts<<" stage_rejected="<<result.stageRejected<<" endpoint_rejected="<<result.endpointRejected<<" max_gap="<<maximum<<" analytic_error="<<error<<'\n';
 if(!(result.endpointRejected+result.stageRejected)||maximum>1e-10||minimum< -1e-10||error>1e-6)throw std::runtime_error("curved reference/gap gate failed");
 bool release=false;try{auto separating=[](const Eigen::VectorXd&,double){return Force{Eigen::VectorXd::Zero(2),Eigen::MatrixXd::Zero(2,2)};};endpointControlledRows(M,0,q,v,0,.1,separating,geometry,gap);}catch(const std::domain_error&){release=true;}
 if(!release)throw std::runtime_error("release was hidden as refinement");
 bool budget=false;try{endpointControlledRows(M,0,q,v,0,.1,force,geometry,gap,63,0);}catch(const std::runtime_error&){budget=true;}
 if(!budget)throw std::runtime_error("depth budget ignored");
 // Nonquadratic holonomic curve y=L*sin(x/L),L=1mm. Generalized multiplier
 // uses the gradient of this defining function,not a unit-normal force.
 Eigen::VectorXd sineQ(2),sineV(2);sineQ<<.2,std::sin(.2);sineV<<.5,.5*std::cos(.2);
 auto sineGeometry=[](const Eigen::VectorXd&x){RowGeometry g{Eigen::VectorXd(1),Eigen::MatrixXd::Zero(1,2),{Eigen::MatrixXd::Zero(2,2)}};g.gap<<x(1)-std::sin(x(0));g.J<<-std::cos(x(0)),1;g.H[0](0,0)=std::sin(x(0));return g;};
 auto gravity=[](const Eigen::VectorXd&,double){Force f{Eigen::VectorXd(2),Eigen::MatrixXd::Zero(2,2)};f.value<<0,-4e-6;return f;};
 auto sineGap=[](const Eigen::VectorXd&x){return x(1)-std::sin(x(0));};
 auto sine=endpointControlledRows(M,0,sineQ,sineV,0,.1,gravity,sineGeometry,sineGap);
 auto ode=[](Eigen::Vector2d x){double c=std::cos(x[0]),s=std::sin(x[0]);return Eigen::Vector2d(x[1],-c*(4-s*x[1]*x[1])/(1+c*c));};
 auto referenceSine=[&](unsigned steps){Eigen::Vector2d x(.2,.5);double h=.1/steps;for(unsigned i=0;i<steps;++i){Eigen::Vector2d a=ode(x),b=ode(x+h*a/2),c=ode(x+h*b/2),d=ode(x+h*c);x+=h*(a+2*b+2*c+d)/6;}return x;};
 auto coarseRef=referenceSine(10000),fineRef=referenceSine(20000);Eigen::Vector2d refQ(fineRef[0],std::sin(fineRef[0]));
 double sineError=(sine.q-refQ).norm(),sineMaximum=0;for(const auto&step:sine.accepted)for(const auto&stage:step.stages)sineMaximum=std::max(sineMaximum,std::abs(sineGap(stage.q)));
 std::cerr<<"sine endpoint="<<sine.endpointRejected<<" stage="<<sine.stageRejected<<" gap="<<sineMaximum<<" error="<<sineError<<" ref_difference="<<(coarseRef-fineRef).norm()<<'\n';
 if(!sine.endpointRejected||sineMaximum>1e-10||sineError>1e-6||(coarseRef-fineRef).norm()>1e-12)throw std::runtime_error("nonquadratic endpoint branch/reference fails");
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"attempts\":"<<result.attempts<<",\"endpoint_rejected\":"<<result.endpointRejected<<",\"stage_rejected\":"<<result.stageRejected<<",\"maximum_abs_gap\":"<<maximum<<",\"analytic_position_error\":"<<error<<",\"sine_endpoint_rejected\":"<<sine.endpointRejected<<",\"sine_stage_rejected\":"<<sine.stageRejected<<",\"sine_maximum_abs_gap\":"<<sineMaximum<<",\"sine_numeric_reference_error\":"<<sineError<<",\"sine_RK_reference_refinement_difference\":"<<(coarseRef-fineRef).norm()<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
