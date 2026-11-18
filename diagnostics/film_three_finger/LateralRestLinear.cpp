#include "../../models/film_lateral_tendon/Step.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_lateral_tendon;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("actual public mass,matrix output required");auto m=model();std::vector<Point>q(m.size()),v(q.size());auto map=mechanics(m,q,v,.0001,0,publicMass(argv[1]));auto rest=parts(map,q,0,6),unit=parts(map,q,1,6);Eigen::MatrixXd M=filmMass(map);if(rest.force.norm()>1e-14||(rest.stiffness-rest.stiffness.transpose()).norm()>1e-12)throw std::runtime_error("rest equilibrium/tangent symmetry fails");std::ofstream out(argv[2]);out<<std::setprecision(17)<<map.freeSize<<'\n'<<M.diagonal().transpose()<<'\n'<<unit.tendon.transpose()<<'\n'<<rest.stiffness<<'\n';std::cout<<"PASS actual-mass frozen-rest lateral tangent/forcing export;NOT measured dynamic mode/completion time\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
