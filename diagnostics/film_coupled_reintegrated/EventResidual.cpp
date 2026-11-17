#include "../../models/film_coupled_contact/CoupledSphere.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("explicit actual event input and output required");std::ifstream input(argv[1]);
 unsigned nx,intervals,rootGuide,count,triangleCount;double offset,bond,start,tau,damping,radius;input>>nx>>intervals>>offset>>bond>>rootGuide>>start>>tau>>damping>>radius;
 Body body;input>>body.mass>>body.inertia;for(double&x:body.center)input>>x;for(double&x:body.linear)input>>x;for(double&x:body.angular)input>>x;for(double&x:body.force)input>>x;
 EventControl control;input>>control.maximum>>control.ramp>>control.release>>control.end>>control.c2;input>>count;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=rootGuide;if(count!=model.size()||tau<=0)throw std::runtime_error("actual event state dimensions/time");
 std::vector<double>mass(count);std::vector<Point>q0(count),v0(count),q1(count),v1(count),zero(count);for(double&x:mass)input>>x;for(auto*values:{&q0,&v0,&q1,&v1})for(auto&p:*values)for(double&x:p)input>>x;
 State actual{q1,v1,body};for(double&x:actual.body.center)input>>x;for(double&x:actual.body.linear)input>>x;for(double&x:actual.body.angular)input>>x;input>>triangleCount;std::vector<std::array<unsigned,3>>triangles(triangleCount);for(auto&t:triangles)for(unsigned&i:t)input>>i;if(!input)throw std::runtime_error("incomplete actual event input");
 CoupledPlaneStep mechanics(model,mass,tau,damping,control.sample(start).tension,q0,v0,zero,0);System system(mechanics,triangles,body,radius);Eigen::VectorXd before=system.pack(system.before),after=system.pack(actual),middle=(before+after)/2;
 auto evaluation=system.evaluate(middle,control.sample(start+tau/2).tension);auto expected=system.endpoint(middle);double position=0;for(unsigned i=0;i<count;++i)for(unsigned d=0;d<3;++d)position=std::max(position,std::abs(actual.q[i][d]-expected.q[i][d]));
 double impulse=(system.M*(after-before)).norm(),residual=2*evaluation.gradient.norm(),bodyPosition=(actual.body.center-expected.body.center).norm();
 if(!std::isfinite(residual+position+bodyPosition+impulse))throw std::runtime_error("nonfinite actual midpoint residual diagnostic");
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"tau,partial_midpoint_momentum_residual,force_equivalent_residual,position_update_error,body_position_update_error,net_momentum_change,relative_momentum_defect\n"<<tau<<','<<residual<<','<<residual/tau<<','<<position<<','<<bodyPosition<<','<<impulse<<',';if(impulse>0)out<<residual/impulse;else out<<"null";out<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
