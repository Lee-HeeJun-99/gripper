#include "../models/film_sphere_contact/SphereStep.h"
#include "../models/film_native_contact/CoupledBDFHistory.h"
#include <iostream>
using namespace regrip_film_sphere;
int main(){try{
 Assembly m(5);auto mass=m.masses();std::vector<Point>q0(m.size()),v0(m.size()),J(m.size());auto tip=m.id(0,4,2);J[tip][2]=1;v0[tip][2]=-1;double dt=.005,damping=2,beta=CoupledBDFHistory::beta;
 CoupledContactStep first(m,mass,dt,damping,0,q0,v0,{{J,0,0,0,{tip}}},true,true);SphereStep begin(first,{100,12,-8},8,true);begin.sqpMerit=true;auto current=begin.solve(v0);
 auto qstar=CoupledBDFHistory::extrapolate(current.displacement,q0),vstar=CoupledBDFHistory::extrapolate(current.velocity,v0);
 CoupledContactStep second(m,mass,beta*dt,damping,0,qstar,vstar,{{J,0,beta*current.lambda(0),0,{tip}}},true,true);SphereStep sphere(second,{100,12,-8},8,true);sphere.sqpMerit=true;auto result=sphere.solve(current.velocity);std::vector<Point>normals;auto impulses=sphere.nodal(result.displacement,result.lambda/beta,normals);
 std::vector<Point>gradient(m.size()),residual(m.size());m.elements(result.displacement,0,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)gradient[e.ids[a/3]][a%3]+=e.energy.g[a];});double kinematic=0;
 for(unsigned i=0;i<m.size();++i)for(unsigned d=0;d<3;++d){double dq=(3*result.displacement[i][d]-4*current.displacement[i][d]+q0[i][d])/(2*dt);kinematic=std::max(kinematic,std::abs(dq-result.velocity[i][d]));residual[i][d]=mass[i]*((3*result.velocity[i][d]-4*current.velocity[i][d]+v0[i][d])/2+dt*damping*result.velocity[i][d])+dt*gradient[i][d]-impulses[i][d];}
 Eigen::VectorXd root=Eigen::VectorXd::Zero(second.mechanics.freeSize);for(unsigned a=0;a<3*m.size();++a)if(second.mechanics.index[a]>=0)root(second.mechanics.index[a])+=second.mechanics.weight[a]*residual[a/3][a%3];if(root.norm()>1e-12||kinematic>1e-10||result.gap>1e-10)throw std::runtime_error("BDF2 physical impulse/kinematic mapping");
 std::cout<<"PASS independent sphere BDF2 mapping:physical impulse residual "<<root.norm()<<",kinematic "<<kinematic<<";NOT time convergence\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
