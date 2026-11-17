#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){unsigned completed=0;try{
 if(argc!=3)throw std::runtime_error("explicit steps and output required");unsigned steps=std::stoul(argv[1]);if(steps!=4&&steps!=8&&steps!=16&&steps!=32)throw std::runtime_error("profiled4/8/16/32 independent grids only");const double horizon=1e-4,h=horizon/steps;SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);auto q=system.initial,v=Eigen::VectorXd::Zero(q.size()).eval();const unsigned nf=system.shared.nf;double time=0,external=0,damping=0,contact=0,previousEnergy=0,cumulativeResidual=0;
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,minimum_gap,U_skin,U_rails,U_attachment,K_total,external_work,damping_work,contact_work,signed_energy_residual,normal_force,body_impulse,q,v\n";
 for(;completed<steps;++completed){auto result=regrip_collocation::persistentRows(system.shared.M,2,q,v,time,h,[&](const auto&x,double){return system.force(x,0.);},[&](const auto&x){return system.geometry(x);});double gap=system.clearance(result.q);Eigen::Vector3d impulse=Eigen::Vector3d::Zero();double work=0,loss=0,cw=0;
  for(unsigned k=0;k<3;++k){const Eigen::VectorXd&x=k?result.stages[k-1].q:q;const Eigen::VectorXd&velocity=k?result.stages[k-1].v:v;Eigen::VectorXd lambda=k?result.stages[k-1].force:result.initialForce;auto g=system.geometry(x);double weight=h*(k==1?2./3:1./6);gap=std::min(gap,system.clearance(x));work+=weight*system.external.dot(velocity.segment<3>(3*nf));loss+=weight*2*velocity.dot(system.shared.M*velocity);cw+=weight*lambda.dot(g.J*velocity);impulse+=weight*g.J.block(0,3*nf,3,3).transpose()*lambda;}
  if(gap< -1e-10)throw std::runtime_error("whole three-film stage clearance failed");q=result.q;v=result.v;double skin=0,rails=0,attachment=0;
  for(unsigned f=0;f<3;++f){auto state=system.local(q,f);system.shared.films[f].film.model.elements(state.q,0,[&](const Element&e){if(e.kind==0){if(e.ids.front()<5*21)skin+=e.energy.v;else rails+=e.energy.v;}if(e.kind==1)attachment+=e.energy.v;});}
  double K=.5*v.dot(system.shared.M*v),energy=skin+rails+attachment+K;external+=work;damping+=loss;contact+=cw;cumulativeResidual+=energy-previousEnergy-work+loss-cw;previousEnergy=energy;time+=h;
  out<<time<<','<<gap<<','<<skin<<','<<rails<<','<<attachment<<','<<K<<','<<external<<','<<damping<<','<<contact<<','<<cumulativeResidual;
  auto quote=[&](const auto&values){out<<",\"";for(double x:values)out<<x<<' ';out<<'"';};quote(result.stages[1].force);quote(impulse);quote(q);quote(v);out<<'\n';out.flush();
 }
 std::cout<<"PASS independent repeated3film/T0/100us;NOT actual SOFA/full time/grasp\n";
 }catch(const std::exception&e){std::cerr<<"completed_steps="<<completed<<" failure="<<e.what()<<'\n';return 1;}}
