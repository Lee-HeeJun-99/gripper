#include "../../models/film_three_finger/SharedFilmSystem.h"
#include "../../models/film_coupled_collocation/GapControlledRows.h"
#include "../../models/film_rail_tendon/ControlProfile.h"
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){unsigned completed=0;try{
 if(argc!=5&&argc!=6)throw std::runtime_error("steps,horizon,maximum tension,output,[adaptive] required");bool adaptive=argc==6&&std::string(argv[5])=="adaptive";
 unsigned steps=std::stoul(argv[1]);double duration=std::stod(argv[2]),maximum=std::stod(argv[3]);
 if((steps!=4&&steps!=8&&steps!=16&&steps!=32)||!(duration>0&&duration<=.01)||!(maximum>0&&maximum<=.0001))throw std::runtime_error("bounded independent driven research pilot only");
 SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);
 auto q=system.initial,v=Eigen::VectorXd::Zero(q.size()).eval();double time=0,h=duration/steps;
 std::ofstream out(argv[4]);out<<std::setprecision(17)<<"time,tension,minimum_gap,momentum_residual,normal_velocity_residual,iterations,attempts,rejected,q,v\n";
 auto tension=[&](double t){return regrip_film_rail::ControlProfile::evaluate(t,maximum,duration,2*duration,3*duration,true).tension;};
 for(;completed<steps;++completed){
  auto force=[&](const Eigen::VectorXd&x,double t){return system.force(x,tension(t));};auto geometry=[&](const Eigen::VectorXd&x){return system.geometry(x);};
  regrip_collocation::GapControlledResult path;
  if(adaptive)path=regrip_collocation::gapControlledRows(system.shared.M,2,q,v,time,h,force,geometry,[&](const Eigen::VectorXd&x){return system.clearance(x);});
  else{path.accepted.push_back(regrip_collocation::persistentRows(system.shared.M,2,q,v,time,h,force,geometry));path.attempts=1;}
  const auto&result=path.accepted.back();double gap=system.clearance(result.q);for(const auto&leaf:path.accepted)for(const auto&stage:leaf.stages)gap=std::min(gap,system.clearance(stage.q));
  std::cerr<<std::setprecision(17)<<"attempt="<<completed<<" time="<<time<<" dt="<<h<<" midpoint_whole_gap="<<system.clearance(result.stages[0].q)<<" endpoint_whole_gap="<<system.clearance(result.q)<<" selected_midpoint_gap="<<result.stages[0].geometry.gap.transpose()<<" selected_endpoint_gap="<<result.stages[1].geometry.gap.transpose()<<'\n';
  if(gap< -1e-10){
   std::ofstream failed(std::string(argv[4])+".rejected.csv");failed<<std::setprecision(17)<<"stage,time,whole_gap,owned_gap,q,v\n";
   for(unsigned k=0;k<2;++k){const auto&s=result.stages[k];auto g=system.geometry(s.q);failed<<k<<','<<s.time<<','<<system.clearance(s.q)<<",\""<<g.gap.transpose()<<"\",\"";for(double x:s.q)failed<<x<<' ';failed<<"\",\"";for(double x:s.v)failed<<x<<' ';failed<<"\"\n";}
   throw std::runtime_error("driven whole-stage clearance failed");
  }
  q=result.q;v=result.v;time+=h;out<<time<<','<<tension(time)<<','<<gap<<','<<result.momentumResidual<<','<<result.velocityResidual<<','<<result.iterations<<','<<path.attempts<<','<<path.rejected;
  for(const auto*values:{&q,&v}){out<<",\"";for(double x:*values)out<<x<<' ';out<<'"';}out<<'\n';out.flush();
 }
 std::cout<<"PASS independent common C2 three-film force integration;NOT actual SOFA,full closing,wrapping or grasp\n";
 }catch(const std::exception&e){std::cerr<<"completed_steps="<<completed<<" failure="<<e.what()<<'\n';return 1;}}
