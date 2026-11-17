#include "../../models/film_combined_contact/ActualStateInput.h"
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("actual pre-state,physical clocks,output required");auto a=readActualPreInput(argv[1]);std::ifstream times(argv[2]);unsigned steps;double h;times>>steps>>h;if(steps>64||!(h>0&&h<=1e-5))throw std::runtime_error("bounded replay clocks");State state{a.q,a.v,a.body};std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time,local_displacement,local_velocity,body_center,body_velocity\n";
 for(unsigned i=0;i<steps;++i){double time;times>>time;if(!times)throw std::runtime_error("missing actual macro clock");CoupledPlaneStep film(a.model,a.mass,h,a.c,a.control.sample(time).tension,state.q,state.v,std::vector<Point>(state.q.size()),0);System system(film,a.tri,state.body,a.r,true,true,true,1e-17,1e-14);state=combinedStep(system,time,a.control).result.state;out<<time+h;
  for(const auto*values:{&state.q,&state.v}){out<<",\"";for(auto p:*values)for(double x:p)out<<x<<' ';out<<'"';}for(const auto*values:{&state.body.center,&state.body.linear}){out<<",\"";for(double x:*values)out<<x<<' ';out<<'"';}out<<'\n';out.flush();
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
