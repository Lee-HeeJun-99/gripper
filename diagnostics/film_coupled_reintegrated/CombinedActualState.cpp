#include "../../models/film_combined_contact/ActualStateInput.h"
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){try{
 if(argc!=6)throw std::runtime_error("actual pre-impact input,horizon,output,base steps,sparse flag required");auto input=readActualPreInput(argv[1]);double H=std::stod(argv[2]);unsigned base=std::stoul(argv[4]);bool sparseStage=std::string(argv[5])=="1";if(!(H>0&&H<=.000125)||base<4||base>16||H/base>1e-5)throw std::runtime_error("profile-bounded combined pilot horizon/steps");
 std::ofstream out(argv[3]);out<<std::setprecision(17)<<"steps,time,events,event_time,impulse,gap,normal_after,body_center,body_velocity,local_displacement,local_velocity\n";
 for(unsigned steps:{base,2*base,4*base}){State state{input.q,input.v,input.body};unsigned events=0;double birth=0,impulse=0,normal=0,gap=0,clock=input.time;
  // Same finite-precision clock protocol as the actual SOFA animation loop.
  // Independent start+=dt;no observed SOFA times/positions are injected.
  for(unsigned k=0;k<steps;++k){double h=H/steps;CoupledPlaneStep film(input.model,input.mass,h,input.c,input.control.sample(clock).tension,state.q,state.v,std::vector<Point>(state.q.size()),0);System system(film,input.tri,state.body,input.r,true,true,true,1e-17,1e-14);auto accepted=combinedStep(system,clock,input.control,sparseStage);if(accepted.result.event){++events;birth=clock+h*accepted.result.event->fraction;impulse+=accepted.result.impact->state.impulse.sum();normal=accepted.result.impact->state.normalVelocity.minCoeff();}state=accepted.result.state;gap=std::min(gap,accepted.result.minimumGap);clock+=h;}
  if(events!=1)throw std::runtime_error("combined coupon did not process exactly one physical event");out<<steps<<','<<clock<<','<<events<<','<<birth<<','<<impulse<<','<<gap<<','<<normal;
  for(const auto*value:{&state.body.center,&state.body.linear}){out<<",\"";for(double x:*value)out<<x<<' ';out<<'"';}
  for(const auto*value:{&state.q,&state.v}){out<<",\"";for(auto p:*value)for(double x:p)out<<x<<' ';out<<'"';}out<<'\n';out.flush();
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
