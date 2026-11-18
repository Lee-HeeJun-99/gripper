#include "RoutedCheckpoint.h"
#include "../../models/film_lateral_tendon/Route.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{
 using namespace regrip_three_finger;using namespace regrip_film_rail;
 if(argc!=4)throw std::runtime_error("actual checkpoint,stage samples,output required");SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q0,v0;double start,h;regrip_routed_checkpoint::read(argv[1],s,q0,v0,start,h);unsigned n=q0.size(),nf=s.shared.nf,body=3*nf;
 std::ifstream in(argv[2]);unsigned count;in>>count;if(!in||count<2||count>600)throw std::runtime_error("bounded complete actual release sample count required");std::ofstream out(argv[3]);out<<std::setprecision(17)<<"kind,time,weight,T,tendon_power,normal_power,damping_power,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation\n";
 for(unsigned sample=0;sample<count;++sample){char kind;double time,weight;Eigen::VectorXd force(3),q(n),v(n);in>>kind>>time>>weight;for(double&x:force)in>>x;for(double&x:q)in>>x;for(double&x:v)in>>x;if(!in||!q.allFinite()||!v.allFinite()||force.minCoeff()<0||weight<0||time<start||time>start+h)throw std::runtime_error("finite actual non-tensile stage sample required");
  double T=regrip_film_rail::ControlProfile::evaluate(time,.0001,.01,.02,.03,true).tension;long double tendon=0,normal=0;double skin=0,rails=0,bond=0;
  for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f].film;auto x=film.expand(q.segment(f*nf,nf)),vel=film.expand(v.segment(f*nf,nf));
   regrip_lateral_tendon::route(film.model,x,T,6,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)tendon-=static_cast<long double>(e.energy.g[a])*vel[e.ids[a/3]][a%3];});
   if(kind=='E')film.model.elements(x,0,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)skin+=e.energy.v;else rails+=e.energy.v;}if(e.kind==1)bond+=e.energy.v;});
   if(force(f)>0){auto row=s.shared.films[f].geometry(s.local(q,f),116);double vn=row.gradient.head(nf).dot(v.segment(f*nf,nf))+row.gradient.segment<3>(nf).dot(s.layout.mount[f].R.transpose()*v.segment<3>(body));if(row.feature!=6||std::abs(row.gap)>1e-10||std::abs(vn)>1e-10)throw std::runtime_error("positive actual reaction outside fixed touching tangent face");normal+=static_cast<long double>(force(f))*vn;}
  }
  long double Kf=0,Kl=0,Kr=0,damping=0;for(unsigned i=0;i<n;++i){long double value=.5L*s.shared.M(i,i)*v(i)*v(i);if(i<body)Kf+=value;else if(i<body+3)Kl+=value;else Kr+=value;damping+=4*value;}
  out<<kind<<','<<time<<','<<weight<<','<<T<<','<<tendon<<','<<normal<<','<<damping<<','<<skin<<','<<rails<<','<<bond<<','<<Kf<<','<<Kl<<','<<Kr<<'\n';
 }
 std::string extra;if(in>>extra)throw std::runtime_error("trailing stage sample data");
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
