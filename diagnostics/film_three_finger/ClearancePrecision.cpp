#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("checkpoint,output required");std::ifstream in(argv[1]);std::string magic,token;double time,dt;unsigned step;in>>magic>>time>>dt>>step>>token;SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q(s.initial.size());for(double&x:q)in>>x;if(!in||magic!="REGRIP_PERSISTENT_V1")throw std::runtime_error("checkpoint q missing");std::ofstream out(argv[2]);out<<std::setprecision(17)<<"finger,triangle,feature,AD_gap_mm,high_precision_gap_mm,selected,coordinates\n";using H=boost::multiprecision::cpp_bin_float_100;
 for(unsigned f=0;f<3;++f){auto state=s.local(q,f);const auto&system=s.shared.films[f];auto rest=system.film.model.rest();auto selected=s.selected(q,f);for(unsigned k=0;k<system.triangles.size();++k){auto e=system.primitive(state,k);TriangleCoordinates x;for(unsigned a=0;a<3;++a){unsigned node=system.triangles[k][a];x[a]=sub(add(rest[node],state.q[node]),point(state.body.center));}H squared=preciseSquaredDistance<H>(x);H gap=sqrt(squared)-H(s.layout.bufferRadius);out<<f<<','<<k<<','<<e.feature<<','<<e.gap.v<<','<<gap<<','<<(selected.triangle==k)<<",\"";for(auto p:x)for(double d:p)out<<d<<' ';out<<"\"\n";}}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
