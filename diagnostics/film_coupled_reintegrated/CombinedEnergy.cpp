#include "../../models/film_combined_contact/ActualStateInput.h"
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("actual mechanics,input samples,output required");auto a=readActualPreInput(argv[1]);std::ifstream in(argv[2]);unsigned samples;in>>samples;std::ofstream out(argv[3]);out<<std::setprecision(17)<<"name,time,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation,tension,cable_length,cable_power,damping_power,external_power\n";
 for(unsigned i=0;i<samples;++i){std::string name;double time;in>>name>>time;std::vector<Point>q(a.q.size()),v(a.q.size());Body body=a.body;for(auto*p:{&q,&v})for(auto&x:*p)for(double&d:x)in>>d;for(double&d:body.center)in>>d;for(double&d:body.linear)in>>d;for(double&d:body.angular)in>>d;if(!in)throw std::runtime_error("truncated actual energy sample");
  double skin=0,rails=0,attachment=0,K=0,cablePower=0;auto tension=a.control.sample(time).tension;
  a.model.elements(q,1,[&](const Element&e){if(e.kind==0){if(e.ids[0]<a.model.parts[1].offset)skin+=e.energy.v;else rails+=e.energy.v;}if(e.kind==1)attachment+=e.energy.v;if(e.kind==2)for(unsigned j=0;j<3*e.ids.size();++j)cablePower+=e.energy.g[j]*v[e.ids[j/3]][j%3];});
  for(unsigned j=0;j<v.size();++j)K+=.5*a.mass[j]*dot(v[j],v[j]);double linear=.5*body.mass*body.linear.squaredNorm(),angular=.5*body.inertia*body.angular.squaredNorm();
  out<<name<<','<<time<<','<<skin<<','<<rails<<','<<attachment<<','<<K<<','<<linear<<','<<angular<<','<<tension<<','<<a.model.cableLength(q)<<','<<cablePower<<','<<2*a.c*(K+linear+angular)<<','<<body.force.dot(body.linear)<<'\n';
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
