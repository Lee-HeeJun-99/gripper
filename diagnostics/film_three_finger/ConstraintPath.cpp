#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("samples,output required");SharedFilmSystem s(Layout(),{0,0,-.001},false,true);s.exactUnresolved=true;std::ifstream in(argv[1]);unsigned count;in>>count;std::ofstream out(argv[2]);out<<std::setprecision(17)<<"sample,gap0,gap1,gap2,rate0,rate1,rate2\n";
 for(unsigned i=0;i<count;++i){std::string name;in>>name;for(unsigned f=0;f<3;++f)in>>s.owned[f]>>s.features[f];Eigen::VectorXd q(s.initial.size()),v(q.size());for(double&x:q)in>>x;for(double&x:v)in>>x;if(!in||!q.allFinite()||!v.allFinite())throw std::runtime_error("invalid cubic-path sample");auto g=s.geometry(q);Eigen::VectorXd rate=g.J*v;out<<name;for(double x:g.gap)out<<','<<x;for(double x:rate)out<<','<<x;out<<'\n';}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
