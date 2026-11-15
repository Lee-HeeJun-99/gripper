#include "../../models/conservative_beam/EnergyKernel.h"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
// OFFLINE evaluation of actual saved SOFA states with the frozen rod strain
// kernel. No SOFA stepping, missing energies or dissipation are inferred here.
int main(int argc,char**argv){try{
 if(argc!=3)throw std::invalid_argument("INPUT OUTPUT");
 std::ifstream in(argv[1]);std::ofstream out(argv[2]);if(!in||!out)throw std::runtime_error("energy files");
 int nodes,frames;in>>nodes>>frames;regrip_beam::Properties m;in>>m.EA>>m.GAy>>m.GAz>>m.GJ>>m.EIy>>m.EIz;m.validate();if(nodes<3||nodes>41||frames<1||frames>10000)throw std::invalid_argument("bounded journal dimensions");int total=6*nodes+1;std::vector<regrip_beam::Pose>rest(total),x(total);std::vector<regrip_beam::Reference>references;out<<std::setprecision(17)<<"time,beam_U,kinetic_K\n";
 for(int frame=0;frame<frames;++frame){double t;in>>t;double K=0;for(int i=0;i<total;++i){for(auto&v:x[i].p)in>>v;for(auto&v:x[i].q)in>>v;double v[6];for(auto&a:v)in>>a;double mass=i==total-1?.0001:.00006/(total-1),inertia=i==total-1?10:1;for(int j=0;j<6;++j)K+=.5*mass*(j<3?1:inertia)*v[j]*v[j];}
  if(!in)throw std::runtime_error("truncated energy input");
  if(!frame){rest=x;for(int layer=0;layer<6;++layer)for(int i=0;i<nodes-1;++i){int a=layer*nodes+i;references.push_back(regrip_beam::reference(rest[a],rest[a+1]));}}
  double U=0;int edge=0;auto material=m.values();for(int layer=0;layer<6;++layer)for(int i=0;i<nodes-1;++i,++edge){int a=layer*nodes+i;const auto&r=references[edge];auto s=regrip_beam::strains(x[a],x[a+1],r.length,false);for(int j=0;j<3;++j){double g=s.gamma[j].v-r.gamma[j],k=s.kappa[j].v-r.kappa[j];U+=.5*r.length*(material[j]*g*g+material[j+3]*k*k);}}
  out<<t<<','<<U<<','<<K<<'\n';}
 std::cout<<"PASS offline stored beam energy and isotropic kinetic journal "<<frames<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
