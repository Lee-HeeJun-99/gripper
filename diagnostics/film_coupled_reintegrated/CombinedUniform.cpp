#include "../../models/film_combined_contact/ActualStateInput.h"
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){unsigned step=0;double clock=0;try{
 if(argc!=5)throw std::runtime_error("pre-state,horizon,steps,output required");auto a=readActualPreInput(argv[1]);double duration=std::stod(argv[2]);unsigned steps=std::stoul(argv[3]);if(!(duration>0&&duration<=.001)||steps<16||steps>512||duration/steps>1e-5)throw std::runtime_error("profiled uniform1ms/512step/10us budget");double h=duration/steps;clock=a.time;State state{a.q,a.v,a.body};std::ofstream out(argv[4]);out<<std::setprecision(17)<<"time,minimum_gap,event,impulse,normal_after,body_center,body_velocity,local_displacement,local_velocity\n";unsigned atoms=0;
 for(;step<steps;++step){CoupledPlaneStep film(a.model,a.mass,h,a.c,a.control.sample(clock).tension,state.q,state.v,std::vector<Point>(state.q.size()),0);System s(film,a.tri,state.body,a.r,true,true,true,1e-17,1e-14);auto result=combinedStep(s,clock,a.control,true);state=result.result.state;if(result.result.event)++atoms;clock+=h;out<<clock<<','<<result.result.minimumGap<<','<<bool(result.result.event)<<','<<(result.result.impact?result.result.impact->state.impulse.sum():0)<<',';
  if(result.result.impact)out<<result.result.impact->state.normalVelocity.minCoeff();else out<<"null";
  for(const auto*p:{&state.body.center,&state.body.linear}){out<<",\"";for(double x:*p)out<<x<<' ';out<<'"';}for(const auto*p:{&state.q,&state.v}){out<<",\"";for(auto x:*p)for(double d:x)out<<d<<' ';out<<'"';}out<<'\n';out.flush();
 }if(atoms!=1)throw std::runtime_error("isolated uniform reference event count differs");
 }catch(const std::exception&e){std::cerr<<std::setprecision(17)<<"step="<<step<<" physical_time="<<clock<<" failure="<<e.what()<<'\n';return 1;}}
