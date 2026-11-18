#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_rail_tendon/ControlProfile.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("mass,samples,output required");Layout layout;auto shared=sharedPointReference(layout);unsigned nf=shared.nf,n=shared.M.rows(),nodes=shared.films[0].film.model.size();std::ifstream mass(argv[1]);unsigned count;mass>>count;if(count!=nodes)throw std::runtime_error("mass dimension");std::array<std::vector<double>,3>m;for(auto&values:m){values.resize(nodes);for(double&x:values)mass>>x;}double bodyMass,inertia;mass>>bodyMass>>inertia;if(!mass||bodyMass<=0||inertia<=0)throw std::runtime_error("actual public mass/inertia invalid");
 std::ifstream in(argv[2]);std::array<std::array<unsigned,2>,3>edges;for(auto&e:edges)for(auto&i:e)in>>i;unsigned samples;in>>samples;std::ofstream out(argv[3]);out<<std::setprecision(17)<<"sample,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation,unit_tendon_power,profile_tension,normal_power_Nmm_s\n";
 for(unsigned i=0;i<samples;++i){std::string name;double time;in>>name>>time;Eigen::VectorXd q(n),v(n);for(double&x:q)in>>x;for(double&x:v)in>>x;Eigen::Vector3d lambda;for(double&x:lambda)in>>x;if(!in||!q.allFinite()||!v.allFinite()||lambda.minCoeff()<0)throw std::runtime_error("finite actual samples/nonnegative applied force required");double skin=0,rails=0,attachment=0,K=0,power=0,normalPower=0;
  for(unsigned f=0;f<3;++f){auto&film=shared.films[f].film;auto x=film.expand(q.segment(f*nf,nf)),velocity=film.expand(v.segment(f*nf,nf));film.model.elements(x,1.,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)skin+=e.energy.v;else rails+=e.energy.v;}else if(e.kind==1)attachment+=e.energy.v;else if(e.kind==2)for(unsigned a=0;a<3*e.ids.size();++a)power-=e.energy.g[a]*velocity[e.ids[a/3]][a%3];});for(unsigned j=0;j<nodes;++j)K+=.5*m[f][j]*dot(velocity[j],velocity[j]);
   if(lambda(f)>0){auto rest=film.model.rest();Eigen::Vector3d body=layout.mount[f].R.transpose()*(q.segment<3>(3*nf)-layout.mount[f].origin),bv=layout.mount[f].R.transpose()*v.segment<3>(3*nf);std::vector<Point>p;for(unsigned node:edges[f]){if(node>=nodes)throw std::runtime_error("edge index invalid");p.push_back(sub(add(rest[node],x[node]),point(body)));}auto e=regrip_film_sphere::ClosestPrimitive::evaluate(p,{0,0,0},layout.bufferRadius);if(e.feature!=3)throw std::runtime_error("independent normal-power edge branch changed");double rate=0;for(unsigned a=0;a<6;++a)rate+=e.gap.g[a]*(velocity[edges[f][a/3]][a%3]-bv(a%3));normalPower+=lambda(f)*rate;}
  }
  out<<name<<','<<skin<<','<<rails<<','<<attachment<<','<<K<<','<<.5*bodyMass*v.segment<3>(3*nf).squaredNorm()<<','<<.5*inertia*v.tail<3>().squaredNorm()<<','<<power<<','<<regrip_film_rail::ControlProfile::evaluate(time,.0001,.01,.02,.03,true).tension<<','<<normalPower<<'\n';
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
