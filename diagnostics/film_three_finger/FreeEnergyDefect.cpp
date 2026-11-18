#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
long double dot(const Eigen::VectorXd&a,const Eigen::VectorXd&b){long double value=0;for(int i=0;i<a.size();++i)value+=static_cast<long double>(a(i))*b(i);return value;}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("mass,actual steps,output required");SharedFilmSystem s(Layout(),{0,0,-.001},true,true);unsigned n=s.initial.size();std::ifstream mass(argv[1]);unsigned size;mass>>size;Eigen::VectorXd D(n);for(double&x:D)mass>>x;if(!mass||size!=n||D.minCoeff()<=0)throw std::runtime_error("positive actual projected diagonal mass required");std::ifstream in(argv[2]);unsigned count;in>>count;if(!in||count<1||count>32)throw std::runtime_error("bounded actual8/16/32 step witness");std::array<std::vector<std::pair<double,double>>,2>quadrature;
 for(unsigned k=0;k<2;++k){unsigned size;in>>size;if(size!=(k?8:4))throw std::runtime_error("independent4/8 point path quadrature required");for(unsigned j=0;j<size;++j){double x,w;in>>x>>w;if(x<=0||x>=1||w<=0)throw std::runtime_error("invalid path quadrature");quadrature[k].emplace_back(x,w);}}
 std::ofstream out(argv[3]);out<<std::setprecision(20)<<"step,h_s,energy_defect_Nmm,potential_chord_defect_Nmm,position_power_defect_Nmm,momentum_energy_defect_Nmm,kinetic_roundoff_Nmm,closure_defect_Nmm,line4_potential_defect_Nmm,line8_potential_defect_Nmm,momentum_norm_Ns\n";
 for(unsigned k=0;k<count;++k){double h;long double U0,U1;in>>h>>U0>>U1;Eigen::VectorXd q0(n),v0(n),q1(n),v1(n);for(auto*p:{&q0,&v0,&q1,&v1})for(double&x:*p)in>>x;if(!in||h<=0||h>.0002)throw std::runtime_error("actual finite step payload");Eigen::VectorXd vm=(v0+v1)/2,dv=v1-v0,dq=q1-q0,qm=q0+h/2*vm;auto evaluated=s.force(qm,0);Eigen::VectorXd ext=Eigen::VectorXd::Zero(n);ext(n-4)=-.001;Eigen::VectorXd internal=evaluated.value-ext,Mdv=D.cwiseProduct(dv),damping=2*D.cwiseProduct(vm),residual=Mdv-h*(evaluated.value-damping),position=h*vm-dq;
  long double deltaK=0;for(unsigned i=0;i<n;++i)deltaK+=.5L*D(i)*(static_cast<long double>(v1(i))-v0(i))*(static_cast<long double>(v1(i))+v0(i));
  long double energy=U1-U0+deltaK-h*dot(ext,vm)+h*dot(damping,vm),chord=U1-U0+dot(dq,internal),positionPower=dot(position,internal),momentum=dot(vm,residual),kinetic=deltaK-dot(vm,Mdv);std::array<long double,2>line{U1-U0,U1-U0};
  for(unsigned j=0;j<2;++j)for(auto [alpha,weight]:quadrature[j]){Eigen::VectorXd x=q0+alpha*dq;auto force=s.force(x,0);Eigen::VectorXd f=force.value-ext;line[j]+=static_cast<long double>(weight)*dot(dq,f);}
  out<<k<<','<<h<<','<<energy<<','<<chord<<','<<positionPower<<','<<momentum<<','<<kinetic<<','<<energy-chord-positionPower-momentum-kinetic<<','<<line[0]<<','<<line[1]<<','<<residual.norm()<<'\n';out.flush();
 }std::string extra;if(in>>extra)throw std::runtime_error("unrecognized state payload");std::cout<<"COMPLETED independent force/potential/momentum decomposition on actual FREE states;NOT energy Gate waiver/heat\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
