#pragma once
#include "CombinedStep.h"
#include <fstream>
namespace regrip_coupled {
struct ActualPreInput {Assembly model;std::vector<double>mass;std::vector<Point>q,v;Body body;std::vector<std::array<unsigned,3>>tri;EventControl control;double time,c,r;};
inline ActualPreInput readActualPreInput(const char*path){
 std::ifstream in(path);unsigned nx,intervals,root,count,nt;double offset,bond,start,tau,c,r;in>>nx>>intervals>>offset>>bond>>root>>start>>tau>>c>>r;
 Body body;in>>body.mass>>body.inertia;for(double&x:body.center)in>>x;for(double&x:body.linear)in>>x;for(double&x:body.angular)in>>x;for(double&x:body.force)in>>x;
 EventControl control;in>>control.maximum>>control.ramp>>control.release>>control.end>>control.c2>>count;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=root;if(count!=model.size())throw std::runtime_error("actual combined input size");
 std::vector<double>mass(count);std::vector<Point>q0(count),v0(count),q1(count),v1(count);for(double&x:mass)in>>x;for(auto*values:{&q0,&v0,&q1,&v1})for(auto&p:*values)for(double&x:p)in>>x;
 double ignored;for(unsigned i=0;i<9;++i)in>>ignored;in>>nt;std::vector<std::array<unsigned,3>>tri(nt);for(auto&t:tri)for(unsigned&i:t)in>>i;
 if(!in)throw std::runtime_error("incomplete actual combined pre-state");
 return {std::move(model),std::move(mass),std::move(q0),std::move(v0),body,std::move(tri),control,start,c,r};
}
}
