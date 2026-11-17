#include "../../models/film_three_finger/FrameLayout.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("recorded public mass input required");auto system=sharedPointReference(Layout());std::ifstream in(argv[1]);unsigned count;in>>count;if(count!=system.films[0].film.mass.size())throw std::runtime_error("mass dimensions");unsigned different=0;double maximum=0;std::cout<<std::setprecision(17);
 for(unsigned f=0;f<3;++f)for(unsigned i=0;i<count;++i){double value;in>>value;double assumed=system.films[f].film.mass[i];if(value!=assumed){++different;maximum=std::max(maximum,std::abs(value-assumed)/assumed);if(different<=8)std::cout<<"different finger="<<f<<" node="<<i<<" assumed="<<assumed<<" public="<<value<<" assumed_hex="<<std::hexfloat<<assumed<<" public_hex="<<value<<std::defaultfloat<<'\n';}}
 double m,I;in>>m>>I;if(!in)throw std::runtime_error("public mass parse");std::cout<<"different_nodes="<<different<<"\nmaximum_relative_mass_difference="<<maximum<<"\nbody_mass_difference="<<m-system.M(3*system.nf,3*system.nf)<<"\ninertia_difference="<<I-system.M(3*system.nf+3,3*system.nf+3)<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
