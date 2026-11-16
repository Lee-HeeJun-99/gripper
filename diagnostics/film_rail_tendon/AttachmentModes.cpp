#include "../../models/film_rail_tendon/Kernel.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cstdint>
using namespace regrip_film_rail;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("frozen actual state/error binary");std::ifstream in(argv[1],std::ios::binary);std::uint64_t n;in.read(reinterpret_cast<char*>(&n),8);if(n!=231)throw std::invalid_argument("bounded nx21 diagnostic");Assembly model(n/11);std::vector<Point>u(n),error(n);for(auto*array:{&u,&error})for(auto&p:*array)in.read(reinterpret_cast<char*>(p.data()),24);if(!in)throw std::runtime_error("truncated input");
 unsigned nd=3*n;Eigen::MatrixXd J=Eigen::MatrixXd::Identity(nd,nd),H=Eigen::MatrixXd::Zero(nd,nd),B=H,M=H;auto masses=model.masses();for(unsigned i=0;i<nd;++i)M(i,i)=masses[i/3];
 for(const auto&p:model.parts)for(unsigned j=0;j<p.ny;++j){unsigned i=p.offset+p.ny+j;J(3*i+2,3*i+2)=0;J(3*i+2,3*(i+p.ny)+2)=.25;}
 model.elements(u,0,[&](const Element&e){if(e.kind!=0&&e.kind!=1)return;for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b){unsigned i=3*e.ids[a/3]+a%3,j=3*e.ids[b/3]+b%3;H(i,j)+=e.energy.h[N*a+b];if(e.kind==1)B(i,j)+=e.energy.h[N*a+b];}});
 H=J.transpose()*H*J;B=J.transpose()*B*J;M=J.transpose()*M*J;
 std::vector<unsigned>free;for(unsigned i=0;i<nd;++i){bool fixed=false;unsigned node=i/3;for(const auto&p:model.parts)if((node>=p.offset&&node<p.offset+p.ny)||(node>=p.offset+p.ny&&node<p.offset+2*p.ny&&i%3==2))fixed=true;if(!fixed)free.push_back(i);}
 unsigned nf=free.size();Eigen::MatrixXd h(nf,nf),b(nf,nf),m(nf,nf);Eigen::VectorXd e(nf);for(unsigned i=0;i<nf;++i){e[i]=error[free[i]/3][free[i]%3];for(unsigned j=0;j<nf;++j){h(i,j)=H(free[i],free[j]);b(i,j)=B(free[i],free[j]);m(i,j)=M(free[i],free[j]);}}
 Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd>solve(h,m);if(solve.info()!=Eigen::Success)throw std::runtime_error("generalized eigensolve");auto amplitude=solve.eigenvectors().transpose()*m*e;
 std::cout<<std::setprecision(17)<<"mode,eigenvalue,omega_rad_s,error_quadratic_energy,attachment_fraction\n";
 for(unsigned i=0;i<nf;++i){double lambda=solve.eigenvalues()[i],bond=solve.eigenvectors().col(i).dot(b*solve.eigenvectors().col(i));std::cout<<i<<','<<lambda<<','<<(lambda>0?std::sqrt(lambda):0)<<','<<.5*lambda*amplitude[i]*amplitude[i]<<','<<(lambda!=0?bond/lambda:0)<<'\n';}return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
