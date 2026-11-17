#include "../../models/film_coupled_contact/CoupledSphere.h"
#include "../../models/film_coupled_collocation/SingleRowRadau.h"
#include "../../models/film_coupled_collocation/SystemRadau.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){try{
 if(argc!=6)throw std::runtime_error("actual post-impact input,horizon,output,lobatto flag,base steps required");bool lobatto=std::string(argv[4])=="1";unsigned baseSteps=std::stoul(argv[5]);if(!baseSteps||baseSteps>64)throw std::runtime_error("base step budget64");std::ifstream in(argv[1]);
 unsigned nx,intervals,root,count,nt;double offset,bond,start,tau,c,r;in>>nx>>intervals>>offset>>bond>>root>>start>>tau>>c>>r;
 Body b;in>>b.mass>>b.inertia;for(double&x:b.center)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;for(double&x:b.force)in>>x;
 EventControl control;in>>control.maximum>>control.ramp>>control.release>>control.end>>control.c2>>count;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=root;
 if(count!=model.size())throw std::runtime_error("actual size mismatch");
 std::vector<double>mass(count);std::vector<Point>q0(count),v0(count),q(count),v(count),zero(count);for(double&x:mass)in>>x;for(auto*values:{&q0,&v0,&q,&v})for(auto&p:*values)for(double&x:p)in>>x;
 for(double&x:b.center)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;in>>nt;std::vector<std::array<unsigned,3>>tri(nt);for(auto&t:tri)for(unsigned&i:t)in>>i;for(auto&p:v)for(double&x:p)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;if(!in)throw std::runtime_error("incomplete actual input");
 double horizon=std::stod(argv[2]);if(!(horizon>0&&horizon<=.000625&&horizon/baseSteps<=1e-5))throw std::runtime_error("bounded persistent horizon<=625us,h<=10us");
 CoupledPlaneStep film(model,mass,horizon,c,control.sample(start+tau).tension,q,v,zero,0);System s(film,tri,b,r);State initial{q,v,b};unsigned id=0;double gap=std::numeric_limits<double>::infinity();for(unsigned i=0;i<nt;++i)if(s.primitive(initial,i).gap.v<gap){gap=s.primitive(initial,i).gap.v;id=i;}
 unsigned feature=s.geometry(initial,id).feature;
 auto state=[&](const Eigen::VectorXd&x){State z=initial;z.q=film.expand(x.head(s.nf));z.body.center=x.segment<3>(s.nf);return z;};
 auto geometry=[&](const Eigen::VectorXd&x){auto row=s.geometry(state(x),id);if(row.feature!=feature)throw std::domain_error("single-row Radau feature transition;not silently frozen");return regrip_collocation::Geometry{row.gap,row.gradient,row.hessian};};
 auto force=[&](const Eigen::VectorXd&x,double time){auto z=state(x);regrip_collocation::Force f{Eigen::VectorXd::Zero(s.n),Eigen::MatrixXd::Zero(s.n,s.n)};f.value.segment<3>(s.nf)=b.force;
  model.elements(z.q,control.sample(time).tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=film.index[ga];if(i<0)continue;f.value(i)-=film.weight[ga]*e.energy.g[a];for(unsigned z=0;z<3*e.ids.size();++z){unsigned gz=3*e.ids[z/3]+z%3;int k=film.index[gz];if(k>=0)f.negativeTangent(i,k)+=film.weight[ga]*film.weight[gz]*e.energy.h[N*a+z];}}});return f;};
 Eigen::VectorXd initialQ=Eigen::VectorXd::Zero(s.n);initialQ.head(s.nf)=film.pack(q);initialQ.segment<3>(s.nf)=b.center;auto initialV=s.pack(initial);
 std::ofstream out(argv[3]);out<<std::setprecision(17)<<"steps,time,gap,normal_velocity,normal_force,stage_momentum_residual,stage_velocity_residual,q,v\n";
 for(unsigned steps:{baseSteps,2*baseSteps,4*baseSteps}){Eigen::VectorXd x=initialQ,y=initialV;double forceEnd=0,momentum=0,velocity=0;
  for(unsigned step=0;step<steps;++step){double time=start+tau+step*horizon/steps,h=horizon/steps;auto before=state(x);s.velocity(before,y);CoupledPlaneStep local(model,mass,h,c,control.sample(time).tension,before.q,before.v,zero,0);System shared(local,tri,before.body,r);auto adapter=singleRowRadauStep(shared,time,control,lobatto);auto result=regrip_collocation::singleRowRadau(s.M,c,x,y,time,h,force,geometry,false,lobatto);
   if((shared.pack(adapter.result.state)-result.v).norm()>1e-12||std::abs(adapter.stages.stages[1].force-result.stages[1].force)>1e-12)throw std::runtime_error("actual shared adapter differs from independent coordinate implementation");
   x=result.q;y=result.v;forceEnd=result.stages[1].force;momentum=std::max(momentum,result.momentumResidual);velocity=std::max(velocity,result.velocityResidual);if(s.clearance(state(x))< -1e-10)throw std::runtime_error("Radau whole-surface endpoint clearance FAIL");}
  auto row=geometry(x);out<<steps<<','<<start+tau+horizon<<','<<s.clearance(state(x))<<','<<row.J.dot(y)<<','<<forceEnd<<','<<momentum<<','<<velocity<<",\"";for(double z:x)out<<z<<' ';out<<"\",\"";for(double z:y)out<<z<<' ';out<<"\"\n";out.flush();
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
