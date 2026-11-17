#include "../../models/film_three_finger/SharedFilmSystem.h"
#include "../../models/film_coupled_collocation/GapControlledRows.h"
#include "../../models/film_rail_tendon/ControlProfile.h"
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){unsigned completed=0;try{
 if(argc<5||argc>8)throw std::runtime_error("steps,horizon,maximum tension,output,[adaptive],[exact],[mass=FILE] required");bool adaptive=false,exact=false;std::string publicMass;for(int i=5;i<argc;++i){std::string option=argv[i];if(option=="adaptive")adaptive=true;else if(option=="exact")exact=true;else if(option.rfind("mass=",0)==0)publicMass=option.substr(5);else throw std::runtime_error("unknown driven mode");}
 unsigned steps=std::stoul(argv[1]);double duration=std::stod(argv[2]),maximum=std::stod(argv[3]);
 if((steps!=4&&steps!=8&&steps!=16&&steps!=32&&steps!=64)||!(duration>0&&duration<=.01)||!(maximum>0&&maximum<=.0001))throw std::runtime_error("bounded independent driven research pilot only");
 SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);
 system.exactUnresolved=exact;
 if(!publicMass.empty()){
  std::ifstream in(publicMass);unsigned count;in>>count;if(count!=system.shared.films[0].film.mass.size())throw std::runtime_error("public nodal mass dimensions");system.shared.M.setZero();
  for(unsigned f=0;f<3;++f){const auto&film=system.shared.films[f].film;for(unsigned i=0;i<count;++i){double mass;in>>mass;if(!(mass>0)||std::abs(mass-film.mass[i])>1e-13*film.mass[i])throw std::runtime_error("public mass differs from declared research model");for(unsigned d=0;d<3;++d){unsigned a=3*i+d;if(film.index[a]>=0)system.shared.M(f*system.shared.nf+film.index[a],f*system.shared.nf+film.index[a])+=mass*film.weight[a]*film.weight[a];}}}
  double mass,inertia;in>>mass>>inertia;if(!in||mass!=.0001||std::abs(inertia-.036)>1e-16)throw std::runtime_error("public rigid mass/inertia differ");system.shared.M.block<3,3>(3*system.shared.nf,3*system.shared.nf).diagonal().setConstant(mass);system.shared.M.block<3,3>(3*system.shared.nf+3,3*system.shared.nf+3).diagonal().setConstant(inertia);
 }
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
 std::cout<<"rational_fallbacks="<<system.exactFallbackCalls<<"\nPASS independent common C2 three-film force integration;NOT actual SOFA,full closing,wrapping or grasp\n";
 }catch(const UnresolvedDistanceOrder&e){std::ofstream out(std::string(argv[4])+".precision.csv");out<<std::setprecision(17)<<"triangle,vertex,x,y,z\n";for(unsigned t=0;t<2;++t)for(unsigned i=0;i<3;++i){out<<t<<','<<i;for(double x:(t?e.b:e.a)[i])out<<','<<x;out<<'\n';}std::cerr<<"completed_steps="<<completed<<" failure="<<e.what()<<'\n';return 1;
 }catch(const std::exception&e){std::cerr<<"completed_steps="<<completed<<" failure="<<e.what()<<'\n';return 1;}}
