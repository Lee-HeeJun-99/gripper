#include "../../models/film_three_finger/FrameLayout.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("actual mass,samples,output required");auto shared=sharedPointReference(Layout());const unsigned nf=shared.nf,n=shared.M.rows(),nodes=shared.films[0].film.model.size();std::ifstream mass(argv[1]);unsigned count;mass>>count;if(count!=nodes)throw std::runtime_error("actual energy mass dimension");std::array<std::vector<double>,3>m;for(auto&values:m){values.resize(nodes);for(double&v:values)if(!(mass>>v)||!(v>0))throw std::runtime_error("actual energy positive nodal masses");}double bodyMass,inertia;mass>>bodyMass>>inertia;if(!(bodyMass>0&&inertia>0))throw std::runtime_error("actual energy rigid mass/inertia");std::ifstream in(argv[2]);unsigned samples;in>>samples;std::ofstream out(argv[3]);out<<std::setprecision(17)<<"sample,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation\n";
 for(unsigned i=0;i<samples;++i){std::string name;in>>name;Eigen::VectorXd q(n),v(n);for(double&x:q)in>>x;for(double&x:v)in>>x;if(!in||!q.allFinite()||!v.allFinite())throw std::runtime_error("finite actual energy sample required");double skin=0,rails=0,attachment=0,K=0;
  for(unsigned f=0;f<3;++f){auto&film=shared.films[f].film;auto x=film.expand(q.segment(f*nf,nf)),velocity=film.expand(v.segment(f*nf,nf));film.model.elements(x,0,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)skin+=e.energy.v;else rails+=e.energy.v;}if(e.kind==1)attachment+=e.energy.v;});for(unsigned j=0;j<nodes;++j)K+=.5*m[f][j]*dot(velocity[j],velocity[j]);}
  out<<name<<','<<skin<<','<<rails<<','<<attachment<<','<<K<<','<<.5*bodyMass*v.segment<3>(3*nf).squaredNorm()<<','<<.5*inertia*v.tail<3>().squaredNorm()<<'\n';
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
