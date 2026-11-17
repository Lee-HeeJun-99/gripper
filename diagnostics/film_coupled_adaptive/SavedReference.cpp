#include "../../models/film_coupled_adaptive/AdaptiveStep.h"
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace regrip_coupled_adaptive;
int main(int argc,char**argv){try{
 if(argc<3||argc>8)throw std::runtime_error("input/output,optional strict flag,trial cap,force/gap residual,event budget required");bool strict=argc>=4&&std::string(argv[3])=="strict";unsigned trials=argc>=5?std::stoul(argv[4]):384;double forceResidual=argc>=6?std::stod(argv[5]):0.,gapSolve=argc>=7?std::stod(argv[6]):1e-10;unsigned eventBudget=argc==8?std::stoul(argv[7]):0;if(trials>384||trials==0)throw std::runtime_error("trial cap1..384");std::ifstream input(argv[1]);
 unsigned nx,intervals,rootGuide,macros,count;double offset,bond,time,h,radius,damping;bool midpoint;
 input>>nx>>intervals>>offset>>bond>>rootGuide>>time>>h>>macros>>radius>>damping>>midpoint;
 if(macros>4||macros==0||h>.001||h<=0)throw std::runtime_error("saved adaptive4macro/1ms budget");
 Body body;input>>body.mass>>body.inertia;for(double&x:body.center)input>>x;for(double&x:body.linear)input>>x;for(double&x:body.angular)input>>x;
 Eigen::Vector4d quat;for(double&x:quat)input>>x;body.orientation=Eigen::Quaterniond(quat(3),quat(0),quat(1),quat(2));for(double&x:body.force)input>>x;
 EventControl control;input>>control.maximum>>control.ramp>>control.release>>control.end>>control.c2;
 input>>count;Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=rootGuide;
 if(count!=model.size())throw std::runtime_error("saved mass/state dimension");std::vector<double>mass(count);std::vector<Point>q(count),v(count),zero(count);for(double&x:mass)input>>x;for(auto&p:q)for(double&x:p)input>>x;for(auto&p:v)for(double&x:p)input>>x;if(!input)throw std::runtime_error("incomplete saved input");
 std::vector<std::array<unsigned,3>>triangles;for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);triangles.push_back({a,b,c});triangles.push_back({b,d,c});}
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,trials,rejected,accepted_segments,max_error,minimum_gap\n";unsigned total=0;
 for(unsigned macro=0;macro<macros;++macro){CoupledPlaneStep mechanics(model,mass,h,damping,control.sample(time).tension,q,v,zero,0);System system(mechanics,triangles,body,radius,strict,true,midpoint,forceResidual,gapSolve);auto accepted=adaptiveStep(system,time,control,1e-4,trials,12,&std::cerr,true,{},true,eventBudget);double gap=std::numeric_limits<double>::infinity();for(auto&s:accepted.segments)gap=std::min(gap,s.result.minimumGap);total+=accepted.segments.size();if(total>1600||gap< -1e-10)throw std::runtime_error("saved accepted step/clearance guard");q=accepted.segments.back().result.state.q;v=accepted.segments.back().result.state.v;body=accepted.segments.back().result.state.body;time+=h;out<<time<<','<<accepted.trials<<','<<accepted.rejected<<','<<accepted.segments.size()<<','<<accepted.maximumAcceptedError<<','<<gap<<'\n';out.flush();std::cout<<"macro "<<macro<<" accepted "<<accepted.segments.size()<<" trials "<<accepted.trials<<" total "<<total<<std::endl;}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
