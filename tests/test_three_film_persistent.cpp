#include "../models/film_three_finger/SharedFilmSystem.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 double load=argc>1?std::stod(argv[1]):-1e-3,h=argc>2?std::stod(argv[2]):1e-4;
 if(argc>5||(argc==5&&std::string(argv[4])!="rescan"&&std::string(argv[4])!="precise")||!(h>0&&h<=1e-4)||!std::isfinite(load)||std::abs(load)>1e-3)throw std::runtime_error("bounded explicit three-film research load/step");
 bool precise=argc==5&&std::string(argv[4])=="precise",rescan=argc==5;SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,load),rescan,precise);auto q=system.initial,v=Eigen::VectorXd::Zero(q.size()).eval();
 if(argc>=4)system.ambiguityObserver=[&](const Eigen::VectorXd&x,unsigned finger,const Row&a,const Row&b){
  std::string path=std::string(argv[3])+".rejected.csv";if(std::ifstream(path))throw std::runtime_error("rejected-state observer destination exists");std::ofstream out(path);out<<std::setprecision(17)<<"finger,triangle_a,feature_a,gap_a,triangle_b,feature_b,gap_b,gradient_difference,q,j_a,j_b\n"<<finger<<','<<a.triangle<<','<<a.feature<<','<<a.gap<<','<<b.triangle<<','<<b.feature<<','<<b.gap<<','<<(a.gradient-b.gradient).norm();for(const auto*values:{&x,&a.gradient,&b.gradient}){out<<",\"";for(double value:*values)out<<value<<' ';out<<'"';}out<<'\n';
 };
 auto geometry=[&](const Eigen::VectorXd&x){return system.geometry(x);};
 // Explicit research IVP,NOT earlier834/835 nor tendon-driven closing.
 auto force=[&](const Eigen::VectorXd&x,double){return system.force(x,0.);};
 auto before=geometry(q);if(before.gap.cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("initial three-film geometry");
 auto result=regrip_collocation::persistentRows(system.shared.M,2.,q,v,0,h,force,geometry);
 double gap=system.clearance(result.q);
 if(gap< -1e-10||result.initialForce.minCoeff()<0||result.momentumResidual>1e-17||result.velocityResidual>1e-10)throw std::runtime_error("three-film persistent physical gate");
 if(argc>=4){std::ofstream out(argv[3]);out<<std::setprecision(17)<<"q,v\n\"";for(double x:result.q)out<<x<<' ';out<<"\",\"";for(double x:result.v)out<<x<<' ';out<<"\"\n";}
 std::cout<<std::setprecision(17)<<"PASS independent three-film/ONE free sphere nonlinear FEM persistent branch;NOT actual SOFA/grasp\nDOFs "<<q.size()<<"\nexternal_Fz_N "<<load<<"\nduration_s "<<h<<"\nminimum_whole_triangle_gap "<<gap<<"\nmomentum_residual "<<result.momentumResidual<<"\nnormal_velocity_residual "<<result.velocityResidual<<"\ninitial_reactions "<<result.initialForce.transpose()<<"\nend_reactions "<<result.stages[1].force.transpose()<<"\nbody_displacement "<<(result.q.segment<3>(3*system.shared.nf)-q.segment<3>(3*system.shared.nf)).transpose()<<"\niterations "<<result.iterations<<"\nevaluations "<<result.evaluations<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
